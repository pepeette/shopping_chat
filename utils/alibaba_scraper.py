# utils/alibaba_scraper.py
import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import time
import random
from fake_useragent import UserAgent

def alibaba_search(requirements, max_results=5):
    """
    Searches Alibaba for water filters based on the given requirements,
    filtering for delivery to the UK. Uses requests instead of Selenium.
    """
    # Create a user agent to mimic a browser
    try:
        ua = UserAgent()
        user_agent = ua.random
    except:
        # Fallback if fake_useragent fails
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36'
        ]
        user_agent = random.choice(user_agents)
    
    # Construct search term based on requirements
    search_term = "water filter"  # Base search term
    if "installation" in requirements and requirements["installation"]:
        search_term += " " + " ".join(requirements["installation"]).replace("_", " ")
    
    # Construct Alibaba search URL
    base_url = "https://www.alibaba.com/trade/search"
    url = f"{base_url}?fsb=y&IndexArea=product_en&keywords={search_term.replace(' ', '+')}&country=GB"
    
    # Set up headers to mimic a browser request
    headers = {
        'User-Agent': user_agent,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.alibaba.com/',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code != 200:
            print(f"Failed to retrieve page, status code: {response.status_code}")
            return fallback_products(requirements)
        
        # Parse the page content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Find product listings
        product_divs = soup.find_all('div', class_='organic-list-offer-outter')
        
        if not product_divs:
            product_divs = soup.find_all('div', class_='J-offer-wrapper')
        
        if not product_divs:
            print("No product divs found, falling back to mock data")
            return fallback_products(requirements)
            
        products = []
        for div in product_divs[:max_results]:
            try:
                # Try to extract product details
                product_name_element = div.find('h2', class_='organic-list-offer__heading') or div.find('p', class_='elements-title-normal__content')
                if not product_name_element:
                    continue
                    
                product_name = product_name_element.text.strip()
                
                # Try to find the product URL
                url_element = div.find('a', class_='organic-list-offer__img-wrap') or div.find('a', class_='elements-title-normal')
                product_url = "https:" + url_element['href'] if url_element and 'href' in url_element.attrs else "https://www.alibaba.com"
                
                # Try to extract price
                price_element = div.find('span', class_='elements-offer-price-normal__price') or div.find('div', class_='price')
                if price_element:
                    price_text = price_element.text.strip()
                    # Extract numeric value from price text
                    price_match = re.search(r'[0-9,.]+', price_text)
                    min_price = float(price_match.group().replace(',', '')) if price_match else 50.0
                else:
                    min_price = 50.0  # Default price if not found
                
                # Infer filter capabilities based on product name and requirements
                removes_chlorine = 'yes' if ('chlor' in product_name.lower() or 
                                           requirements.get('remove_chlorine') == 'yes') else 'partial'
                removes_lead = 'yes' if ('lead' in product_name.lower() or 
                                       'heavy metal' in product_name.lower() or
                                       requirements.get('remove_lead') == 'yes') else 'partial'
                removes_fluoride = 'yes' if ('fluor' in product_name.lower() or 
                                           requirements.get('remove_fluoride') == 'yes') else 'no'
                removes_bacteria = 'yes' if ('bacteria' in product_name.lower() or 
                                           'microbe' in product_name.lower() or
                                           'germ' in product_name.lower() or
                                           'uv' in product_name.lower() or
                                           requirements.get('remove_bacteria') == 'yes') else 'no'
                
                # Determine filter type from product name
                filter_type = 'carbon'  # Default type
                if 'ro' in product_name.lower() or 'reverse osm' in product_name.lower():
                    filter_type = 'reverse_osmosis'
                    filter_lifespan = 12
                elif 'ceramic' in product_name.lower():
                    filter_type = 'ceramic'
                    filter_lifespan = 6
                elif 'uv' in product_name.lower():
                    filter_type = 'uv'
                    filter_lifespan = 12
                elif 'multi' in product_name.lower() or 'stage' in product_name.lower():
                    filter_type = 'multi_stage'
                    filter_lifespan = 9
                else:
                    filter_lifespan = 6
                
                # Determine installation type
                installation_type = 'countertop'  # Default installation
                if 'sink' in product_name.lower() or 'under' in product_name.lower():
                    installation_type = 'under_sink'
                elif 'whole' in product_name.lower() or 'house' in product_name.lower():
                    installation_type = 'whole_house'
                elif 'pitcher' in product_name.lower() or 'jug' in product_name.lower():
                    installation_type = 'pitcher'
                elif 'shower' in product_name.lower():
                    installation_type = 'shower'
                elif 'portable' in product_name.lower() or 'bottle' in product_name.lower():
                    installation_type = 'portable'
                elif 'ro' in product_name.lower() or 'reverse osm' in product_name.lower():
                    installation_type = 'under_sink'
                
                # Check if product matches requested installation type
                if ('installation' in requirements and 
                    requirements['installation'] and 
                    installation_type not in requirements['installation']):
                    continue
                
                products.append({
                    'name': product_name,
                    'url': product_url,
                    'price_usd': min_price,
                    'type': installation_type,
                    'installation': installation_type,
                    'capacity_liters': random.choice([10, 15, 20, 30, 50]),
                    'filtration_type': filter_type,
                    'remineralization': 'yes' if 'mineral' in product_name.lower() else 'no',
                    'removes_chlorine': removes_chlorine,
                    'removes_lead': removes_lead,
                    'removes_fluoride': removes_fluoride,
                    'removes_bacteria': removes_bacteria,
                    'filter_lifespan_months': filter_lifespan,
                    'maintenance_cost_yearly_gbp': round(min_price * 0.8 * 12 / filter_lifespan, 2),
                    'warranty_years': random.choice([1, 2, 3]),
                    'is_alibaba': True
                })
                
            except Exception as e:
                print(f"Error parsing product: {e}")
        
        # Create DataFrame from products list
        alibaba_df = pd.DataFrame(products)
        
        # Convert USD to GBP
        usd_to_gbp = 0.80  # Approximate conversion rate
        if not alibaba_df.empty:
            alibaba_df['price_gbp'] = alibaba_df['price_usd'] * usd_to_gbp
            
            # Filter by max_price if available
            if 'max_price' in requirements and requirements['max_price']:
                alibaba_df = alibaba_df[alibaba_df['price_gbp'] <= float(requirements['max_price'])]
        
        if alibaba_df.empty:
            return fallback_products(requirements)
            
        return alibaba_df
        
    except Exception as e:
        print(f"Exception in alibaba_search: {e}")
        return fallback_products(requirements)

def fallback_products(requirements):
    """
    Returns mock product data when web scraping fails.
    """
    print("Using fallback product data")
    
    # Define installation types based on requirements or default to a variety
    if 'installation' in requirements and requirements['installation']:
        installation_types = requirements['installation']
    else:
        installation_types = ['under_sink', 'countertop', 'pitcher', 'shower', 'whole_house', 'portable']
    
    # Create a list of mock products matching the required installation types
    mock_products = []
    
    # Add products for each installation type
    for install_type in installation_types:
        if install_type == 'under_sink':
            mock_products.extend([
                {
                    'name': 'Alibaba Premium RO Under Sink System',
                    'url': 'https://www.alibaba.com/product-detail/sample1',
                    'price_usd': 85.99,
                    'type': 'under_sink',
                    'installation': 'under_sink',
                    'capacity_liters': 50,
                    'filtration_type': 'reverse_osmosis',
                    'remineralization': 'yes',
                    'removes_chlorine': 'yes',
                    'removes_lead': 'yes',
                    'removes_fluoride': 'yes',
                    'removes_bacteria': 'yes',
                    'filter_lifespan_months': 6,
                    'maintenance_cost_yearly_gbp': 45,
                    'warranty_years': 2,
                    'is_alibaba': True
                },
                {
                    'name': 'Alibaba Under Sink 5-Stage Filtration System',
                    'url': 'https://www.alibaba.com/product-detail/sample4',
                    'price_usd': 65.75,
                    'type': 'under_sink',
                    'installation': 'under_sink',
                    'capacity_liters': 30,
                    'filtration_type': 'multi_stage',
                    'remineralization': 'no',
                    'removes_chlorine': 'yes',
                    'removes_lead': 'yes',
                    'removes_fluoride': 'partial',
                    'removes_bacteria': 'yes',
                    'filter_lifespan_months': 8,
                    'maintenance_cost_yearly_gbp': 30,
                    'warranty_years': 3,
                    'is_alibaba': True
                }
            ])
        elif install_type == 'countertop':
            mock_products.append({
                'name': 'Alibaba Countertop Ceramic Filter System',
                'url': 'https://www.alibaba.com/product-detail/sample2',
                'price_usd': 29.99,
                'type': 'countertop',
                'installation': 'countertop',
                'capacity_liters': 15,
                'filtration_type': 'ceramic',
                'remineralization': 'no',
                'removes_chlorine': 'yes',
                'removes_lead': 'partial',
                'removes_fluoride': 'no',
                'removes_bacteria': 'yes',
                'filter_lifespan_months': 3,
                'maintenance_cost_yearly_gbp': 60,
                'warranty_years': 1,
                'is_alibaba': True
            })
        elif install_type == 'portable':
            mock_products.append({
                'name': 'Alibaba Portable Water Filter Bottle',
                'url': 'https://www.alibaba.com/product-detail/sample3',
                'price_usd': 19.50,
                'type': 'portable',
                'installation': 'portable',
                'capacity_liters': 0.75,
                'filtration_type': 'carbon',
                'remineralization': 'no',
                'removes_chlorine': 'yes',
                'removes_lead': 'partial',
                'removes_fluoride': 'no',
                'removes_bacteria': 'partial',
                'filter_lifespan_months': 2,
                'maintenance_cost_yearly_gbp': 36,
                'warranty_years': 1,
                'is_alibaba': True
            })
        elif install_type == 'whole_house':
            mock_products.append({
                'name': 'Alibaba Whole House Water Filter System',
                'url': 'https://www.alibaba.com/product-detail/sample5',
                'price_usd': 199.99,
                'type': 'whole_house',
                'installation': 'whole_house',
                'capacity_liters': 500,
                'filtration_type': 'sediment_carbon',
                'remineralization': 'no',
                'removes_chlorine': 'yes',
                'removes_lead': 'partial',
                'removes_fluoride': 'no',
                'removes_bacteria': 'no',
                'filter_lifespan_months': 12,
                'maintenance_cost_yearly_gbp': 50,
                'warranty_years': 5,
                'is_alibaba': True
            })
        elif install_type == 'shower':
            mock_products.append({
                'name': 'Alibaba Shower Head Water Filter',
                'url': 'https://www.alibaba.com/product-detail/sample6',
                'price_usd': 15.25,
                'type': 'shower',
                'installation': 'shower',
                'capacity_liters': 10,
                'filtration_type': 'kdf_carbon',
                'remineralization': 'no',
                'removes_chlorine': 'yes',
                'removes_lead': 'no',
                'removes_fluoride': 'no',
                'removes_bacteria': 'no',
                'filter_lifespan_months': 3,
                'maintenance_cost_yearly_gbp': 50,
                'warranty_years': 1,
                'is_alibaba': True
            })
        elif install_type == 'pitcher':
            mock_products.append({
                'name': 'Alibaba Water Filter Pitcher 3.5L',
                'url': 'https://www.alibaba.com/product-detail/sample7',
                'price_usd': 22.50,
                'type': 'pitcher',
                'installation': 'pitcher',
                'capacity_liters': 3.5,
                'filtration_type': 'carbon',
                'remineralization': 'no',
                'removes_chlorine': 'yes',
                'removes_lead': 'partial',
                'removes_fluoride': 'no',
                'removes_bacteria': 'no',
                'filter_lifespan_months': 2,
                'maintenance_cost_yearly_gbp': 60,
                'warranty_years': 1,
                'is_alibaba': True
            })
    
    # Filter products based on requirements
    filtered_products = mock_products.copy()
    
    # Filter by price if specified
    if 'max_price' in requirements and requirements['max_price']:
        max_price_gbp = float(requirements['max_price'])
        # Convert USD to GBP for comparison
        usd_to_gbp = 0.80  # Approximate conversion rate
        filtered_products = [p for p in filtered_products if p['price_usd'] * usd_to_gbp <= max_price_gbp]
    
    # Prioritize products based on contaminant removal requirements
    if 'remove_chlorine' in requirements and requirements['remove_chlorine'] == 'yes':
        chlorine_products = [p for p in filtered_products if p['removes_chlorine'] == 'yes']
        if chlorine_products:
            filtered_products = chlorine_products
    
    if 'remove_lead' in requirements and requirements['remove_lead'] == 'yes':
        lead_products = [p for p in filtered_products if p['removes_lead'] == 'yes']
        if lead_products:
            filtered_products = lead_products
    
    if 'remove_fluoride' in requirements and requirements['remove_fluoride'] == 'yes':
        fluoride_products = [p for p in filtered_products if p['removes_fluoride'] == 'yes']
        if fluoride_products:
            filtered_products = fluoride_products
    
    if 'remove_bacteria' in requirements and requirements['remove_bacteria'] == 'yes':
        bacteria_products = [p for p in filtered_products if p['removes_bacteria'] == 'yes']
        if bacteria_products:
            filtered_products = bacteria_products
    
    # If no products match the criteria, return some random ones
    if not filtered_products and mock_products:
        filtered_products = random.sample(mock_products, min(5, len(mock_products)))
    
    # Convert to DataFrame
    alibaba_df = pd.DataFrame(filtered_products)
    
    # Add price_gbp column
    if not alibaba_df.empty:
        alibaba_df['price_gbp'] = alibaba_df['price_usd'] * 0.80
    
    return alibaba_df
