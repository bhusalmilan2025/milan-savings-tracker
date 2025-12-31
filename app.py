import streamlit as st
import pandas as pd
from fpdf import FPDF
from datetime import datetime

# Page Setup
st.set_page_config(page_title="Milan Finance", page_icon="⚖️", layout="wide")

# Minimalist CSS with subtle background colors
st.markdown("""
    <style>
    /* Main Background */
    .stApp {
        background-color: #f4f7f6;
    }
    
    /* Metric Cards */
    div[data-testid="stMetric"] {
        background-color: #ffffff;
        border: 1px solid #e6e9ef;
        padding: 20px 15px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.02);
    }

    /* Container Styling */
    .stTabs {
        background-color: #ffffff;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.03);
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #e1e4e8;
    }

    /* Clean Header Colors */
    .needs-header { color: #2e5a88; font-weight: 600; }
    .wants-header { color: #c87e2f; font-weight: 600; }
    .savings-header { color: #2d7a4d; font-weight: 600; }
    </style>
    """, unsafe_allow_html=True)

# --- RESET LOGIC ---
def reset_all():
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.toast("Dashboard Cleaned")

def normalize(amount, frequency):
    return {"Weekly": amount * 2, "Monthly": amount / 2.1667}.get(frequency, amount)

# --- HEADER ---
st.title("Financial Allocation Dashboard")
st.caption(f"Cycle Audit | {datetime.now().strftime('%d %B %Y')}")

# --- SIDEBAR ---
with st.sidebar:
    st.markdown("### Controls")
    st.button("Reset All Variables", on_click=reset_all, use_container_width=True)
    st.divider()
    
    st.markdown("### Revenue")
    salary = st.number_input("Fortnightly Net Income", min_value=0.0, step=100.0, key="salary")
    carry_forward = st.number_input("Balance Carryover", min_value=0.0, step=10.0, key="carry")
    
    st.divider()
    st.markdown("### Savings Target")
    goal_name = st.text_input("Objective", "Primary Savings")
    goal_target = st.number_input("Goal Target", min_value=0.0, value=1000.0)
    current_saved = st.number_input("Existing Balance", min_value=0.0, value=0.0)

    total_pool = salary + carry_forward

# --- CALCULATE ALLOCATIONS ---
alloc_needs = total_pool * 0.50
alloc_wants = total_pool * 0.30
alloc_savings = total_pool * 0.20

# --- MAIN DASHBOARD ---
tab1, tab2 = st.tabs(["Allocation Entry", "Performance & Log"])

with tab1:
    st.write("### Strategic Distribution")
    b1, b2, b3 = st.columns(3)
    exp_vals = {}
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown('<p class="needs-header">ESSENTIAL (50%)</p>', unsafe_allow_html=True)
        st.caption(f"Budget: ${alloc_needs:,.2f}")
        needs_list = ["Rent/Mortgage", "Groceries", "Utilities", "Transport"]
        cat_needs_total = 0
        for cat in needs_list:
            c_in, c_fr = st.columns([3, 2])
            v = c_in.number_input(cat, min_value=0.0, key=f"v_{cat}")
            f = c_fr.selectbox("Cycle", ["Weekly", "Fortnightly", "Monthly"], index=1, key=f"f_{cat}")
            amt = normalize(v, f)
            exp_vals[cat] = (amt, "Essential")
            cat_needs_total += amt
        b1.metric("Essential Remaining", f"${(alloc_needs - cat_needs_total):,.2f}", delta=f"-${cat_needs_total:,.2f}", delta_color="inverse")

    with col2:
        st.markdown('<p class="wants-header">DISCRETIONARY (30%)</p>', unsafe_allow_html=True)
        st.caption(f"Budget: ${alloc_wants:,.2f}")
        wants_list = ["Subscriptions", "Lifestyle"]
        cat_wants_total = 0
        for cat in wants_list:
            c_in, c_fr = st.columns([3, 2])
            v = c_in.number_input(cat, min_value=0.0, key=f"v_{cat}")
            f = c_fr.selectbox("Cycle", ["Weekly", "Fortnightly", "Monthly"], index=1, key=f"f_{cat}")
            amt = normalize(v, f)
            exp_vals[cat] = (amt, "Discretionary")
            cat_wants_total += amt
        b2.metric("Discretionary Remaining", f"${(alloc_wants - cat_wants_total):,.2f}", delta=f"-${cat_wants_total:,.2f}", delta_color="inverse")

    with col3:
        st.markdown('<p class="savings-header">SAVINGS/TEMP (20%)</p>', unsafe_allow_html=True)
        st.caption(f"Budget: ${alloc_savings:,.2f}")
        temp_total = 0
        for i in range(2):
            label = st.text_input(f"Label {i+1}", value=f"Temporary {i+1}", key=f"lab_t_{i}")
            c_in, c_fr = st.columns([3, 2])
            v = c_in.number_input(f"Value", min_value=0.0, key=f"v_t_{i}")
            f = c_fr.selectbox("Cycle", ["Weekly", "Fortnightly", "Monthly"], index=1, key=f"f_t_{i}")
            amt = normalize(v, f)
            exp_vals[label] = (amt, "Temporary")
            temp_total += amt
        b3.metric("Savings Contribution", f"${(alloc_savings - temp_total):,.2f}", delta=f"-${temp_total:,.2f}", delta_color="inverse")

# --- SUMMARY CALCULATIONS ---
total_spent = cat_needs_total + cat_wants_total + temp_total
leftover = total_pool - total_spent
new_total_saved = current_saved + leftover
progress_pct = min(1.0, new_total_saved / goal_target) if goal_target > 0 else 0

with tab2:
    st.markdown(f"### Target Progress: {goal_name}")
    st.progress(progress_pct)
    st.write(f"**Current: ${new_total_saved:,.2f}** / Target: ${goal_target:,.2f} ({progress_pct*100:.1f}%)")
    
    st.divider()
    
    st.write("### Cycle Summary")
    r1, r2, r3 = st.columns(3)
    r1.metric("Available Funds", f"${total_pool:,.2f}")
    r2.metric("Total Expenses", f"${total_spent:,.2f}")
    r3.metric("Carryover to Next", f"${leftover:,.2f}")

    st.divider()
    
    st.write("### Itemized Log")
    log_data = [{"Description": k, "Type": v[1], "Amount": v[0]} for k, v in exp_vals.items() if v[0] > 0]
    if log_data:
        st.dataframe(pd.DataFrame(log_data), use_container_width=True, hide_index=True)
    else:
        st.info("Waiting for expenditure data...")

# --- PDF ---
def create_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 14)
    pdf.cell(0, 10, 'FINANCIAL AUDIT STATEMENT', ln=True)
    pdf.set_font('Helvetica', '', 10)
    pdf.cell(0, 10, f"Generated: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
    pdf.ln(10)
    pdf.cell(0, 10, f"Total Income/Carry: ${total_pool:,.2f}", ln=True)
    pdf.cell(0, 10, f"Total Expenses: ${total_spent:,.2f}", ln=True)
    pdf.cell(0, 10, f"Net Balance: ${leftover:,.2f}", ln=True)
    return pdf.output(dest='S').encode('latin-1')

if st.sidebar.button("Export PDF Report"):
    pdf_bytes = create_pdf()
    st.sidebar.download_button("Download Report", data=pdf_bytes, file_name="Statement.pdf")
