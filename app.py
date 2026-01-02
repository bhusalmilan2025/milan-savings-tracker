import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Milan Finance Pro", page_icon="⚖️", layout="wide")

# CSS for a minimalist look
st.markdown("""
    <style>
    .stApp { background-color: #f4f7f6; }
    div[data-testid="stMetric"] { background-color: #ffffff; border: 1px solid #e6e9ef; padding: 20px; border-radius: 10px; }
    .stTabs { background-color: #ffffff; padding: 20px; border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)

# --- GOOGLE SHEETS CONNECTION ---
# This creates a persistent connection to your sheet
conn = st.connection("gsheets", type=GSheetsConnection)

def fetch_data():
    return conn.read(worksheet="Sheet1", ttl="0") # ttl="0" ensures it fetches fresh data every time

# --- APP LOGIC ---
st.title("Milan Fortnightly Tracker")
st.caption(f"Live Sync Active | {datetime.now().strftime('%d %B %Y')}")

# --- SIDEBAR: INCOME SETUP ---
with st.sidebar:
    st.header("Financial Core")
    salary = st.number_input("Fortnightly Salary ($)", min_value=0.0, value=2500.0, step=100.0)
    carry_over = st.number_input("Carry Over ($)", min_value=0.0, value=0.0)
    total_pool = salary + carry_over
    
    st.divider()
    st.header("Quick Add Expense")
    with st.form("expense_form", clear_on_submit=True):
        desc = st.text_input("What did you buy?")
        amt = st.number_input("Amount ($)", min_value=0.0, step=1.0)
        cat = st.selectbox("Bucket", ["Needs (50%)", "Wants (30%)", "Temporary/Savings (20%)"])
        submit = st.form_submit_button("Record Transaction")
        
        if submit and desc and amt > 0:
            # Create new row
            new_row = pd.DataFrame([{
                "Date": datetime.now().strftime("%Y-%m-%d"),
                "Description": desc,
                "Category": cat,
                "Amount": amt
            }])
            # Fetch, Append, and Update
            existing_data = fetch_data()
            updated_data = pd.concat([existing_data, new_row], ignore_index=True)
            conn.update(worksheet="Sheet1", data=updated_data)
            st.success("Synced to Cloud!")

# --- CALCULATIONS ---
df = fetch_data()
# Filter to only show current fortnight (simplified logic)
# We calculate totals based on the 'Bucket' chosen
spent_needs = df[df['Category'] == "Needs (50%)"]['Amount'].sum()
spent_wants = df[df['Category'] == "Wants (30%)"]['Amount'].sum()
spent_temp = df[df['Category'] == "Temporary/Savings (20%)"]['Amount'].sum()

# Allocation Targets
target_needs = total_pool * 0.5
target_wants = total_pool * 0.3
target_savings = total_pool * 0.2

# --- DASHBOARD ---
tab1, tab2 = st.tabs(["Bucket Status", "Transaction History"])

with tab1:
    st.write("### Live Bucket Balances")
    c1, c2, c3 = st.columns(3)
    
    c1.metric("Essential (Needs)", f"${(target_needs - spent_needs):,.2f}", f"-${spent_needs:,.2f}", delta_color="inverse")
    c2.metric("Discretionary (Wants)", f"${(target_wants - spent_wants):,.2f}", f"-${spent_wants:,.2f}", delta_color="inverse")
    c3.metric("Savings/Temp", f"${(target_savings - spent_temp):,.2f}", f"-${spent_temp:,.2f}", delta_color="inverse")

    st.divider()
    total_spent = spent_needs + spent_wants + spent_temp
    leftover = total_pool - total_spent
    st.subheader(f"Total Carry Over for next Fortnight: ${leftover:,.2f}")

with tab2:
    st.write("### Itemized Log (From Google Sheets)")
    st.dataframe(df, use_container_width=True)
    if st.button("Clear All Data (New Fortnight)"):
        # This overwrites the sheet with just the headers
        empty_df = pd.DataFrame(columns=["Date", "Description", "Category", "Amount"])
        conn.update(worksheet="Sheet1", data=empty_df)
        st.rerun()
