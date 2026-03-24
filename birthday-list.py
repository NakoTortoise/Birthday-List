import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & DATA
# ==========================================
st.set_page_config(page_title="My Gift List", page_icon="🎁", layout="wide")

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

# Price Filter with Snapping (Step=50)
max_val = int(df['Price'].max())
# We use step=50 to make it snap in R50 increments
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_val + 500, max_val, step=50)

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
                     labels={"Want": "Want (1-10)", "Need": "Need (1-10)"},
                     template="plotly_white")

    # MOBILE OPTIMIZATION: Move legend to bottom and clean up text
    fig.update_traces(textposition='top center')
    fig.update_layout(
        height=600,
        legend=dict(
            orientation="h",     # Horizontal orientation
            yanchor="bottom",
            y=-0.2,              # Move it below the X-axis
            xanchor="center",
            x=0.5
        ),
        margin=dict(l=20, r=20, t=20, b=100) # Extra bottom margin for legend
    )

    st.plotly_chart(fig, use_container_width=True)

    # Display list as a nice clean table
    st.subheader("Selected Gifts")
    st.dataframe(
        filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
        use_container_width=True,
        hide_index=True
    )

st.markdown("---")
st.caption("Tip: On mobile, pinch the chart to zoom or tap bubbles for details.")
