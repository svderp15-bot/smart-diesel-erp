# CIDPL ADVANCED PROJECT ERP v9.0
# PROJECT: RAW WATER RESERVOIR, ANUPPUR (PHASE-I)
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

# Colorful Styling for Dashboard & UI
st.markdown("""
    <style>
    .main-header { font-size: 30px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .card-green { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-blue { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-amber { background: linear-gradient(135deg, #F59E0B 0%, #D97706 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .card-red { background: linear-gradient(135deg, #EF4444 0%, #B91C1C 100%); color: white; padding: 15px; border-radius: 10px; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1); }
    .footer { text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .login-box { max-width: 400px; margin: auto; padding: 40px; border: 1px solid #E5E7EB; border-radius: 10px; background: white; box-shadow: 0 4px 10px rgba(0,0,0,0.1); }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False

def login_page():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.header("🔐 CIDPL ERP v9.0")
    pwd = st.text_input("Project Access Password", type="password")
    if st.button("Login", use_container_width=True):
        if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
        else: st.error("Access Denied.")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

# ---------------- INITIALIZE STATE ----------------
# 1. BOQ Master
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil)", "Total Qty": 125000.0, "UoM": "Sqm", "Unit Rate": 15.0},
        {"Code": "20", "Item": "Excavation (All types)", "Total Qty": 1700000.0, "UoM": "CuM", "Unit Rate": 125.0},
        {"Code": "90", "Item": "Embankment Layer Filling", "Total Qty": 473333.0, "UoM": "CuM", "Unit Rate": 145.0},
        {"Code": "120", "Item": "1000 micron HDPE Sheet", "Total Qty": 444803.0, "UoM": "Sqm", "Unit Rate": 350.0}
    ])

# 2. Project Logs
if 'boq_progress' not in st.session_state: st.session_state.boq_progress = []
if 'consumption_log' not in st.session_state: st.session_state.consumption_log = []
if 'receipt_log' not in st.session_state: st.session_state.receipt_log = []
if 'manpower_log' not in st.session_state: st.session_state.manpower_log = []
if 'opening_stock' not in st.session_state: st.session_state.opening_stock = 15000.0

# 3. Trip Chart Module (SR 1-10 HYVAs)
if 'trip_log' not in st.session_state:
    # 10 Vehicles, each with columns: SR, Tipper, Driver, Start Reading, Closed Reading, HMR, Trips (1-42), Total Trips
    cols = ["SR", "Tipper", "Driver", "Start Reading", "Closed Reading", "HMR"] + [f"T-{i}" for i in range(1, 43)] + ["Total"]
    data = []
    vehicles = ["HYVA 2218", "HYVA 2217", "HYVA 2649", "HYVA 3560", "HYVA 3511", "HYVA 1134", "HYVA 3101", "HYVA 3102", "HYVA 3103", "HYVA 9034"]
    for i, v in enumerate(vehicles):
        row = {c: 0 for c in cols}
        row["SR"] = i + 1; row["Tipper"] = v; row["Driver"] = "Operator"; row["HMR"] = 0.0; row["Total"] = 0
        data.append(row)
    st.session_state.trip_log = pd.DataFrame(data)

# ---------------- CORE LOGIC ----------------
def get_boq_status():
    status = st.session_state.boq_master.copy()
    if not st.session_state.boq_progress: status["Done Qty"] = 0.0
    else:
        agg = pd.DataFrame(st.session_state.boq_progress).groupby("Code")["Done Qty"].sum().reset_index()
        status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    status["Value"] = status["Done Qty"] * status["Unit Rate"]
    status["%"] = (status["Done Qty"] / status["Total Qty"] * 100).round(2)
    return status

def get_fuel_stock():
    total_in = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    total_out = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
    return st.session_state.opening_stock + total_in - total_out

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL-BHAIYALAL ADVANCED ERP v9.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">RAW WATER RESERVOIR PROJECT | ANUPPUR 3X800 MW | ADANI POWER LTD</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR: REVENUE & REPORTS ----------------
with st.sidebar:
    st.header("🏢 Site Revenue Center")
    status_df = get_boq_status()
    billed = status_df["Value"].sum()
    st.markdown(f'<div class="card-blue"><b>Total Project Billing</b><br>Rs. {billed/100000:.2f} Lakhs</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.header("📋 High-Signal Reports")
    report_type = st.radio("Select Period", ["Daily", "Weekly", "Monthly"])
    
    if st.button("📊 Generate Excel (Professional)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            # Sheet 1: DPR Dashboard
            status_df.to_excel(writer, sheet_name='DPR_Summary', index=False)
            # Sheet 2: Trip Chart
            st.session_state.trip_log.to_excel(writer, sheet_name='Trip_Chart', index=False)
            # Formatting (XlsxWriter)
            workbook = writer.book; header_fmt = workbook.add_format({'bold': True, 'bg_color': '#1E3A8A', 'font_color': 'white'})
            for worksheet in writer.sheets.values():
                for col_num, value in enumerate(status_df.columns.values):
                    worksheet.write(0, col_num, value, header_fmt)
        st.download_button(label=f"💾 Download {report_type} Report", data=output.getvalue(), file_name=f"CIDPL_Report_{report_type}_{datetime.now().strftime('%Y%m%d')}.xlsx")

    st.write("---")
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["📊 Dashboard", "🚧 Progress Log", "🚛 Trip Chart (OCR)", "🚜 Diesel & Machine", "🛠️ Database"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="card-green"><b>Physical Progress</b><br>{status_df["%"].mean():.2f}%</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-blue"><b>Billing Value</b><br>Rs. {billed/100000:.2f}L</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card-amber"><b>HSD Stock</b><br>{get_fuel_stock():,.0f} L</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-red"><b>Active Trips</b><br>{st.session_state.trip_log["Total"].sum()} Total</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("Bill of Quantities (BOQ) Summary Status")
    st.dataframe(status_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("Physical vs Financial Growth (Trending)")
    st.line_chart(status_df.set_index("Item")["Value"])

# --- TAB 2: PROGRESS LOG ---
with tabs[1]:
    st.subheader("Daily Work Progress Report")
    with st.form("dpr_form"):
        col1, col2, col3 = st.columns(3)
        p_item = col1.selectbox("BOQ Item", st.session_state.boq_master["Item"].tolist())
        p_qty = col2.number_input("Today's Quantity", min_value=0.0)
        p_rem = col3.text_input("Remarks / Chainage")
        if st.form_submit_button("Save Work Progress"):
            code = st.session_state.boq_master[st.session_state.boq_master["Item"] == p_item]["Code"].values[0]
            st.session_state.boq_progress.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Code": code, "Item": p_item, "Done Qty": p_qty, "Remark": p_rem})
            st.success("Work Logged Successfully!"); st.rerun()

# --- TAB 3: TRIP CHART (OCR) ---
with tabs[2]:
    st.subheader("Supervisor Trip Chart & OCR Simulator")
    
    col_up1, col_up2 = st.columns([1, 2])
    with col_up1:
        st.write("📸 **Upload Trip Chart Picture**")
        trip_file = st.file_uploader("Upload Image (OCR)", type=["png", "jpg", "jpeg"])
        if st.button("🤖 Simulate AI-OCR Read"):
            if trip_file:
                # Simulated OCR Reading 5 trips for each HYVA
                for i in range(len(st.session_state.trip_log)):
                    st.session_state.trip_log.loc[i, "T-1":"T-5"] = np.random.randint(1, 3, size=5)
                    st.session_state.trip_log.loc[i, "Total"] = st.session_state.trip_log.loc[i, "T-1":"T-42"].sum()
                st.success("AI parsed 50 trips from the chart image!"); st.rerun()
            else: st.warning("Please upload a picture first.")

    st.write("---")
    st.write("**TRIP CHART MATRIX (Log 1-42 Trips)**")
    edited_trips = st.data_editor(st.session_state.trip_log, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Trip Data"):
        # Recalculate totals
        for i in range(len(edited_trips)):
            edited_trips.loc[i, "Total"] = edited_trips.loc[i, "T-1":"T-42"].sum()
            edited_trips.loc[i, "HMR"] = float(edited_trips.loc[i, "Closed Reading"]) - float(edited_trips.loc[i, "Start Reading"])
        st.session_state.trip_log = edited_trips; st.success("Trip Data Updated!"); st.rerun()

# --- TAB 4: DIESEL & MACHINE ---
with tabs[3]:
    st.subheader("HSD Management Control")
    st.metric("Current HSD Stock (Opening + Receipts - Issues)", f"{get_fuel_stock():,.2f} L")
    st.write("---")
    c1, c2, c3 = st.columns(3)
    dm_machine = c1.selectbox("Select Machine", ["EX KOBELCO 380", "HYVA 2218", "HYVA 2217", "BOLERO"])
    dm_fill = c2.number_input("HSD Fill (L)", min_value=0.0)
    if st.button("➕ Log Diesel Issue"):
        st.session_state.consumption_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "MACHINE NO": dm_machine, "FILL HSD": dm_fill})
        st.success("Diesel Logged!"); st.rerun()

# --- TAB 5: DATABASE ---
with tabs[4]:
    st.subheader("🛠️ Professional Database Manager")
    st.write("**Edit BOQ Scopes & Unit Rates**")
    e_boq = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Master DB"): st.session_state.boq_master = e_boq; st.success("Database Saved!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL FULL PROJECT ERP v9.0</b> | Adani Power Ltd (Anuppur Project)<br>
        Developed by: <b>Upendra Singh</b> | Contact for Support: (Admin/Bhaiyalal Infra)<br>
        Current System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
