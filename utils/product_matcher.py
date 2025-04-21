import pandas as pd

def match_products(products_df, user_requirements):
    """
    Match products to user requirements
    
    Parameters:
    products_df (DataFrame): DataFrame with product data
    user_requirements (dict): Dictionary with user requirements
    
    Returns:
    DataFrame: Filtered and sorted products
    """
    # Start with all products
    filtered_df = products_df.copy()
    
    # Filter by installation type if specified
    if 'installation' in user_requirements and user_requirements['installation']:
        filtered_df = filtered_df[filtered_df['installation'].isin(user_requirements['installation'])]
    
    # Filter by price range if specified
    if 'max_price' in user_requirements and user_requirements['max_price']:
        filtered_df = filtered_df[filtered_df['price_gbp'] <= user_requirements['max_price']]
    
    # Filter by specific contaminant removal requirements
    if 'remove_chlorine' in user_requirements and user_requirements['remove_chlorine']:
        filtered_df = filtered_df[filtered_df['removes_chlorine'].isin(['yes', 'partial'])]
    
    if 'remove_lead' in user_requirements and user_requirements['remove_lead']:
        filtered_df = filtered_df[filtered_df['removes_lead'].isin(['yes', 'partial'])]
    
    if 'remove_fluoride' in user_requirements and user_requirements['remove_fluoride']:
        filtered_df = filtered_df[filtered_df['removes_fluoride'].isin(['yes', 'partial'])]
    
    if 'remove_bacteria' in user_requirements and user_requirements['remove_bacteria']:
        filtered_df = filtered_df[filtered_df['removes_bacteria'].isin(['yes', 'partial'])]
    
    # Filter by eco-friendliness if specified
    if 'eco_friendly' in user_requirements and user_requirements['eco_friendly']:
        filtered_df = filtered_df[filtered_df['ecofriendly_rating'] >= 4]
    
    # Filter by remineralization if specified
    if 'remineralization' in user_requirements and user_requirements['remineralization']:
        filtered_df = filtered_df[filtered_df['remineralization'] == 'yes']
    
    # Calculate a match score for sorting
    filtered_df['match_score'] = 0
    
    # Increase score based on matched priorities
    if 'priorities' in user_requirements:
        priorities = user_requirements['priorities']
        
        if 'health' in priorities:
            # Health priority boosts products that remove more contaminants
            filtered_df['match_score'] += (
                (filtered_df['removes_chlorine'] == 'yes').astype(int) +
                (filtered_df['removes_lead'] == 'yes').astype(int) * 2 +
                (filtered_df['removes_fluoride'] == 'yes').astype(int) * 2 +
                (filtered_df['removes_bacteria'] == 'yes').astype(int) * 2 +
                (filtered_df['remineralization'] == 'yes').astype(int)
            )
        
        if 'eco' in priorities:
            # Eco priority boosts products with higher eco rating
            filtered_df['match_score'] += filtered_df['ecofriendly_rating']
        
        if 'price' in priorities:
            # Price priority gives higher score to lower-priced options
            filtered_df['match_score'] += (500 - filtered_df['price_gbp']) / 100
            
        if 'maintenance' in priorities:
            # Low maintenance priority gives higher score to products with longer filter life
            filtered_df['match_score'] += filtered_df['filter_lifespan_months'] / 2
            # And lower annual maintenance costs
            filtered_df['match_score'] += (200 - filtered_df['maintenance_cost_yearly_gbp']) / 40
    
    # Sort by match score (descending)
    filtered_df = filtered_df.sort_values('match_score', ascending=False)
    
    return filtered_df

def format_comparison_table(matched_products, top_n=3):
    """
    Format top matched products into a comparison table
    
    Parameters:
    matched_products (DataFrame): DataFrame with matched products
    top_n (int): Number of top products to include
    
    Returns:
    str: Markdown formatted comparison table
    """
    top_products = matched_products.head(top_n)
    
    if top_products.empty:
        return "No products found matching your requirements."
    
    # Create enhanced table header with more columns
    header = "| Product | Type | Price (£) | Installation | Filtration | Removes Chlorine | Removes Lead | Removes Bacteria | Filter Life | Maintenance Cost | Eco Rating |\n"
    separator = "|---------|------|-----------|-------------|------------|-----------------|-------------|-----------------|-------------|------------------|------------|\n"
    
    # Create table rows
    rows = ""
    for _, product in top_products.iterrows():
        # Format removal capabilities with emojis for clarity
        chlorine_icon = "✅" if product['removes_chlorine'] == 'yes' else "⚠️" if product['removes_chlorine'] == 'partial' else "❌"
        lead_icon = "✅" if product['removes_lead'] == 'yes' else "⚠️" if product['removes_lead'] == 'partial' else "❌"
        bacteria_icon = "✅" if product['removes_bacteria'] == 'yes' else "⚠️" if product['removes_bacteria'] == 'partial' else "❌"
        
        rows += f"| {product['name']} | {product['type'].replace('_', ' ').title()} | £{product['price_gbp']} | "
        rows += f"{product['installation'].replace('_', ' ').title()} | {product['filtration_type'].replace('_', ' ').title()} | "
        rows += f"{chlorine_icon} | {lead_icon} | {bacteria_icon} | "
        rows += f"{product['filter_lifespan_months']} months | £{product['maintenance_cost_yearly_gbp']}/year | {product['ecofriendly_rating']}/5 |\n"
    
    # Add explanation for icons
    legend = "\n**Legend**: ✅ Yes | ⚠️ Partial | ❌ No\n"
    
    return header + separator + rows + legend

