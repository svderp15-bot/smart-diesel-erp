# CIDPL FULL RESERVOIR ERP (DPR-05.04.2026 EDITION)
# PROJECT: Raw Water Reservoir, ANUPPUR (BHAIYALAL INFRASTRUCTURE PVT. LTD.)
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

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
# --- 1. BOQ MASTER DATA (Updated Scopes) ---
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil)", "Total Qty": 125000.0, "UoM": "Sqm", "Planned Target (Month)": 30000.0},
        {"Code": "20", "Item": "Excavation (All types)", "Total Qty": 1700000.0, "UoM": "CuM", "Planned Target (Month)": 150000.0},
        {"Code": "90", "Item": "Embankment Layer Filling", "Total Qty": 473333.0, "UoM": "CuM", "Planned Target (Month)": 32000.0},
        {"Code": "120", "Item": "1000 micron HDPE Sheet", "Total Qty": 444803.0, "Sqm": "Sqm", "Planned Target (Month)": 42000.0},
        {"Code": "130", "Item": "Cement concrete liner (75mm)", "Total Qty": 163000.0, "UoM": "Sqm", "Planned Target (Month)": 15000.0}
    ])

# --- 2. BOQ PROGRESS LOG (Pre-loaded with DPR 05.04.2026) ---
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        # Cumulative Progress before 05.04.2026
        {"Date": "2026-04-04", "Code": "10", "Item": "Stripping (top soil)", "Done Qty": 63204.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "20", "Item": "Excavation (All types)", "Done Qty": 100274.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 91693.0, "Remark": "PREV. CUMULATIVE"},
        # Today's Work 05.04.2026
        {"Date": "2026-04-05", "Code": "10", "Item": "Stripping (top soil)", "Done Qty": 0.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "20", "Item": "Excavation (All types)", "Done Qty": 4466.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 1406.0, "Remark": "DPR Entry"}
    ]

# --- 3. MANPOWER LOG ---
if 'manpower_log' not in st.session_state:
    st.session_state.manpower_log = [
        {"Date": "2026-04-05", "Staff": 15, "Operators": 20, "Skilled": 2, "Unskilled": 4, "Security": 2}
    ]

# --- 4. SITE SNAPSHOT (Machinery Count) ---
if 'site_snapshot' not in st.session_state:
    st.session_state.site_snapshot = [
        {"Date": "2026-04-05", "Excavator": 6, "Dumper": 20, "Road Roller": 2, "Diesel Tanker": 1, "Grader": 2, "Dozer": 2, "Drilling Machine": 5, "Water Tanker": 4, "DG": 1}
    ]

# --- 5. DIESEL & MACHINERY ---
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

def to_excel(df_list, sheet_names):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for df, name in zip(df_list, sheet_names):
            df.to_excel(writer, sheet_name=name, index=False)
    return output.getvalue()

