# CIDPL FULL RESERVOIR ERP (PHASE-I)
# PROJECT: Raw Water Reservoir, ANUPPUR (BHAIYALAL INFRASTRUCTURE PVT. LTD.)
# AUTHOR: UPENDRA SINGH | CONTRACTOR: CIDPL & BHAIYALAL INFRA

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import re

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CIDPL FULL ERP", layout="wide", page_icon="🏗️")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-header { font-size: 28px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .footer { text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; }
    .metric-container { background: white; border: 1px solid #E5E7EB; padding: 10px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE STATE ----------------
# --- 1. BOQ MASTER DATA ---
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil)", "Total Qty": 250000.0, "UoM": "Sqm", "Planned Target (Month)": 30000.0},
        {"Code": "30a", "Item": "Earthwork excavation soil (0-5m)", "Total Qty": 535500.0, "UoM": "CuM", "Planned Target (Month)": 40000.0},
        {"Code": "40a", "Item": "Weathered rock excavation (0-5m)", "Total Qty": 428400.0, "UoM": "CuM", "Planned Target (Month)": 20000.0},
        {"Code": "40b", "Item": "Weathered rock excavation (5-10m)", "Total Qty": 642600.0, "UoM": "CuM", "Planned Target (Month)": 25000.0},
        {"Code": "70a", "Item": "Hard rock - Blasting (0-5m)", "Total Qty": 292740.0, "UoM": "CuM", "Planned Target (Month)": 15000.0},
        {"Code": "80", "Item": "Transportation of Earth/Rock", "Total Qty": 2850000.0, "UoM": "CuM", "Planned Target (Month)": 89000.0},
        {"Code": "90", "Item": "Embankment filling", "Total Qty": 473333.0, "UoM": "CuM", "Planned Target (Month)": 32000.0},
        {"Code": "120", "Item": "1000 micron HDPE Sheet", "Total Qty": 444803.0, "UoM": "Sqm", "Planned Target (Month)": 42000.0},
        {"Code": "130", "Item": "Cement concrete liner (75mm)", "Total Qty": 163000.0, "UoM": "Sqm", "Planned Target (Month)": 15000.0}
    ])

# --- 2. BOQ PROGRESS LOG ---
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = []

