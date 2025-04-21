# utils/alibaba_scraper.py
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import re
import time

def alibaba_search(requirements, max_results=5):
    """
    Searches Alibaba for water filters based on the given requirements,
    filtering for delivery to the UK.
    """
    search_term = "water filter"  # Base search term
    if "installation" in requirements and requirements["installation"]:
        search_term += " " + " ".join(requirements["installation"]).replace("_", " ")

    # Construct Alibaba search URL
    base_url = "https://www.alibaba.com/trade/search"
    url = f"{base_url}?fsb=y&IndexArea=product_en&keywords={search_term.replace(' ', '+')}"

    # Selenium setup (ensure ChromeDriver is installed and in PATH)
    options = Options()
    options.add_argument("--headless")  # Run in headless mode (no browser window)
    driver = webdriver.Chrome(options=options) # or Firefox()

    driver.get(url)

    # Wait for search results to load (adjust timeout as needed)
    try:
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.J-search-result-data'))
        )
    except:
        print("Search results didn't load in time.")

    # Extract product data using BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    product_divs = soup.find_all('div', class_='J-search-result-data')

    products = []
    for div in product_divs[:max_results]:
        try:
            # Check for delivery to GB
            delivery_to_gb = div.find('div', class_='tnh-country-flag')
            if delivery_to_gb and delivery_to_gb.find('img', src=re.compile(r'gb\.png')): #delivery_to_gb:
                product_name = div.find('p', class_='title').text.strip()
                product_url = "https:" + div.find('a', class_='product-title')['href']
                # Updated Price Extraction based on Inspection
                price_element = div.find('span', class_='price-num')
                if price_element:
                    price_text = price_element.text.strip()
                    # Clean the price text (remove commas, currency symbols)
                    price_text = re.sub(r'[^\d\.]', '', price_text)
                    try:
                        min_price = float(price_text)
                    except ValueError:
                        min_price = None  # Handle cases where price is unparseable
                else:
                    min_price = None

                if min_price is not None: #Only add product if we found a price

                    products.append({
                        'name': product_name,
                        'url': product_url,
                        'price_usd': min_price,  #Store in USD first
                        'installation': requirements.get('installation', ['unknown']),
                        'remove_chlorine': requirements.get('remove_chlorine', False),
                        'remove_lead': requirements.get('remove_lead', False),
                        'remove_fluoride': requirements.get('remove_fluoride', False),
                        'remove_bacteria': requirements.get('remove_bacteria', False),
                        'eco_friendly': requirements.get('eco_friendly', False),
                        'remineralization': requirements.get('remineralization', False)
                    })
                else:
                    print(f"Could not extract price for product: {product_name}")
            else:
                print(f"Skipping product, not delivered to GB")

        except Exception as e:
            print(f"Error parsing product: {e}")

    driver.quit()

    alibaba_df = pd.DataFrame(products)

     # Convert USD to GBP (using a simplified conversion - use an API for real-time rates)
    usd_to_gbp = 0.80  # Approximate conversion rate
    if not alibaba_df.empty: #Added check for empty dataframe before price conversion
        alibaba_df['price_gbp'] = alibaba_df['price_usd'] * usd_to_gbp

    # Filter by max_price if available
    if 'max_price' in requirements and not alibaba_df.empty:
        alibaba_df = alibaba_df[alibaba_df['price_gbp'] <= requirements['max_price']]

    return alibaba_df
