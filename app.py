import streamlit as st
from printer import generate_price_tag # Imports your engine!

# 1. Page Setup
st.set_page_config(page_title="Price Tag Generator", layout="centered")
st.title("🏷️ Retail Price Tag Generator")
st.write("Enter the product details below to generate a print-ready tag.")

# 2. The Input Form
with st.form("tag_form"):
    product_name = st.text_input("Product Name", "Organic Gala Apples")
    item_id = st.number_input("Item ID", value=12345, step=1)
    
    # Put prices side-by-side using columns
    col1, col2 = st.columns(2)
    with col1:
        old_price = st.number_input("Old Price ($)", value=5.99, step=0.50)
    with col2:
        new_price = st.number_input("New Price ($)", value=2.99, step=0.50)
        
    discount_type = st.selectbox("Template Type", ["General discount", "Member Card"])
    
    # The giant submit button
    submit_button = st.form_submit_button("Generate Tag")

# 3. What happens when they click the button?
if submit_button:
    with st.spinner("Generating high-res tag..."):
        # Run your Pillow engine!
        output_file = generate_price_tag(product_name, item_id, old_price, new_price, discount_type)
        
        # Display the result on the web page
        if output_file:
            st.success("Tag generated successfully!")
            st.image(output_file, caption=f"File saved as: {output_file}")