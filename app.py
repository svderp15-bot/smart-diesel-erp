# CIDPL FULL PROJECT ERP v7.0
# PROJECT: RAW WATER RESERVOIR, ANUPPUR (PHASE-I)
# CONTRACTOR: BHAIYALAL INFRASTRUCTURE PVT. LTD. & CIDPL
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CIDPL SECURE ERP", layout="wide", page_icon="🏗️")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .footer { text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .login-box { max-width: 400px; margin: auto; padding: 40px; border: 1px solid #E5E7EB; border-radius: 10px; background: white; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; }
    .metric-container { background: white; border: 1px solid #E5E7EB; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="login-box">', unsafe_allow_html=True)
        st.header("🔐 CIDPL ERP LOGIN")
        st.write("Project: Anuppur Reservoir Phase-I")
        pwd = st.text_input("Enter Access Password", type="password")
        if st.button("Login", use_container_width=True):
            if pwd == "Welcome@123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("Incorrect password. Please try again.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in:
    login_page()
    st.stop()

# ---------------- INITIALIZE STATE ----------------
# --- 1. BOQ MASTER DATA (58.09 Cr Project Scopes & Rates) ---
if 'boq_master' not in st.session_state:
    # Pre-loading project-specific BOQ from user data
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil)", "Total Qty": 250000.0, "UoM": "Sqm", "Unit Rate": 15.0},
        {"Code": "30a", "Item": "Earthwork excavation soil (0-5m)", "Total Qty": 535500.0, "UoM": "CuM", "Unit Rate": 120.0},
        {"Code": "40a", "Item": "Weathered rock excavation (0-5m)", "Total Qty": 428400.0, "UoM": "CuM", "Unit Rate": 250.0},
        {"Code": "40b", "Item": "Weathered rock excavation (5-10m)", "Total Qty": 642600.0, "UoM": "CuM", "Unit Rate": 310.0},
        {"Code": "70a", "Item": "Hard rock - Blasting (0-5m)", "Total Qty": 292740.0, "UoM": "CuM", "Unit Rate": 650.0},
        {"Code": "80", "Item": "Transportation of Earth/Rock", "Total Qty": 2850000.0, "UoM": "CuM", "Unit Rate": 85.0},
        {"Code": "90", "Item": "Embankment Layer Filling", "Total Qty": 473333.0, "UoM": "CuM", "Unit Rate": 140.0},
        {"Code": "120", "Item": "1000 micron HDPE Sheet", "Total Qty": 444803.0, "UoM": "Sqm", "Unit Rate": 320.0},
        {"Code": "130", "Item": "Cement concrete liner (75mm)", "Total Qty": 163000.0, "UoM": "Sqm", "Unit Rate": 450.0}
    ])

# --- 2. BOQ PROGRESS LOG (Pre-loaded with DPR 05.04.2026) ---
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        {"Date": "2026-04-04", "Code": "10", "Item": "Stripping (top soil)", "Done Qty": 63204.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "30a", "Item": "Earthwork excavation soil (0-5m)", "Done Qty": 100274.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-05", "Code": "10", "Item": "Stripping (top soil)", "Done Qty": 0.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "30a", "Item": "Earthwork excavation soil (0-5m)", "Done Qty": 4466.0, "Remark": "DPR Entry"}
    ]

# --- 3. DIESEL, MANPOWER, SNAPSHOT ---
if 'manpower_log' not in st.session_state:
    st.session_state.manpower_log = [{"Date": "2026-04-05", "Staff": 15, "Operators": 20, "Skilled": 2, "Unskilled": 4, "Security": 2}]

if 'site_snapshot' not in st.session_state:
    st.session_state.site_snapshot = [{"Date": "2026-04-05", "Excavator": 6, "Dumper": 20, "Road Roller": 2, "Diesel Tanker": 1, "Water Tanker": 4}]

if 'machine_master' not in st.session_state:
    st.session_state.machine_master = pd.DataFrame([
        {"MACHINE NO": "EX KOBEELCO 380", "TYPE": "EXCAVATOR", "AVG": 22.5},
        {"MACHINE NO": "EX KOMATSU 300", "TYPE": "EXCAVATOR", "AVG": 20.0},
        {"MACHINE NO": "HYVA 2218", "TYPE": "TIPPER", "AVG": 2.3}
    ])

if 'consumption_log' not in st.session_state: st.session_state.consumption_log = []
if 'receipt_log' not in st.session_state: st.session_state.receipt_log = []
if 'opening_stock' not in st.session_state: st.session_state.opening_stock = 10000.0

# ---------------- CORE LOGIC ----------------
def calculate_status():
    status = st.session_state.boq_master.copy()
    if not st.session_state.boq_progress:
        status["Done Qty"] = 0.0
    else:
        agg = pd.DataFrame(st.session_state.boq_progress).groupby("Code")["Done Qty"].sum().reset_index()
        status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    
    status["Done Value"] = (status["Done Qty"] * status["Unit Rate"])
    status["Total Value"] = (status["Total Qty"] * status["Unit Rate"])
    status["% Progress"] = (status["Done Qty"] / status["Total Qty"] * 100).round(2)
    return status

