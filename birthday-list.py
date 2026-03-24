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
    base_path = os.path.dirname(__file__)
    # Ensure this matches your filename on GitHub
    file_path = os.path.join(base_path, 'birthday-list.csv')
    
    if os.path.exists(file_path):
        try:
            return pd.read_csv(file_path, encoding='utf-8-sig')
        except Exception:
            return pd.read_csv(file_path, encoding='cp1252')
    else:
        return None

df = load_data()

# ==========================================
# 2. MAIN UI & ERROR HANDLING
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

if df is None:
    st.error("⚠️ 'birthday-list.csv' not found!")
    st.stop()

st.success("✅ **Notice:** Panning is limited to the 0-11 range. Zoom in for details!", icon="🚀")

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.header("🔍 Filter Options")
max_val = int(df['Price'].max())
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_val + 500, max_val, step=100)
min_need = st.sidebar.slider("Min 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Min 'Want' Score", 1, 10, 1)

# Reset button for a clean UI snap-back
if st.sidebar.button("🔄 Reset View"):
    st.rerun()

filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 4. CHART & TABLE DISPLAY
# ==========================================
if filtered_df.empty:
    st.warning("No gifts match those filters!")
else:
    fig = px.scatter(filtered_df, 
                     x="Want", 
                     y="Need", 
                     size="Price", 
                     color="Category",
                     hover_name="Gift Item",
                     text="Gift Item",
                     size_max=50, 
                     labels={"Want": "Want Score (1-10)", "Need": "Need Score (1-10)"},
                     template="plotly_white")

    fig.update_traces(textposition='top center')
    
    # THE LOCKING MECHANISM
    fig.update_layout(
        height=650,
        dragmode='pan', 
        xaxis=dict(
            range=[0, 11],
            constrain='domain',
            fixedrange=False # Allows zooming IN
        ),
        yaxis=dict(
            range=[0, 11],
            constrain='domain',
            fixedrange=False # Allows zooming IN
        ),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=20, b=150)
    )

    # Use 'config' to block the user from scaling the axes manually
    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True, 
        'displayModeBar': True,
        'doubleClick': 'reset', # Double tap/click to snap back to 0-11
        'displaylogo': False,
        'modeBarButtonsToRemove': ['zoom2d', 'select2d', 'lasso2d', 'autoScale2d', 'resetScale2d']
    })

    st.markdown("---")
    st.subheader("Selected Gifts Details")
    
    col_left, col_center, col_right = st.columns([0.1, 0.8, 0.1])
    with col_center:
        st.dataframe(
            filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
            use_container_width=True,
            hide_index=True
        )