# ---------------- BRANDING ----------------
st.markdown('<div class="main-header">CIDPL RESERVOIR ERP & DPR SYSTEM</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">PROJECT: Raw Water Reservoir, ANUPPUR | UPDATED DPR: 05.04.2026</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🏢 Project Overview")
    status_df = calculate_boq_status()
    total_progress = status_df["% Complete"].mean()
    st.metric("Avg. Project Progress", f"{total_progress:.2f} %")
    
    diesel_st = calculate_diesel_stock()
    st.metric("Current HSD Stock", f"{diesel_st:,.2f} L")
    
    st.write("---")
    st.header("👷 Manpower Today")
    mp = st.session_state.manpower_log[-1] if st.session_state.manpower_log else {}
    if mp:
        st.write(f"Staff: **{mp['Staff']}** | Operators: **{mp['Operators']}**")
        st.write(f"Skilled: **{mp['Skilled']}** | Labor: **{mp['Unskilled']}**")
    
    st.write("---")
    if st.button("📥 Export Final DPR Report"):
        data_list = [status_df, pd.DataFrame(st.session_state.boq_progress), pd.DataFrame(st.session_state.manpower_log), pd.DataFrame(st.session_state.site_snapshot)]
        sheet_names = ['BOQ_Status', 'Daily_Progress', 'Manpower_Log', 'Machinery_Count']
        data_xl = to_excel(data_list, sheet_names)
        st.download_button(label="💾 Download DPR", data=data_xl, file_name=f"DPR_ANUPPUR_{datetime.now().strftime('%Y%m%d')}.xlsx")

# ---------------- TABS ----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📊 Dashboard", "🚧 Work Progress", "👷 Manpower", "🚜 Diesel & Machine", "🛠️ Database"])

# --- TAB 1: DASHBOARD ---
with tab1:
    st.subheader("Bill of Quantities (BOQ) Summary Status")
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Physical Progress (%)")
        st.bar_chart(status_df.set_index("Item")["% Complete"])
    with col2:
        st.subheader("Machinery on Site (Latest)")
        if st.session_state.site_snapshot:
            snap = st.session_state.site_snapshot[-1]
            st.json(snap)

# --- TAB 2: BOQ PROGRESS LOG ---
with tab2:
    st.subheader("Log Daily Work Progress")
    col1, col2, col3 = st.columns(3)
    with col1:
        p_date = st.date_input("Work Date", datetime.now())
        p_item = st.selectbox("Select BOQ Item", st.session_state.boq_master["Item"].tolist())
    with col2:
        p_code = st.session_state.boq_master[st.session_state.boq_master["Item"] == p_item]["Code"].values[0]
        p_qty = st.number_input(f"Today's Quantity", min_value=0.0)
    with col3:
        p_rem = st.text_input("Remarks", placeholder="e.g., North Slope")

    if st.button("➕ Save Work Entry", type="primary", use_container_width=True):
        entry = {"Date": p_date.strftime("%Y-%m-%d"), "Code": p_code, "Item": p_item, "Done Qty": p_qty, "Remark": p_rem}
        st.session_state.boq_progress.append(entry)
        st.success(f"Log Saved for {p_item}!"); st.rerun()

# --- TAB 3: MANPOWER ---
with tab3:
    st.subheader("Log Daily Manpower Deployment")
    m1, m2, m3 = st.columns(3)
    with m1:
        m_date = st.date_input("Report Date", datetime.now(), key="mp_date")
        m_staff = st.number_input("Staff (Engr. & Sup.)", value=15)
    with m2:
        m_ops = st.number_input("Operators/Drivers", value=20)
        m_skilled = st.number_input("Skilled Labor", value=2)
    with m3:
        m_unskilled = st.number_input("Unskilled Labor", value=4)
        m_sec = st.number_input("Security", value=2)

    if st.button("➕ Save Manpower Log", use_container_width=True):
        st.session_state.manpower_log.append({
            "Date": m_date.strftime("%Y-%m-%d"), "Staff": m_staff, "Operators": m_ops, 
            "Skilled": m_skilled, "Unskilled": m_unskilled, "Security": m_sec
        })
        st.success("Manpower Data Logged!"); st.rerun()
    
    st.write("---")
    st.write("**Recent Manpower History**")
    st.dataframe(pd.DataFrame(st.session_state.manpower_log).tail(10), use_container_width=True)

# --- TAB 4: DIESEL & MACHINE ---
with tab4:
    st.subheader("HSD Management & Machinery Snapshot")
    h1, h2 = st.tabs(["Diesel Issue", "Machinery Count"])
    
    with h1:
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

    with h2:
        st.write("Update Machinery Deployment Count on Site")
        s1, s2, s3 = st.columns(3)
        with s1:
            s_ex = st.number_input("Excavators", 6); s_dum = st.number_input("Dumpers", 20)
        with s2:
            s_rr = st.number_input("Road Rollers", 2); s_dt = st.number_input("Diesel Tanker", 1)
        with s3:
            s_wt = st.number_input("Water Tanker", 4); s_dg = st.number_input("DG Sets", 1)
        
        if st.button("📸 Update Snapshot"):
            st.session_state.site_snapshot.append({
                "Date": datetime.now().strftime("%Y-%m-%d"), "Excavator": s_ex, "Dumper": s_dum, 
                "Road Roller": s_rr, "Diesel Tanker": s_dt, "Water Tanker": s_wt, "DG": s_dg
            })
            st.success("Snapshot Updated!"); st.rerun()

# --- TAB 5: DATABASE ---
with tab5:
    st.subheader("🛠️ System Data Control")
    d1, d2 = st.tabs(["BOQ Master", "Machine Master"])
    with d1:
        st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
    with d2:
        st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL SMART DPR ERP v6.0</b><br>
        Developed by: <b>Upendra Singh</b><br>
        Project: Anuppur Phase-I Reservoir | Updated: 05.04.2026
    </div>
""", unsafe_allow_html=True)