def get_stock():
    in_fuel = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    out_fuel = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
    return st.session_state.opening_stock + in_fuel - out_fuel

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL SECURE PROJECT ERP v7.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">BHAIYALAL INFRASTRUCTURE PVT. LTD. | ANUPPUR RESERVOIR PROJECT (58.09 CR.)</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("👤 User: Admin")
    status_df = calculate_status()
    total_val = status_df["Total Value"].sum()
    billed_val = status_df["Done Value"].sum()
    
    st.metric("Total Project Value", f"Rs. {total_val/10000000:.2f} Cr")
    st.metric("Total Certified (Billing)", f"Rs. {billed_val/100000:.2f} L")
    st.progress(float(billed_val/total_val) if total_val > 0 else 0.0)
    
    st.write("---")
    st.metric("Current Diesel Stock", f"{get_stock():,.2f} L")
    
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Financial Dashboard", "🚧 Work Progress", "👷 Manpower", "🚜 Diesel & Machine", "🛠️ Database"])

# --- TAB 1: DASHBOARD ---
with tab1:
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Financial Progress Status")
        st.dataframe(status_df[["Code", "Item", "Total Qty", "Done Qty", "Done Value", "% Progress"]], use_container_width=True)
    with col2:
        st.subheader("Billing Trends (Work Done Value)")
        st.bar_chart(status_df.set_index("Item")["Done Value"])
    
    st.write("---")
    st.subheader("Daily Snapshot")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Today's Manpower", sum([m['Staff']+m['Operators']+m['Skilled']+m['Unskilled'] for m in st.session_state.manpower_log[-1:]]))
    with c2: st.metric("Today's Excavation (CuM)", sum([p['Done Qty'] for p in st.session_state.boq_progress if p['Date'] == datetime.now().strftime('%Y-%m-%d') and p['Code'] == '30a']))
    with c3: st.metric("Project Health", "On Track ✅", delta="Stable")

# --- TAB 2: PROGRESS LOG ---
with tab2:
    st.subheader("Daily Progress Report (DPR)")
    c1, c2, c3 = st.columns(3)
    with c1:
        p_date = st.date_input("DATED", datetime.now())
        p_item = st.selectbox("Select Item", st.session_state.boq_master["Item"].tolist())
    with c2:
        p_qty = st.number_input(f"Today's Work Quantity", min_value=0.0)
        p_rate = st.session_state.boq_master[st.session_state.boq_master["Item"] == p_item]["Unit Rate"].values[0]
        st.info(f"Unit Rate: Rs. {p_rate} | Work Value: Rs. {p_qty * p_rate:,.2f}")
    with c3:
        p_rem = st.text_input("Remarks", placeholder="Chainage / Location")
    
    if st.button("➕ Save Work Log", type="primary", use_container_width=True):
        code = st.session_state.boq_master[st.session_state.boq_master["Item"] == p_item]["Code"].values[0]
        st.session_state.boq_progress.append({"Date": p_date.strftime("%Y-%m-%d"), "Code": code, "Item": p_item, "Done Qty": p_qty, "Remark": p_rem})
        st.success("Entry Saved!"); st.rerun()

# --- TAB 3: MANPOWER ---
with tab3:
    st.subheader("Daily Manpower Tracking")
    m1, m2, m3 = st.columns(3)
    with m1: ms = st.number_input("Staff", 15); mo = st.number_input("Operators", 20)
    with m2: mk = st.number_input("Skilled", 2); mu = st.number_input("Unskilled", 4)
    with m3: my = st.number_input("Security", 2)
    
    if st.button("👷 Log Manpower", use_container_width=True):
        st.session_state.manpower_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Staff": ms, "Operators": mo, "Skilled": mk, "Unskilled": mu, "Security": my})
        st.success("Manpower Data Logged!"); st.rerun()

# --- TAB 4: DIESEL ---
with tab4:
    st.subheader("Machinery & Fuel Control")
    d1, d2 = st.tabs(["Diesel Log", "Snapshot"])
    with d1:
        c1, c2 = st.columns(2)
        with c1: dm_machine = st.selectbox("Machine NO", st.session_state.machine_master["MACHINE NO"].tolist())
        with c2: dm_fill = st.number_input("FILL HSD (L)", min_value=0.0)
        if st.button("➕ Save Fuel Issue"):
            st.session_state.consumption_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "MACHINE NO": dm_machine, "FILL HSD": dm_fill})
            st.success("HSD Logged!"); st.rerun()

# --- TAB 5: DATABASE ---
with tab5:
    st.subheader("🛠️ Professional Master Setup")
    d_boq, d_mm = st.tabs(["Financial BOQ", "Machine Master"])
    with d_boq:
        st.write("Configure Item Rates (for 58.09 Cr Project)")
        e_boq = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Financial Master"): st.session_state.boq_master = e_boq; st.success("Master Updated!"); st.rerun()
    with d_mm:
        e_mm = st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Machine Master"): st.session_state.machine_master = e_mm; st.success("Machines Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL SECURE PROJECT ERP v7.0</b><br>
        Bhaiyalal Infrastructure Pvt. Ltd. | Developed by: Upendra Singh<br>
        Copyright © 2026 Anuppur Reservoir Project
    </div>
""", unsafe_allow_html=True)
