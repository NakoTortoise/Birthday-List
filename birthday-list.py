import streamlit as st
import pandas as pd
import plotly.express as px

# ==========================================
# 1. PAGE CONFIG & SECRETS RETRIEVAL
# ==========================================
st.set_page_config(page_title="Josua's 21st Birthday List", page_icon="🎁", layout="wide")

# We fetch the secrets and force them to be plain strings
try:
    # Explicitly casting to str() prevents the AttrDict error
    SHEET_URL = str(st.secrets["connections"]["gsheets"])
    ADMIN_PWD = str(st.secrets["secrets"]["admin_password"])
except Exception as e:
    st.error(f"🚨 Configuration Error: {e}")
    st.info("Check your Streamlit Cloud Secrets for [connections] and [secrets] sections.")
    st.stop()

# The underscore _url tells Streamlit not to hash this internal object
@st.cache_data(ttl=60)
def load_data(_url_string):
    try:
        # Now pd.read_csv gets a clean string URL
        return pd.read_csv(_url_string)
    except Exception as e:
        st.error(f"🚨 Connection Error: {e}")
        return None

df = load_data(SHEET_URL)

# ==========================================
# 2. DATA CLEANING & VERIFICATION
# ==========================================
if df is not None:
    # Clean headers
    df.columns = [str(c).strip() for c in df.columns]
    
    # Check for HTML gibberish
    if not df.empty and '<!DOCTYPE' in str(df.columns[0]):
        st.error("🚨 App is reading a Web Page instead of Data.")
        st.stop()

    # Required columns check
    required = ['Gift Item', 'Price', 'Need', 'Want', 'Category']
    if not all(col in df.columns for col in required):
        st.warning(f"Header mismatch. Found: {list(df.columns)}")
        # Forced recovery if structure is correct but names are weird
        if len(df.columns) >= 5:
            df.columns = required + list(df.columns[5:])
            
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
    pwd_input = st.text_input("Enter Password", type="password")
    
    if ADMIN_PWD and pwd_input == ADMIN_PWD:
        st.success("Admin Verified")
        is_admin = True
    else:
        if not ADMIN_PWD:
            st.warning("Password not set in Secrets.")
        is_admin = False

# ==========================================
# 4. SIDEBAR FILTERS
# ==========================================
st.sidebar.markdown("---")
st.sidebar.header("🔍 Filter Options")

max_price = int(df['Price'].max())
budget = st.sidebar.slider("Max Budget (Rands)", 0, max_price + 1000, max_price, step=100)
min_need = st.sidebar.slider("Min 'Need' Score", 1, 10, 1)
min_want = st.sidebar.slider("Min 'Want' Score", 1, 10, 1)

filtered_df = df[
    (df['Price'] <= budget) & 
    (df['Need'] >= min_need) & 
    (df['Want'] >= min_want)
]

# ==========================================
# 5. CHART & TABLE
# ==========================================
if not filtered_df.empty:
    fig = px.scatter(filtered_df, x="Want", y="Need", size="Price", color="Category",
                     hover_name="Gift Item", text="Gift Item", size_max=40,
                     range_x=[0, 11], range_y=[0, 11], template="plotly_white")
    
    fig.update_layout(height=600, dragmode='pan')
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.dataframe(filtered_df[['Gift Item', 'Price', 'Category']], use_container_width=True, hide_index=True)
else:
    st.warning("No items match your filters.")

# ==========================================
# 6. ADMIN ACTIONS
# ==========================================
if is_admin:
    st.markdown("---")
    st.subheader("🛠️ Admin Tools")
    st.link_button("📂 Open Google Sheet to Edit", SHEET_URL.replace('/export?format=csv&gid=0', '/edit'))
    if st.button("🔄 Refresh Data Now"):
        st.cache_data.clear()
        st.rerun()
