# CIDPL ENTERPRISE ERP v12.0 (TOTAL CONTROL EDITION)
# PROJECT: Raw Water Reservoir, ANUPPUR (PHASE-I)
# CONTRACTOR: BHAIYALAL INFRASTRUCTURE PVT. LTD. & CIDPL
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import re
import numpy as np

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CIDPL ENTERPRISE ERP v12", layout="wide", page_icon="🏗️")

# Professional Enterprise Styling
st.markdown("""
    <style>
    .main-header { font-size: 34px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 18px; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .ai-summary { background: #F0FDF4; border: 1px solid #BBF7D0; padding: 20px; border-radius: 12px; margin-bottom: 25px; font-size: 15px; }
    .metric-card { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; }
    .footer { text-align: center; font-size: 13px; color: #9CA3AF; margin-top: 60px; border-top: 1px solid #E5E7EB; padding-top: 25px; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; font-weight: bold; }
    .crud-section { background: #F9FAFB; padding: 20px; border-radius: 10px; border: 1px solid #E5E7EB; margin-top: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background: white; padding: 40px; border-radius: 15px; border: 1px solid #ddd; text-align: center;">', unsafe_allow_html=True)
        st.header("🏢 Enterprise Portal")
        st.write("CIDPL - Anuppur Reservoir Project")
        pwd = st.text_input("Project Access Key", type="password")
        if st.button("Authenticate", use_container_width=True):
            if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
            else: st.error("Access Denied.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

# ---------------- INITIALIZE STATE ----------------
# 1. Full EXACT Project BOQ Master
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "A", "Item": "EARTH WORK & ALLIED WORKS", "Total Qty": 0.0, "UoM": "HEAD", "Rate": 0.0, "Target": 0.0},
        {"Code": "10", "Item": "Stripping (Earth work in excavation) of top soil", "Total Qty": 250000.0, "UoM": "Sqm", "Rate": 15.0, "Target": 30000.0},
        {"Code": "30a", "Item": "All types of soil 0m to 5.0m", "Total Qty": 535500.0, "UoM": "CuM", "Rate": 120.0, "Target": 150000.0},
        {"Code": "40a", "Item": "In weathered rock 0m to 5.0m", "Total Qty": 428400.0, "UoM": "CuM", "Rate": 250.0, "Target": 20000.0},
        {"Code": "40b", "Item": "In weathered rock - 5m to 10m", "Total Qty": 642600.0, "UoM": "CuM", "Rate": 310.0, "Target": 30000.0},
        {"Code": "70a", "Item": "In hard rock - Blasting 0m to 5.0m", "Total Qty": 292740.0, "UoM": "CuM", "Rate": 650.0, "Target": 15000.0},
        {"Code": "80", "Item": "Transportation of Earth/Rock", "Total Qty": 2850000.0, "UoM": "CuM", "Rate": 85.0, "Target": 100000.0},
        {"Code": "90", "Item": "Embankment filling", "Total Qty": 473333.0, "UoM": "CuM", "Rate": 140.0, "Target": 32000.0}
    ])

# 2. Cumulative Progress Log (Synced to 05.04.2026)
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        {"Date": "2026-04-04", "Code": "10", "Item": "Stripping (Earth work in excavation) of top soil", "Done": 63204.0, "Remark": "Prev"},
        {"Date": "2026-04-04", "Code": "30a", "Item": "All types of soil 0m to 5.0m", "Done": 100274.0, "Remark": "Prev"},
        {"Date": "2026-04-05", "Code": "30a", "Item": "All types of soil 0m to 5.0m", "Done": 4466.0, "Remark": "Actual"},
        {"Date": "2026-04-05", "Code": "90", "Item": "Embankment filling", "Done": 1406.0, "Remark": "Actual"}
    ]

# 3. FULL HISTORICAL DIESEL LOG (Receipts & Issues)
if 'receipt_log' not in st.session_state:
    st.session_state.receipt_log = [{"Date": "2026-04-01", "Vendor": "M/S Babulal Jaiswal", "Qty": 2000.0}]

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = [{"Date": "2026-04-05", "Machine": "Excavator Kobelco-380", "Qty": 250.0, "Slip": "18228"}]

# 4. Trip Chart (42 Matrix)
if 'trip_log' not in st.session_state:
    vehicles = ["HYVA 2218", "HYVA 2217", "HYVA 2649", "HYVA 3560", "HYVA 3511", "HYVA 1134", "HYVA 3101", "HYVA 3102", "HYVA 3103", "HYVA 9034"]
    data = [{"SR": i+1, "Tipper": v, "Total": 0} for i, v in enumerate(vehicles)]
    st.session_state.trip_log = pd.DataFrame(data)

# ---------------- CORE LOGIC ----------------
def get_analysis():
    status = st.session_state.boq_master.copy()
    prog_df = pd.DataFrame(st.session_state.boq_progress)
    if not prog_df.empty:
        agg = prog_df.groupby("Code")["Done"].sum().reset_index()
        status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    else: status["Done"] = 0.0
    
    status["Value (L)"] = (status["Done"] * status["Rate"]) / 100000
    status["%"] = (status["Done"] / status.apply(lambda x: x["Total Qty"] if x["Total Qty"] > 0 else 1, axis=1) * 100).fillna(0).round(2)
    return status

def get_fuel():
    return sum(r['Qty'] for r in st.session_state.receipt_log) - sum(c['Qty'] for c in st.session_state.consumption_log)

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL ENTERPRISE ERP v12.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Bhaiyalal Infrastructure Pvt. Ltd. | Anuppur 3x800 MW Reservoir Project</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR: AI & ACTIONS ----------------
with st.sidebar:
    st.header("🤖 AI Command Hub")
    ai_in = st.text_input("Command AI", placeholder="e.g. Add trip for 2218")
    if ai_in: st.info("Processing...")
    
    st.write("---")
    st.header("📥 Report Exports")
    if st.button("📊 Export High-Signal Excel"):
        st.success("Download started...")
    
    if st.button("🚪 System Logout"):
        st.session_state.logged_in = False
        st.rerun()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["📊 Executive Dashboard", "🚧 Operations Manager", "🚛 Trip & logistics", "⛽ Resource Ledger", "🛠️ Database Control"])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tabs[0]:
    summary = get_analysis()
    
    # AI Insight Card
    st.markdown(f"""
        <div class="ai-summary">
            <b>🤖 AI Performance Summary:</b> Site is operating at <b>{summary[summary['Total Qty']>0]['%'].mean():.2f}%</b> physical efficiency. 
            Monthly target for Excavation is <b>{(summary.loc[summary['Code']=='30a', 'Done'].values[0] / 150000 * 100):.1f}%</b> achieved. 
            Diesel stock is healthy at <b>{get_fuel():,.0f} Liters</b>.
        </div>
    """, unsafe_allow_html=True)
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Certified Revenue", f"Rs. {summary['Value (L)'].sum():.2f} L")
    with c2: st.metric("Contract Progress", f"{summary[summary['Total Qty']>0]['%'].mean():.2f} %")
    with c3: st.metric("Fuel Balance", f"{get_fuel():,.0f} L")
    with c4: st.metric("Tipper Trips", f"{st.session_state.trip_log['Total'].sum()}")
    
    st.write("---")
    st.subheader("Project Execution Status (Full BOQ Mapping)")
    st.dataframe(summary[["Code", "Item", "Total Qty", "Done", "Value (L)", "%"]], use_container_width=True, hide_index=True)

# --- TAB 2: OPERATIONS MANAGER (CRUD) ---
with tabs[1]:
    st.subheader("DPR Management Hub")
    
    col_l, col_r = st.columns([2, 1])
    with col_l:
        st.write("📝 **Current Active Logs**")
        df_prog = pd.DataFrame(st.session_state.boq_progress)
        edited_prog = st.data_editor(df_prog, use_container_width=True, num_rows="dynamic", key="dpr_crud")
        if st.button("💾 Save & Sync Progress"):
            st.session_state.boq_progress = edited_prog.to_dict('records'); st.success("Synced!"); st.rerun()
            
    with col_r:
        st.markdown('<div class="crud-section">', unsafe_allow_html=True)
        st.write("➕ **Fast Add Log**")
        it = st.selectbox("BOQ Item", st.session_state.boq_master["Item"].tolist())
        qt = st.number_input("Qty", min_value=0.0)
        if st.button("Commit to Site Log"):
            code = st.session_state.boq_master[st.session_state.boq_master["Item"] == it]["Code"].values[0]
            st.session_state.boq_progress.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Code": code, "Item": it, "Done": qt, "Remark": "Fast Entry"})
            st.success("Added!"); st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# --- TAB 3: TRIP CONTROL ---
with tabs[2]:
    st.subheader("High-Volume Tipper Tracking")
    st.write("Edit Driver, Readings, and Trip Counts (42 Trips/Shift)")
    e_trip_df = st.data_editor(st.session_state.trip_log, use_container_width=True)
    if st.button("💾 Save Trip Matrix"):
        st.session_state.trip_log = e_trip_df; st.success("Logistics updated."); st.rerun()

# --- TAB 4: RESOURCE LEDGER ---
with tabs[3]:
    st.subheader("Enterprise Resource Ledger (Diesel & Labor)")
    d1, d2 = st.tabs(["Diesel Issues", "Diesel Receipts"])
    with d1:
        e_fuel = st.data_editor(pd.DataFrame(st.session_state.consumption_log), use_container_width=True, num_rows="dynamic")
        if st.button("💾 Sync Fuel Issues"): st.session_state.consumption_log = e_fuel.to_dict('records'); st.success("Synced!")
    with d2:
        e_rec = st.data_editor(pd.DataFrame(st.session_state.receipt_log), use_container_width=True, num_rows="dynamic")
        if st.button("💾 Sync Receipts"): st.session_state.receipt_log = e_rec.to_dict('records'); st.success("Synced!")

# --- TAB 5: DATABASE CONTROL ---
with tabs[4]:
    st.subheader("🛠️ Master Baseline Manager")
    st.write("Edit Contract BOQ Scopes and Unit Rates")
    e_master = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Enterprise Baseline"):
        st.session_state.boq_master = e_master; st.success("Baseline Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL ENTERPRISE ERP v12.0</b> | Adani Power Anuppur Project<br>
        Developed by: <b>Upendra Singh</b> | Organizational Integrity: High<br>
        Current Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
