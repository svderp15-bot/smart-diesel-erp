# CIDPL ADVANCED PROJECT ERP v10.0 (MEGA RE-UPDATE)
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
st.set_page_config(page_title="CIDPL ADVANCED ERP", layout="wide", page_icon="🏗️")

# Custom CSS for Professional Branding and Colorful Dashboard
st.markdown("""
    <style>
    .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .card-green { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-weight: bold; }
    .card-blue { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-weight: bold; }
    .card-amber { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-weight: bold; }
    .card-red { background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; box-shadow: 0 4px 10px rgba(0,0,0,0.1); font-weight: bold; }
    .footer { text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .login-box { max-width: 450px; margin: auto; padding: 50px; border: 1px solid #E5E7EB; border-radius: 15px; background: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1); text-align: center; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; font-weight: bold; border-radius: 8px 8px 0px 0px; }
    .stTabs [data-baseweb="tab"] { height: 50px; padding: 10px 20px; background-color: #f3f4f6; border-radius: 8px 8px 0px 0px; margin-right: 4px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.image("https://cdn-icons-png.flaticon.com/512/3135/3135715.png", width=100)
    st.header("🔐 CIDPL ERP v10.0")
    st.write("Anuppur Reservoir Project Phase-I")
    pwd = st.text_input("Enter Project Password", type="password")
    if st.button("Access Dashboard", use_container_width=True):
        if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
        else: st.error("Invalid Access Key.")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

# ---------------- INITIALIZE STATE ----------------
# 1. Full Project BOQ Master (From 58.09 Cr Scope)
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil) - 2.5L sqm", "Total Qty": 125000.0, "UoM": "Sqm", "Rate": 15.0},
        {"Code": "30a", "Item": "Earthwork excavation 0-5m", "Total Qty": 1700000.0, "UoM": "CuM", "Rate": 120.0},
        {"Code": "40a", "Item": "Weathered rock 0-5m", "Total Qty": 214200.0, "UoM": "CuM", "Rate": 250.0},
        {"Code": "40b", "Item": "Weathered rock 5-10m", "Total Qty": 321300.0, "UoM": "CuM", "Rate": 310.0},
        {"Code": "70a", "Item": "Hard rock Blasting 0-5m", "Total Qty": 146370.0, "UoM": "CuM", "Rate": 650.0},
        {"Code": "80", "Item": "Transportation extra", "Total Qty": 1425000.0, "UoM": "CuM", "Rate": 85.0},
        {"Code": "90", "Item": "Embankment Layer Filling", "Total Qty": 236667.0, "UoM": "CuM", "Rate": 140.0},
        {"Code": "120", "Item": "1000 micron HDPE Sheet", "Total Qty": 222402.0, "UoM": "Sqm", "Rate": 350.0},
        {"Code": "130", "Item": "Cement concrete liner 75mm", "Total Qty": 81500.0, "UoM": "Sqm", "Rate": 450.0}
    ])

# 2. Cumulative Progress Log (Synced to 05.04.2026)
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        {"Date": "2026-04-04", "Code": "10", "Item": "Stripping (top soil) - 2.5L sqm", "Done Qty": 63204.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "30a", "Item": "Earthwork excavation 0-5m", "Done Qty": 100274.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 91693.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-05", "Code": "10", "Item": "Stripping (top soil) - 2.5L sqm", "Done Qty": 0.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "30a", "Item": "Earthwork excavation 0-5m", "Done Qty": 4466.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 1406.0, "Remark": "DPR Entry"}
    ]

# 3. Trip Chart Module (SR 1-10 HYVAs, 42 Trips)
if 'trip_log' not in st.session_state:
    cols = ["SR", "Tipper", "Driver", "Start Reading", "Closed Reading", "HMR"] + [f"T-{i}" for i in range(1, 43)] + ["Total"]
    vehicles = ["HYVA 2218", "HYVA 2217", "HYVA 2649", "HYVA 3560", "HYVA 3511", "HYVA 1134", "HYVA 3101", "HYVA 3102", "HYVA 3103", "HYVA 9034"]
    data = []
    for i, v in enumerate(vehicles):
        row = {c: 0 for c in cols}; row["SR"] = i + 1; row["Tipper"] = v; row["Driver"] = f"Driver {i+1}"; row["Total"] = 0
        data.append(row)
    st.session_state.trip_log = pd.DataFrame(data)

# 4. Manpower & Machine Counts
if 'manpower_log' not in st.session_state: st.session_state.manpower_log = [{"Date": "2026-04-05", "Staff": 15, "Operators": 20, "Skilled": 2, "Unskilled": 4, "Security": 2}]
if 'site_snapshot' not in st.session_state: st.session_state.site_snapshot = [{"Date": "2026-04-05", "Excavator": 6, "Dumper": 20, "Road Roller": 2, "Drilling": 5, "Water Tanker": 4}]

# 5. Diesel Log
if 'consumption_log' not in st.session_state: st.session_state.consumption_log = []
if 'receipt_log' not in st.session_state: st.session_state.receipt_log = []
if 'opening_stock' not in st.session_state: st.session_state.opening_stock = 15000.0

# ---------------- CORE LOGIC ----------------
def get_status():
    status = st.session_state.boq_master.copy()
    if st.session_state.boq_progress:
        agg = pd.DataFrame(st.session_state.boq_progress).groupby("Code")["Done Qty"].sum().reset_index()
        status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    else: status["Done Qty"] = 0.0
    status["Value"] = status["Done Qty"] * status["Rate"]
    status["Total Val"] = status["Total Qty"] * status["Rate"]
    status["%"] = (status["Done Qty"] / status["Total Qty"] * 100).round(2)
    return status

def get_fuel():
    return st.session_state.opening_stock + sum(r['Qty (L)'] for r in st.session_state.receipt_log) - sum(c['FILL HSD'] for c in st.session_state.consumption_log)

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL-BHAIYALAL PROJECT ERP v10.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">RAW WATER RESERVOIR | ANUPPUR 3X800 MW | BHAIYALAL INFRASTRUCTURE PVT. LTD.</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🏢 Site Command")
    status_df = get_status()
    billed = status_df["Value"].sum(); total_v = status_df["Total Val"].sum()
    st.markdown(f'<div class="card-blue">Financial Progress<br>Rs. {billed/100000:.2f} L / {total_v/10000000:.2f} Cr</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.header("📥 Report Center")
    rep_period = st.radio("Report Basis", ["Daily DPR", "Weekly Report", "Monthly Report"])
    if st.button("📊 Export Excel (Colorful)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            status_df.to_excel(writer, sheet_name='Summary', index=False)
            pd.DataFrame(st.session_state.boq_progress).to_excel(writer, sheet_name='Progress_Logs', index=False)
            st.session_state.trip_log.to_excel(writer, sheet_name='Trip_Chart', index=False)
            workbook = writer.book; header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
            for worksheet in writer.sheets.values():
                for col_num, value in enumerate(status_df.columns.values): worksheet.write(0, col_num, value, header_fmt)
        st.download_button(label=f"💾 Download {rep_period}", data=output.getvalue(), file_name=f"CIDPL_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")

    st.write("---")
    st.markdown("<b>🤖 Local AI Assistant</b>", unsafe_allow_html=True)
    ai_msg = st.text_input("Talk to ERP", placeholder="e.g., Stripping done 5000")
    if ai_msg: st.info("AI Logic ready. Integration pending backend server.")

    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["📊 Dashboard", "🚧 Work Progress", "🚛 Trips & Logistics", "🚜 Diesel & Machine", "🛠️ Database"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="card-green"><b>Work Progress</b><br>{status_df["%"].mean():.2f}%</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-blue"><b>Billing Value</b><br>Rs. {billed/100000:.2f} L</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card-amber"><b>Diesel Stock</b><br>{get_fuel():,.0f} L</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-red"><b>Total Trips Today</b><br>{st.session_state.trip_log["Total"].sum()}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("Bill of Quantities (BOQ) Progress Status")
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1: st.subheader("Item-wise Completion (%)"); st.bar_chart(status_df.set_index("Item")["%"])
    with col_chart2: st.subheader("Work Value (Lakhs)"); st.line_chart(status_df.set_index("Item")["Value"])

# --- TAB 2: WORK PROGRESS ---
with tabs[1]:
    st.subheader("Daily Progress Report (DPR) Entry")
    with st.form("progress_form"):
        col_p1, col_p2, col_p3 = st.columns(3)
        sel_item = col_p1.selectbox("BOQ Item", st.session_state.boq_master["Item"].tolist())
        qty_done = col_p2.number_input("Today's Done Quantity", min_value=0.0)
        p_date = col_p1.date_input("DPR Date", datetime.now())
        rem_p = col_p3.text_input("Remarks / Section")
        if st.form_submit_button("➕ Save Work Log"):
            code = st.session_state.boq_master[st.session_state.boq_master["Item"] == sel_item]["Code"].values[0]
            st.session_state.boq_progress.append({"Date": p_date.strftime("%Y-%m-%d"), "Code": code, "Item": sel_item, "Done Qty": qty_done, "Remark": rem_p})
            st.success("Log Saved!"); st.rerun()

# --- TAB 3: TRIPS & LOGISTICS ---
with tabs[2]:
    st.subheader("Supervisors Trip Chart (OCR Simulation Ready)")
    col_trip1, col_trip2 = st.columns([1, 2])
    with col_trip1:
        st.write("📸 **OCR Image Upload**")
        trip_img = st.file_uploader("Upload Trip Chart Picture", type=["png", "jpg", "jpeg"])
        if st.button("🤖 AI-OCR Simulate Read"):
            if trip_img:
                for i in range(len(st.session_state.trip_log)):
                    st.session_state.trip_log.loc[i, "T-1":"T-10"] = np.random.randint(1, 4, size=10)
                    st.session_state.trip_log.loc[i, "Total"] = st.session_state.trip_log.loc[i, "T-1":"T-42"].sum()
                st.success("Successfully parsed trips from image!"); st.rerun()
    
    st.write("---")
    st.write("**TRIP MATRIX (42 TRIPS PER SHIFT)**")
    e_trips = st.data_editor(st.session_state.trip_log, use_container_width=True)
    if st.button("💾 Save Trip Matrix"):
        for i in range(len(e_trips)):
            e_trips.loc[i, "Total"] = e_trips.loc[i, "T-1":"T-42"].sum()
            e_trips.loc[i, "HMR"] = float(e_trips.loc[i, "Closed Reading"]) - float(e_trips.loc[i, "Start Reading"])
        st.session_state.trip_log = e_trips; st.success("Trips Saved!"); st.rerun()

# --- TAB 4: DIESEL & MACHINE ---
with tabs[3]:
    st.subheader("HSD Management & Site Snapshot")
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Tank Stock", f"{get_fuel():,.2f} L")
    with c2: st.metric("Active Machinery", f"{sum(st.session_state.site_snapshot[-1].values())-1 if st.session_state.site_snapshot else 0}")
    
    st.write("---")
    with st.expander("➕ Log Diesel Issue"):
        dm_mach = st.selectbox("Machine NO", ["HYVA 2218", "EX KOBELCO 380", "HYVA 2217", "DOZER HIRE"])
        dm_qty = st.number_input("Fuel Fill (L)", min_value=0.0)
        if st.button("Save Diesel Entry"):
            st.session_state.consumption_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "MACHINE NO": dm_mach, "FILL HSD": dm_qty})
            st.success("HSD Issued!"); st.rerun()

# --- TAB 5: DATABASE ---
with tabs[4]:
    st.subheader("🛠️ Master Data & Bulk Upload")
    d_tab1, d_tab2 = st.tabs(["BOQ & Rates", "Project Machines"])
    with d_tab1:
        st.write("Edit Project Scopes and Unit Rates")
        eb = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save BOQ Database"): st.session_state.boq_master = eb; st.success("BOQ Updated!"); st.rerun()
    with d_tab2:
        em = st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Machine Master"): st.session_state.machine_master = em; st.success("Machines Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL MEGA ERP v10.0</b> | Adani Power Anuppur Project<br>
        Developed by: <b>Upendra Singh</b> | Contractor: Bhaiyalal Infra<br>
        Sync Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
