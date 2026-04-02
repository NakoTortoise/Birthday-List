import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & DIRECT DATA LOADING
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

@st.cache_data(ttl=10)
def load_data():
    try:
        # Pull the URL from your secrets
        sheet_url = st.secrets["connections"]["gsheets"]["spreadsheet"]
        
        # ENGINEERING TRICK: Convert the "edit" URL to a "export as CSV" URL
        # This bypasses the 400 Bad Request by requesting a raw data stream
        csv_url = sheet_url.replace('/edit#gid=', '/export?format=csv&gid=')
        if '/edit' in sheet_url and 'gid' not in sheet_url:
            csv_url = sheet_url.replace('/edit', '/export?format=csv')
            
        return pd.read_csv(csv_url)
    except Exception as e:
        st.error("🚨 Direct Connection Failed")
        st.write(f"**Error Details:** {e}")
        return None

df = load_data()

if df is None or df.empty:
    st.info("💡 Check: Is Row 1 of your Google Sheet exactly: Gift Item, Price, Need, Want, Category?")
    st.stop()

# ==========================================
# 2. MAIN UI & AUTHENTICATION
# ==========================================
st.title("🎁 Josua's 21st Birthday List")

# Admin Sidebar Toggle with safe secret access
st.sidebar.header("🔐 Admin Controls")
# Replace your authentication logic with this "safer" version
with st.sidebar.expander("Edit Mode"):
    pwd_input = st.text_input("Password", type="password")
    
    # .get() prevents a crash if the key is missing from secrets.toml
    target_password = st.secrets.get("admin_password", "DEFAULT_IF_MISSING")
    
    if pwd_input == target_password and target_password != "DEFAULT_IF_MISSING":
        st.success("Admin Verified")
        is_admin = True
    else:
        is_admin = False

st.success("✅ Connected to Live Database", icon="🚀")

# ==========================================
# 3. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("---")
# ==========================================
# 3. DATA CLEANING & SIDEBAR FILTERS
# ==========================================
# Clean column names: remove leading/trailing spaces and handle case sensitivity
df.columns = df.columns.str.strip()

# Ensure these exact columns exist to avoid the KeyError
required_columns = ['Gift Item', 'Price', 'Need', 'Want', 'Category']
for col in required_columns:
    if col not in df.columns:
        st.error(f"⚠️ Missing column: '{col}'")
        st.info(f"Your Sheet columns are: {list(df.columns)}")
        st.stop()

# Now safe to convert to numeric
df['Price'] = pd.to_numeric(df['Price'], errors='coerce').fillna(0)
df['Need'] = pd.to_numeric(df['Need'], errors='coerce').fillna(1)
df['Want'] = pd.to_numeric(df['Want'], errors='coerce').fillna(1)

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
