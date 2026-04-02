import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & CLEAN DATA LOADING
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

@st.cache_data(ttl=5) # Cache for 5 seconds during debugging
def load_data():
    try:
        # Pull the URL from secrets
        csv_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # Read the data directly
        data = pd.read_csv(csv_url)
        return data
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")
        return None

df = load_data()

# ==========================================
# 2. DATA VERIFICATION (Gibberish Protection)
# ==========================================
if df is not None:
    # Check if we accidentally pulled an HTML login page (the error you got)
    first_cell = str(df.columns[0])
    if '<!DOCTYPE' in first_cell or '<html' in first_cell.lower():
        st.error("🚨 The app is reading a 'Web Page' instead of raw data.")
        st.write("Current URL in Secrets is likely an '/edit' link instead of an '/export' link.")
        st.info("💡 **Fix:** Change the end of your URL in Secrets to `/export?format=csv&gid=0`.")
        st.stop()

    # Clean headers and convert numbers
    df.columns = [str(c).strip() for c in df.columns]
    
    # Ensure Row 1 columns exist
    for col in ['Gift Item', 'Price', 'Need', 'Want', 'Category']:
        if col not in df.columns:
            st.error(f"⚠️ Column '{col}' not found. Found: {list(df.columns)}")
            st.stop()

    # Numeric conversion
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
    df['Need'] = pd.to_numeric(df['Need'], errors='coerce').fillna(1)
    df['Want'] = pd.to_numeric(df['Want'], errors='coerce').fillna(1)
else:
    st.stop()

# ==========================================
# 3. MAIN UI & AUTHENTICATION
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

# Admin Sidebar Toggle
st.sidebar.header("🔐 Admin Controls")
with st.sidebar.expander("Edit Mode"):
    pwd_input = st.text_input("Password", type="password")
    actual_pwd = st.secrets.get("admin_password")
    
    if actual_pwd and pwd_input == actual_pwd:
        st.success("Admin Verified")
        is_admin = True
    else:
        is_admin = False

st.success("✅ Connected to Live Database", icon="🚀")

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Options")

max_price = int(df['Price'].max())
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_price + 1000, max_price, step=100)
min_need = st.sidebar.slider("Min 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Min 'Want' Score", 1, 10, 1)

if st.sidebar.button("🔄 Reset Chart View"):
    st.rerun()

filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 5. CHART DISPLAY (Locked Panning)
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
    
    fig.update_layout(
        height=650,
        dragmode='pan', 
        xaxis=dict(range=[0, 11], constrain='domain', fixedrange=False),
        yaxis=dict(range=[0, 11], constrain='domain', fixedrange=False),
        legend=dict(orientation="h", yanchor="top", y=-0.25, xanchor="center", x=0.5),
        margin=dict(l=40, r=40, t=20, b=150)
    )

    st.plotly_chart(fig, use_container_width=True, config={
        'scrollZoom': True, 
        'displayModeBar': True,
        'doubleClick': 'reset',
        'displaylogo': False,
        'modeBarButtonsToRemove': ['zoom2d', 'select2d', 'lasso2d', 'autoScale2d']
    })

# ==========================================
# 6. DATA TABLE & TOTALS
# ==========================================
st.markdown("---")
total_rands = filtered_df['Price'].sum()
st.metric("Total Value of Filtered Gifts", f"R {total_rands:,.2f}")

col_left, col_center, col_right = st.columns([0.1, 0.8, 0.1])
with col_center:
    st.dataframe(
        filtered_df[['Gift Item', 'Price', 'Category']].sort_values(by="Price"),
        use_container_width=True,
        hide_index=True
    )

# ==========================================
# 7. FOOTER
st.caption("Tip: Use scroll wheel/pinch to zoom. Double-click to reset view.")
