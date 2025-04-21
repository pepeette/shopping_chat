import os
import json
import streamlit as st
import pandas as pd
from dotenv import load_dotenv
from utils.data_loader import load_product_data
from utils.product_matcher import match_products, format_comparison_table
from utils.mock_claude import get_mock_response

# Load environment variables
load_dotenv()

# Set page configuration
st.set_page_config(
    page_title="Water Filter Assistant",
    page_icon="💧",
    layout="wide"
)

# Load product data
products_df = load_product_data()

# Title and description
st.title("💧 Water Filter Shopping Assistant")
st.markdown("""
This assistant will help you find the perfect water filter for your needs.
Chat with our AI to discuss your requirements, and we'll recommend the best products available in the UK.
""")

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []
    st.session_state.user_requirements = {}
    st.session_state.recommendations = None
    st.session_state.context = {
        "refinement_stage": False,
        "previous_requirements": None
    }

# Function to extract requirements from response
def extract_requirements(content):
    try:
        # Look for JSON block in the response
        if "```json" in content:
            json_start = content.find("```json") + 7
            json_end = content.find("```", json_start)
            json_str = content[json_start:json_end].strip()
            requirements = json.loads(json_str)
            return requirements
        return None
    except Exception as e:
        st.error(f"Error extracting requirements: {e}")
        return None

# Function to generate YouTube installation links (in a real app, this would come from your database)
def get_installation_guide(product_type):
    # Mock function to return YouTube URLs based on product type
    # In a real application, this would be stored in the product database
    guides = {
        "reverse_osmosis": "https://www.youtube.com/watch?v=_w-hpBq_Cbo",
        "under_sink": "https://www.youtube.com/watch?v=NDMXLYEv0jU",
        "countertop": "https://www.youtube.com/watch?v=t90RQMKMv3s",
        "pitcher": "https://www.youtube.com/watch?v=ja0ioX6GSz0",
        "portable": "https://www.youtube.com/watch?v=t-c9WjUxLg8",
        "shower": "https://www.youtube.com/watch?v=OaG2RyDxQlk",
        "whole_house": "https://www.youtube.com/watch?v=5DTMfz-MP-k"
    }
    return guides.get(product_type, "https://www.youtube.com/results?search_query=water+filter+installation")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Initial message if conversation is empty
if not st.session_state.messages:
    with st.chat_message("assistant"):
        welcome_message = "Hello! I'm your water filter shopping assistant. I'll help you find the perfect water filtration solution for your needs. How can I assist you today?"
        st.markdown(welcome_message)
    st.session_state.messages.append({"role": "assistant", "content": welcome_message})

# Refinement section - show only after recommendations have been made
if st.session_state.recommendations is not None:
    st.markdown("---")
    st.markdown("### Refine Your Requirements")
    st.markdown("Would you like to adjust your requirements based on any of these scenarios?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Installation constraints"):
            message = "I'm a tenant and cannot drill holes or make permanent modifications. What options would work for me with these limitations?"
            st.session_state.messages.append({"role": "user", "content": message})
            st.session_state.context["refinement_stage"] = True
            st.experimental_rerun()
    
    with col2:
        if st.button("Water hardness concerns"):
            message = "My water is very hard with lots of limescale. Which of these filters would help with this issue?"
            st.session_state.messages.append({"role": "user", "content": message})
            st.session_state.context["refinement_stage"] = True
            st.experimental_rerun()
    
    with col3:
        if st.button("Health priorities"):
            message = "I'm actually more concerned about potential bacteria and lead in my water. Could you adjust the recommendations?"
            st.session_state.messages.append({"role": "user", "content": message})
            st.session_state.context["refinement_stage"] = True
            st.experimental_rerun()

# Chat input
prompt = st.chat_input("Ask about water filters...")

