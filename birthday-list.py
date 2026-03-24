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
    # This finds the folder where this .py file is saved
    base_path = os.path.dirname(__file__)
    file_path = os.path.join(base_path, 'birthday-list.csv')
    
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    else:
        return None

df = load_data()

# ==========================================
# 2. MAIN UI & ERROR HANDLING
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

if df is None:
    st.error("⚠️ 'gifts.csv' not found!")
    st.info("Please ensure 'gifts.csv' is in the same folder as this script.")
    st.stop()

st.caption("Tip: Use the sidebar to filter by Price, Need, and Want.")

st.warning("⚠️ **Note:** This app currently contains **test data only**. Please check back later for the finalized list!", icon="🚀")

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filter Options")

# Price Filter (Step=100 for easy snapping)
max_val = int(df['Price'].max())
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_val + 500, max_val, step=100)

# Need & Want Filters
min_need = st.sidebar.slider("Min 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Min 'Want' Score", 1, 10, 1)

# Apply Filters to the Data
filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 4. CHART & TABLE DISPLAY
# ==========================================
if filtered_df.empty:
    st.warning("No gifts match those filters! Try adjusting the sliders in the sidebar.")
else:
    # --- Create the Bubble Chart ---
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

    # --- Chart Styling (Pan mode & Legend Position) ---
    fig.update_traces(textposition='top center')
    
    fig.update_layout(
        height=650,
        dragmode='pan',  # Default to Panning instead of Zooming
        legend=dict(
            orientation="h",
            yanchor="top",
            y=-0.25,      # Pushes legend down to avoid X-axis overlap
            xanchor="center",
            x=0.5,
            title_text="" 
        ),
        margin=dict(l=40, r=40, t=20, b=150), # Big bottom margin for the legend
        xaxis=dict(fixedrange=False), 
        yaxis=dict(fixedrange=False)
    )

    # --- Display the Chart ---
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

    st.markdown("---")

    # --- Display the Centered Table ---
    st.subheader("Selected Gifts Details")
    
    # We use columns to "center" the table and prevent it from stretching too wide
    col_left, col_center, col_right = st.columns([0.1, 0.8, 0.1])
    
    with col_center:
        st.dataframe(
            filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
            use_container_width=True, # Fits the width of this specific 80% column
            hide_index=True
        )

# ==========================================
# 5. FOOTER
