import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & PERSISTENT CONNECTION
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

# Create connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

@st.cache_data(ttl=300) 
def load_data():
    # Attempting to read from Sheet1
    return conn.read(worksheet="Sheet1")

try:
    df = load_data()
except Exception as e:
    st.error(f"Failed to connect to Google Sheets: {e}")
    st.stop()

# ==========================================
# 2. MAIN UI & AUTHENTICATION
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

# Admin Sidebar Toggle with safe secret access
st.sidebar.header("🔐 Admin Controls")
with st.sidebar.expander("Edit Mode"):
    pwd_input = st.text_input("Password", type="password")
    
    # We use .get to prevent the "KeyError" crash if the secret is missing
    actual_pwd = st.secrets.get("admin_password")
    
    if actual_pwd and pwd_input == actual_pwd:
        st.success("Admin Verified")
        is_admin = True
    else:
        if not actual_pwd:
            st.error("Secret 'admin_password' not found in config.")
        is_admin = False

st.success("✅ Connected to Live Database", icon="🚀")

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Options")

# Force numeric types to prevent slider errors
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
df['Need'] = pd.to_numeric(df['Need'], errors='coerce').fillna(1)
df['Want'] = pd.to_numeric(df['Want'], errors='coerce').fillna(1)

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
# 4. CHART DISPLAY (Locked Panning)
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
        xaxis=dict(
            range=[0, 11],
            constrain='domain',
            fixedrange=False 
        ),
        yaxis=dict(
            range=[0, 11],
            constrain='domain',
            fixedrange=False
        ),
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
# 5. DATA TABLE & TOTALS
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
# 6. ADMIN EDIT FORM (Persistent)
# ==========================================
if is_admin:
    st.markdown("---")
    st.subheader("➕ Add New Gift to Live List")
    with st.form("add_form", clear_on_submit=True):
        f_item = st.text_input("Gift Item Name")
        f_price = st.number_input("Price (R)", min_value=0, step=50)
        f_need = st.slider("Need Score", 1, 10, 5)
        f_want = st.slider("Want Score", 1, 10, 5)
        f_cat = st.selectbox("Category", df['Category'].unique() if not df.empty else ["Tech", "Tools", "Apparel"])
        
        if st.form_submit_with_button("Submit to Google Sheets"):
            new_row = pd.DataFrame([{
                "Gift Item": f_item, 
                "Price": f_price, 
                "Need": f_need, 
                "Want": f_want, 
                "Category": f_cat
            }])
            updated_df = pd.concat([df, new_row], ignore_index=True)
            
            # This updates the actual Google Sheet
            conn.update(worksheet="Sheet1", data=updated_df)
            st.cache_data.clear()
            st.success(f"Added {f_item} successfully!")
            st.rerun()

# ==========================================
# 7. FOOTER
st.caption("Tip: Use scroll wheel/pinch to zoom. Double-click to reset view.")
