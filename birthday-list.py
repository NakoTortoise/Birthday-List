import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & DATA
# ==========================================
st.set_page_config(page_title="My Birthday Gift Guide", page_icon="🎂", layout="wide")

# Your Gift Data
my_gifts = [
    {"Gift Item": "Noise Cancelling Headphones", "Price": 3500, "Need": 8, "Want": 9, "Category": "Tech"},
    {"Gift Item": "Mechanical Keyboard", "Price": 1200, "Need": 4, "Want": 10, "Category": "Tech"},
    {"Gift Item": "Screwdriver Set", "Price": 450, "Need": 10, "Want": 3, "Category": "Tools"},
    {"Gift Item": "Minecraft Server (1 Yr)", "Price": 250, "Need": 2, "Want": 8, "Category": "Gaming"},
    {"Gift Item": "Python Course", "Price": 300, "Need": 9, "Want": 7, "Category": "Education"},
    {"Gift Item": "Stellenbosch Hoodie", "Price": 650, "Need": 5, "Want": 7, "Category": "Apparel"},
    {"Gift Item": "Multimeter", "Price": 900, "Need": 9, "Want": 5, "Category": "Tools"},
    {"Gift Item": "Spotify 6-Month Sub", "Price": 360, "Need": 3, "Want": 9, "Category": "Entertainment"},
]

df = pd.DataFrame(my_gifts)

# ==========================================
# 2. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filter by Your Preferences")

# Price Filter
max_val = int(df['Price'].max())
budget = st.sidebar.slider("Your Max Budget (Rands)", 0, max_val + 500, max_val)

# Need & Want Filters
min_need = st.sidebar.slider("Minimum 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Minimum 'Want' Score", 1, 10, 1)

# Apply Filters to DataFrame
filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 3. MAIN UI
# ==========================================
st.title("🎁 My Interactive Birthday Wishlist")
st.write("Use the sidebar to filter gifts by your budget or how much I need/want them!")

if filtered_df.empty:
    st.warning("No gifts match those filters! Try adjusting your budget or scores in the sidebar.")
else:
    # Creating the Bubble Chart
    # X = Want, Y = Need, Size = Price
    fig = px.scatter(filtered_df, 
                     x="Want", 
                     y="Need", 
                     size="Price", 
                     color="Category",
                     hover_name="Gift Item",
                     text="Gift Item",
                     size_max=60, # Adjusts how big the bubbles get
                     range_x=[0, 11], # Keep scale consistent
                     range_y=[0, 11],
                     labels={"Want": "How much I want it (1-10)", "Need": "How much I need it (1-10)"},
                     title="Gift Priority Matrix")

    # Clean up the look
    fig.update_traces(textposition='top center')
    fig.update_layout(height=600, template="plotly_white")

    st.plotly_chart(fig, use_container_width=True)

    # Display the filtered list in a table
    st.subheader("List of Matching Gifts")
    st.table(filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"))

st.markdown("---")
st.caption("Tip: Hover over the bubbles to see the exact price!")
