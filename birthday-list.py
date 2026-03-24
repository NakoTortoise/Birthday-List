import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ==========================================
# 1. PAGE CONFIG & DATA LOADING
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

@st.cache_data
def load_data():
    # Get the directory where THIS script (birthday_app.py) is located
    base_path = os.path.dirname(__file__)
    # Combine it with the filename to get an absolute path
    file_path = os.path.join(base_path, 'gifts.csv')
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        # Debugging: this will show you exactly where the app IS looking
        st.error(f"Looking for file at: {file_path}")
        return None

df = load_data()

# ==========================================
# 2. MAIN UI & ERROR HANDLING
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

if df is None:
    st.error("⚠️ 'gifts.csv' not found! Please make sure the file is in the same directory as this script.")
    st.info("Your CSV should have these columns: Gift Item, Price, Need, Want, Category")
    st.stop()

st.caption("Tip: Use the sidebar to filter price, need and want.")

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filter Options")

# Price Filter with Snapping (Step=100)
max_val = int(df['Price'].max())
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_val + 500, max_val, step=100)

# Need & Want Filters
min_need = st.sidebar.slider("Min 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Min 'Want' Score", 1, 10, 1)

# Apply Filters
filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 4. PLOTTING
# ==========================================
if filtered_df.empty:
    st.warning("No gifts match those filters! Try adjusting the sidebar.")
else:
    # Creating the Bubble Chart
    fig = px.scatter(filtered_df, 
                     x="Want", 
                     y="Need", 
                     size="Price", 
                     color="Category",
                     hover_name="Gift Item",
                     text="Gift Item",
                     size_max=50, 
                     range_x=[0, 11], 
                     range_y=[0, 11],
                     labels={"Want": "Want Score (1-10)", "Need": "Need Score (1-10)"},
                     template="plotly_white")

    # CUSTOMIZATIONS FOR PAN & OVERLAP
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        height=650,
        dragmode='pan',  # Sets "Pan" as the default interaction tool
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,      # Pushed further down to avoid X-axis overlap
            xanchor="center",
            x=0.5,
            title_text="" # Removes the "Category" title to save space
        ),
        margin=dict(l=40, r=40, t=20, b=150), # Large bottom margin for the legend
        xaxis=dict(fixedrange=False), 
        yaxis=dict(fixedrange=False)
    )

    # Display list as a nice clean table
    st.subheader("Selected Gifts Table")
    
    # Create three columns; the middle one will hold our table
    # Adjust the ratios [1, 2, 1] to change how much space the table takes
    col_left, col_main, col_right = st.columns([1, 2, 1])
    
    with col_main:
        st.dataframe(
            filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
            use_container_width=False,  # This prevents the "stretch"
            hide_index=True
        )

st.markdown("---")
st.caption("Navigation: Use one finger (mobile) or mouse click (desktop) to PAN. Scroll to zoom.")
