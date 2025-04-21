import pandas as pd
import os

def load_product_data():
    """
    Load product data from CSV file
    """
    script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(script_dir, 'data', 'products.csv')
    
    try:
        products_df = pd.read_csv(data_path)
        return products_df
    except Exception as e:
        print(f"Error loading product data: {e}")
        return pd.DataFrame()