def get_detailed_comparison(product1, product2):
    """
    Generate a detailed comparison between two specific products
    
    Parameters:
    product1 (Series): First product details
    product2 (Series): Second product details
    
    Returns:
    str: Detailed comparison markdown
    """
    comparison = f"## Detailed Comparison: {product1['name']} vs {product2['name']}\n\n"
    
    # Feature comparison
    comparison += "| Feature | " + product1['name'] + " | " + product2['name'] + " |\n"
    comparison += "|---------|" + "-" * len(product1['name']) + "|" + "-" * len(product2['name']) + "|\n"
    
    # Important features to compare
    features = [
        ('Price', f"£{product1['price_gbp']}", f"£{product2['price_gbp']}"),
        ('Type', product1['type'].replace('_', ' ').title(), product2['type'].replace('_', ' ').title()),
        ('Installation', product1['installation'].replace('_', ' ').title(), product2['installation'].replace('_', ' ').title()),
        ('Filtration', product1['filtration_type'].replace('_', ' ').title(), product2['filtration_type'].replace('_', ' ').title()),
        ('Capacity', f"{product1['capacity_liters']} liters", f"{product2['capacity_liters']} liters"),
        ('Removes Chlorine', product1['removes_chlorine'].title(), product2['removes_chlorine'].title()),
        ('Removes Lead', product1['removes_lead'].title(), product2['removes_lead'].title()),
        ('Removes Fluoride', product1['removes_fluoride'].title(), product2['removes_fluoride'].title()),
        ('Removes Bacteria', product1['removes_bacteria'].title(), product2['removes_bacteria'].title()),
        ('Remineralization', 'Yes' if product1['remineralization'] == 'yes' else 'No', 'Yes' if product2['remineralization'] == 'yes' else 'No'),
        ('Filter Lifespan', f"{product1['filter_lifespan_months']} months", f"{product2['filter_lifespan_months']} months"),
        ('Yearly Maintenance', f"£{product1['maintenance_cost_yearly_gbp']}", f"£{product2['maintenance_cost_yearly_gbp']}"),
        ('Eco-friendly Rating', f"{product1['ecofriendly_rating']}/5", f"{product2['ecofriendly_rating']}/5"),
        ('Warranty', f"{product1['warranty_years']} years", f"{product2['warranty_years']} years")
    ]
    
    # Add each feature row
    for feature, val1, val2 in features:
        comparison += f"| {feature} | {val1} | {val2} |\n"
    
    # Add key advantages section
    comparison += "\n### Key Advantages\n\n"
    
    # Product 1 advantages
    comparison += f"**{product1['name']} advantages:**\n"
    advantages = []
    
    if product1['price_gbp'] < product2['price_gbp']:
        advantages.append(f"Lower price (£{product1['price_gbp']} vs £{product2['price_gbp']})")
    
    if product1['filter_lifespan_months'] > product2['filter_lifespan_months']:
        advantages.append(f"Longer filter life ({product1['filter_lifespan_months']} months vs {product2['filter_lifespan_months']} months)")
    
    if product1['maintenance_cost_yearly_gbp'] < product2['maintenance_cost_yearly_gbp']:
        advantages.append(f"Lower maintenance cost (£{product1['maintenance_cost_yearly_gbp']}/year vs £{product2['maintenance_cost_yearly_gbp']}/year)")
    
    if product1['ecofriendly_rating'] > product2['ecofriendly_rating']:
        advantages.append(f"More eco-friendly ({product1['ecofriendly_rating']}/5 vs {product2['ecofriendly_rating']}/5)")
    
    if product1['warranty_years'] > product2['warranty_years']:
        advantages.append(f"Longer warranty ({product1['warranty_years']} years vs {product2['warranty_years']} years)")
        
    if advantages:
        for adv in advantages:
            comparison += f"- {adv}\n"
    else:
        comparison += "- No significant advantages identified\n"
    
    # Product 2 advantages
    comparison += f"\n**{product2['name']} advantages:**\n"
    advantages = []
    
    if product2['price_gbp'] < product1['price_gbp']:
        advantages.append(f"Lower price (£{product2['price_gbp']} vs £{product1['price_gbp']})")
    
    if product2['filter_lifespan_months'] > product1['filter_lifespan_months']:
        advantages.append(f"Longer filter life ({product2['filter_lifespan_months']} months vs {product1['filter_lifespan_months']} months)")
    
    if product2['maintenance_cost_yearly_gbp'] < product1['maintenance_cost_yearly_gbp']:
        advantages.append(f"Lower maintenance cost (£{product2['maintenance_cost_yearly_gbp']}/year vs £{product1['maintenance_cost_yearly_gbp']}/year)")
    
    if product2['ecofriendly_rating'] > product1['ecofriendly_rating']:
        advantages.append(f"More eco-friendly ({product2['ecofriendly_rating']}/5 vs {product1['ecofriendly_rating']}/5)")
    
    if product2['warranty_years'] > product1['warranty_years']:
        advantages.append(f"Longer warranty ({product2['warranty_years']} years vs {product1['warranty_years']} years)")
        
    if advantages:
        for adv in advantages:
            comparison += f"- {adv}\n"
    else:
        comparison += "- No significant advantages identified\n"
    
    return comparison