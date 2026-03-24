import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIGURATION & THEME
# ==========================================
st.set_page_config(page_title="My Matched Gift List", page_icon="🎁", layout="wide")

# Custom CSS for styling (optional, but makes it neat)
st.markdown("""
<style>
    .big-font { font-size:18px !important; color: #4F4F4F; }
    .stDataFrame { border: 1px solid #e6e6e6; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 2. YOUR BIRTHDAY LIST DATA ENTRY
# ==========================================
# Edit this dictionary to add your gifts!
# PRICE is in Rands (ZAR). NEED and WANT are 1-10.
my_gifts = [
    {"Gift Item": "Noise Cancelling Headphones", "Price": 3500, "Need": 8, "Want": 9},
    {"Gift Item": "Mechanical Keyboard", "Price": 1200, "Need": 4, "Want": 10},
    {"Gift Item": "Screwdriver Set (Engineering)", "Price": 450, "Need": 10, "Want": 3},
    {"Gift Item": "Minecraft Server Sub (1 Yr)", "Price": 250, "Need": 2, "Want": 8},
    {"Gift Item": "Python Data Science Book", "Price": 750, "Need": 7, "Want": 6},
    {"Gift Item": "Stellenbosch Hoodie", "Price": 600, "Need": 5, "Want": 7},
    {"Gift Item": "Arduino Starter Kit", "Price": 1500, "Need": 9, "Want": 8},
]

# Load into a Pandas DataFrame
df = pd.DataFrame(my_gifts)

# ==========================================
# 3. DATA PROCESSING: WEIGHTING THE PRICE
# ==========================================
# We need an "Affordability Score" (1-10) where 10 is cheap and 1 is expensive.
# We base this on the most expensive item on your list + a buffer.
max_price_on_list = df['Price'].max()
budget_ceiling = max_price_on_list * 1.1 # Adding 10% buffer

# Simple linear weighting formula:
# Score = 10 - ((CurrentPrice / BudgetCeiling) * 9)
# If price is 0, score is 10. If price is BudgetCeiling, score is 1.
df['Affordability'] = 10 - ((df['Price'] / budget_ceiling) * 9)
# Round for cleaner display
df['Affordability'] = df['Affordability'].round(1)

# ==========================================
# 4. STREAMLIT UI LAYOUT
# ==========================================
st.title("🎁 My Matched Birthday Wishlist")
st.markdown('<p class="big-font">This app helps you find the perfect gift based on my needs, wants, and your budget.</p>', unsafe_allow_html=True)

# Setup columns for layout
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("How to Read the Chart")
    st.info("""
    **1. Look at the lines.** Each line is one gift.
    **2. The Axes:**
    * **Price (R):** The actual cost in Rands.
    * **Need (1-10):** How useful this is for my studies/daily life.
    * **Want (1-10):** How much I actually desire this item.
    * **Affordability (1-10):** A calculated score where **10 is very affordable (cheap)** and **1 is expensive.**

    **3. Finding "The Best Deal":**
    You are looking for lines that connect **HIGH** Need, **HIGH** Want, and **LOW** Price (which will correspond to a **HIGH** Affordability score).
    """)

    # Display the raw data table below the instructions
    st.subheader("The Raw List")
    # Show only the original columns for clarity
    st.dataframe(df[['Gift Item', 'Price', 'Need', 'Want']], use_container_width=True)


with col2:
    st.subheader("Gift Priority Matrix (Parallel Coordinates)")

    # ==========================================
    # 5. THE CHART: PARALLEL COORDINATES
    # ==========================================
    fig = px.parallel_coordinates(df,
                                 color="Affordability", # Lines colored by affordability (10=green, 1=red)
                                 dimensions=['Price', 'Need', 'Want', 'Affordability'],
                                 color_continuous_scale=px.colors.diverging.Tealrose, # Good contrast
                                 labels={
                                     "Price": "Price (ZAR)",
                                     "Need": "Need (1-10)",
                                     "Want": "Want (1-10)",
                                     "Affordability": "Affordability (10=Cheap)"
                                 })

    # Adjust layout for better display in Streamlit
    fig.update_layout(
        margin=dict(l=50, r=10, t=40, b=20),
        height=550
    )

    # Display the Plotly chart in Streamlit
    st.plotly_chart(fig, use_container_width=True)

st.markdown("---")
st.caption(f"App created for Stellenbosch University Engineering Student. Max list price detected: R{max_price_on_list:.2f}")