if prompt:
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Get response
    with st.spinner("Thinking..."):
        # Use mock Claude instead of the API
        mock_response = get_mock_response(prompt)
        
        # Check if requirements are in the response
        requirements = extract_requirements(mock_response)
        if requirements:
            # Store previous requirements if we're refining
            if st.session_state.context["refinement_stage"]:
                st.session_state.context["previous_requirements"] = st.session_state.user_requirements
            
            # Update current requirements
            st.session_state.user_requirements = requirements
            
            # Match products with requirements
            matched_products = match_products(products_df, requirements)
            st.session_state.recommendations = matched_products
            
            # Generate comparison table for top 3 alternatives
            comparison_table = format_comparison_table(matched_products, top_n=3)
            
            # Add product recommendations to response
            mock_response += "\n\n### Recommended Products\n\n"
            mock_response += comparison_table
            
            # Add detailed specs for top recommendation
            if not matched_products.empty:
                top_product = matched_products.iloc[0]
                mock_response += f"\n\n### Top Recommendation: {top_product['name']}\n\n"
                mock_response += f"* Price: £{top_product['price_gbp']}\n"
                mock_response += f"* Type: {top_product['type'].replace('_', ' ').title()}\n"
                mock_response += f"* Installation: {top_product['installation'].replace('_', ' ').title()}\n"
                mock_response += f"* Capacity: {top_product['capacity_liters']} liters\n"
                mock_response += f"* Filtration: {top_product['filtration_type'].replace('_', ' ').title()}\n"
                mock_response += f"* Remineralization: {'Yes' if top_product['remineralization'] == 'yes' else 'No'}\n"
                mock_response += f"* Removes Chlorine: {'Yes' if top_product['removes_chlorine'] == 'yes' else 'Partially' if top_product['removes_chlorine'] == 'partial' else 'No'}\n"
                mock_response += f"* Removes Lead: {'Yes' if top_product['removes_lead'] == 'yes' else 'Partially' if top_product['removes_lead'] == 'partial' else 'No'}\n"
                mock_response += f"* Removes Fluoride: {'Yes' if top_product['removes_fluoride'] == 'yes' else 'Partially' if top_product['removes_fluoride'] == 'partial' else 'No'}\n"
                mock_response += f"* Removes Bacteria: {'Yes' if top_product['removes_bacteria'] == 'yes' else 'Partially' if top_product['removes_bacteria'] == 'partial' else 'No'}\n"
                mock_response += f"* Filter Lifespan: {top_product['filter_lifespan_months']} months\n"
                mock_response += f"* Annual Maintenance Cost: £{top_product['maintenance_cost_yearly_gbp']}\n"
                mock_response += f"* Warranty: {top_product['warranty_years']} years\n"
                
                # Add installation guide
                installation_url = get_installation_guide(top_product['type'])
                mock_response += f"\n\n### Installation Guide\n\n"
                mock_response += f"[Watch Installation Tutorial on YouTube]({installation_url})\n"
                
                # Add refinement prompt
                mock_response += f"\n\n### Need To Refine Further?\n\n"
                mock_response += "You can ask me more specific questions about these products or tell me if you have additional requirements or constraints."
    
    # Display response
    st.session_state.messages.append({"role": "assistant", "content": mock_response})
    with st.chat_message("assistant"):
        st.markdown(mock_response)

# Sidebar with current requirements
with st.sidebar:
    st.header("Current Requirements")
    if st.session_state.user_requirements:
        req = st.session_state.user_requirements
        st.write(f"**Installation:** {', '.join([i.replace('_', ' ').title() for i in req.get('installation', ['Not specified'])])}")
        st.write(f"**Max Price:** £{req.get('max_price', 'Not specified')}")
        st.write(f"**Remove Chlorine:** {req.get('remove_chlorine', 'Not specified')}")
        st.write(f"**Remove Lead:** {req.get('remove_lead', 'Not specified')}")
        st.write(f"**Remove Fluoride:** {req.get('remove_fluoride', 'Not specified')}")
        st.write(f"**Remove Bacteria:** {req.get('remove_bacteria', 'Not specified')}")
        st.write(f"**Eco-friendly:** {req.get('eco_friendly', 'Not specified')}")
        st.write(f"**Remineralization:** {req.get('remineralization', 'Not specified')}")
        st.write(f"**Priorities:** {', '.join([p.title() for p in req.get('priorities', ['Not specified'])])}")
        
        # Show previous requirements if we're in refinement stage
        if st.session_state.context["previous_requirements"]:
            st.markdown("---")
            st.header("Previous Requirements")
            prev_req = st.session_state.context["previous_requirements"]
            st.write(f"**Installation:** {', '.join([i.replace('_', ' ').title() for i in prev_req.get('installation', ['Not specified'])])}")
            st.write(f"**Max Price:** £{prev_req.get('max_price', 'Not specified')}")
            # Add other fields as needed
        
        if st.button("Reset Conversation"):
            st.session_state.messages = []
            st.session_state.user_requirements = {}
            st.session_state.recommendations = None
            st.session_state.context = {
                "refinement_stage": False,
                "previous_requirements": None
            }
            st.experimental_rerun()
    else:
        st.write("No requirements gathered yet. Chat with the assistant to get started!")
    
    # Add information about the project
    st.markdown("---")
    st.header("About This Project")
    st.markdown("""
    This is an open-source water filter shopping assistant that uses AI to help you find the right water filtration solution.
    
    **Features:**
    - Personalized recommendations based on your needs
    - Detailed product specifications
    - Installation guides
    - UK price and availability information
    """)

    # Add advanced options
    st.markdown("---")
    st.header("Advanced Options")
    compare_count = st.slider("Number of alternatives to compare", min_value=2, max_value=10, value=3)
    
    # In a real app, these would trigger actual Amazon product searches
    if st.checkbox("Search Amazon directly", value=False):
        st.warning("Amazon direct search requires API integration (currently simulated)")
