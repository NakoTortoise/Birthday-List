import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & DATA
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

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
st.sidebar.header("🔍 Filter Options")

# Price Filter with Snapping (Step=100 for even cleaner UX)
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
# 3. MAIN UI & PLOTTING
# ==========================================
st.title("🎁 My Birthday Wishlist")

st.caption("Tip: Use the sidebar to filter by price, need or want.")

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
        xaxis=dict(fixedrange=False), # Allows horizontal panning
        yaxis=dict(fixedrange=False)  # Allows vertical panning
    )

    # config option to ensure the modebar shows the pan icon as active
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'displayModeBar': True})

    # Display list as a nice clean table
    st.subheader("Selected Gifts Table")
    st.dataframe(
        filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("Navigation: Use one finger (mobile) or mouse click (desktop) to PAN. Scroll to zoom.")