# --- 3. DIESEL & MACHINERY (Carried Forward) ---
if 'machine_master' not in st.session_state:
    st.session_state.machine_master = pd.DataFrame([
        {"MACHINE NO": "EX KOBEELCO 380", "TYPE": "EXCAVATOR", "AVG": 22.5},
        {"MACHINE NO": "EX KOMATSU 300", "TYPE": "EXCAVATOR", "AVG": 20.0},
        {"MACHINE NO": "HYVA 2218", "TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "TRACTOR WT 9785", "TYPE": "WATER TANKER", "AVG": 4.0}
    ])

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = []

if 'receipt_log' not in st.session_state:
    st.session_state.receipt_log = []

if 'opening_stock' not in st.session_state:
    st.session_state.opening_stock = 10000.0

# ---------------- CORE LOGIC ----------------
def calculate_boq_status():
    if not st.session_state.boq_progress:
        df = st.session_state.boq_master.copy()
        df["Done Qty"] = 0.0
        df["Remaining Qty"] = df["Total Qty"]
        df["% Complete"] = 0.0
        return df
    
    prog_df = pd.DataFrame(st.session_state.boq_progress)
    agg = prog_df.groupby("Code")["Done Qty"].sum().reset_index()
    
    status = pd.merge(st.session_state.boq_master, agg, on="Code", how="left").fillna(0)
    status["Remaining Qty"] = status["Total Qty"] - status["Done Qty"]
    status["% Complete"] = (status["Done Qty"] / status["Total Qty"] * 100).round(2)
    return status

def calculate_diesel_stock():
    total_received = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    total_issued = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
    return st.session_state.opening_stock + total_received - total_issued

# ---------------- BRANDING ----------------
st.markdown('<div class="main-header">CIDPL-BHAIYALAL RESERVOIR ERP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">PROJECT: CONSTRUCTION OF RAW WATER RESERVOIR, ANUPPUR (PHASE-I) | COST: 58.09 CR.</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🏢 Project Overview")
    status_df = calculate_boq_status()
    total_progress = status_df["% Complete"].mean()
    st.metric("Overall Project Progress", f"{total_progress:.2f} %")
    
    diesel_st = calculate_diesel_stock()
    st.metric("Current HSD Stock", f"{diesel_st:,.2f} L")
    
    st.write("---")
    st.markdown("<b>🤖 CIDPL Assistant</b><br>Type: 'Stripping done 5000' or 'EX KOBELCO fill 200'", unsafe_allow_html=True)
    ai_in = st.text_input("Smart Entry (AI)", placeholder="Quick log here...")
    
    st.write("---")
    if st.button("📥 Export Full ERP Report"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            status_df.to_excel(writer, sheet_name='BOQ_Status', index=False)
            pd.DataFrame(st.session_state.boq_progress).to_excel(writer, sheet_name='BOQ_History', index=False)
            pd.DataFrame(st.session_state.consumption_log).to_excel(writer, sheet_name='Diesel_Log', index=False)
        st.download_button(label="💾 Download Final Excel", data=output.getvalue(), file_name=f"ANUPPUR_RESERVOIR_ERP_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["📊 Dashboard", "🚧 BOQ Progress", "🚜 Diesel & Machine", "🛠️ Master Setup"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.subheader("Bill of Quantities (BOQ) Summary Status")
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    # Progress Chart (Simple)
    st.write("---")
    st.subheader("Physical Progress Tracking")
    st.bar_chart(status_df.set_index("Item")["% Complete"])

# --- TAB 2: BOQ PROGRESS LOG ---
with tab2:
    st.subheader("Add Daily Work Progress")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_date = st.date_input("Work Date", datetime.now())
        p_item = st.selectbox("Select BOQ Item", st.session_state.boq_master["Item"].tolist())
    with col2:
        p_code = st.session_state.boq_master[st.session_state.boq_master["Item"] == p_item]["Code"].values[0]
        p_qty = st.number_input(f"Quantity Done ({st.session_state.boq_master[st.session_state.boq_master['Item'] == p_item]['UoM'].values[0]})", min_value=0.0)
    with col3:
        p_rem = st.text_input("Progress Remarks", placeholder="Section A / North Face")

    if st.button("➕ Save Work Entry", type="primary", use_container_width=True):
        entry = {"Date": p_date.strftime("%Y-%m-%d"), "Code": p_code, "Item": p_item, "Done Qty": p_qty, "Remark": p_rem}
        st.session_state.boq_progress.append(entry)
        st.success(f"Progress recorded for {p_item}!"); st.rerun()

# --- TAB 3: DIESEL & MACHINE ---
with tab3:
    st.subheader("HSD Management (Anuppur Project)")
    d_tab1, d_tab2 = st.tabs(["Issue Log", "Stock Receipt"])
    
    with d_tab1:
        c1, c2, c3 = st.columns(3)
        with c1:
            dm_machine = st.selectbox("Machine NO", st.session_state.machine_master["MACHINE NO"].tolist())
            dm_curr = st.number_input("Current Reading", min_value=0.0)
        with c2:
            dm_fill = st.number_input("FILL HSD (L)", min_value=0.0)
        with c3:
            dm_rem = st.text_input("Diesel Remark")
        
        if st.button("➕ Save Diesel Entry"):
            # Fetch PRV
            prv = 0.0
            if st.session_state.consumption_log:
                df_temp = pd.DataFrame(st.session_state.consumption_log)
                m_data = df_temp[df_temp["MACHINE NO"] == dm_machine]
                if not m_data.empty: prv = float(m_data.iloc[-1]["CURRENT READING"])
            
            st.session_state.consumption_log.append({
                "Date": datetime.now().strftime("%Y-%m-%d"), "MACHINE NO": dm_machine, "PRV.READING": prv, 
                "CURRENT READING": dm_curr, "FILL HSD": dm_fill, "Remarks": dm_rem
            })
            st.success("Diesel Log Saved!"); st.rerun()

# --- TAB 4: MASTER SETUP ---
with tab4:
    st.subheader("🛠️ Database Setup")
    m_tab1, m_tab2 = st.tabs(["BOQ Master", "Machine Master"])
    
    with m_tab1:
        st.write("Edit the 58.09 Cr. BOQ List below:")
        edited_boq = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Update BOQ"):
            st.session_state.boq_master = edited_boq; st.success("BOQ Database Updated!")

    with m_tab2:
        edited_mm = st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Update Machines"):
            st.session_state.machine_master = edited_mm; st.success("Machine List Updated!")

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL FULL PROJECT ERP v5.0</b><br>
        Developed by: <b>Upendra Singh</b><br>
        Anuppur Phase-I Raw Water Reservoir Project (58.09 Cr.)
    </div>
""", unsafe_allow_html=True)
