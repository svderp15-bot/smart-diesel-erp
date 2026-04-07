# CIDPL MEGA ERP v10.2 (FULL HISTORY SYNC)
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
st.set_page_config(page_title="CIDPL MEGA ERP", layout="wide", page_icon="🏗️")

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
    st.header("🔐 CIDPL MEGA ERP LOGIN")
    st.write("Anuppur Reservoir Project Phase-I")
    pwd = st.text_input("Project Password", type="password")
    if st.button("Login", use_container_width=True):
        if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
        else: st.error("Access Denied.")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

# ---------------- INITIALIZE STATE ----------------
# 1. Exact BOQ Master (Items A to 370 as provided)
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "A", "Item": "EARTH WORK & ALLIED WORKS", "Total Qty": 0.0, "UoM": "HEAD", "Rate": 0.0},
        {"Code": "10", "Item": "Stripping (Earth work in excavation) of top soil", "Total Qty": 250000.0, "UoM": "Sqm", "Rate": 15.0},
        {"Code": "30a", "Item": "All types of soil 0m to 5.0m", "Total Qty": 535500.0, "UoM": "CuM", "Rate": 120.0},
        {"Code": "40a", "Item": "In weathered rock 0m to 5.0m", "Total Qty": 428400.0, "UoM": "CuM", "Rate": 250.0},
        {"Code": "40b", "Item": "In weathered rock - 5m to 10m", "Total Qty": 642600.0, "UoM": "CuM", "Rate": 310.0},
        {"Code": "50a", "Item": "In weathered rock 0m to 5.0m", "Total Qty": 26775.0, "UoM": "CuM", "Rate": 350.0},
        {"Code": "50b", "Item": "In weathered rock - Chiselling 5m to 10m", "Total Qty": 35700.0, "UoM": "CuM", "Rate": 420.0},
        {"Code": "50c", "Item": "In weathered rock - Chiselling 10m to 15m", "Total Qty": 53550.0, "UoM": "CuM", "Rate": 500.0},
        {"Code": "50d", "Item": "In weathered rock - Chiselling 15m to 17m", "Total Qty": 62475.0, "UoM": "CuM", "Rate": 580.0},
        {"Code": "60a", "Item": "In hard rock 0m to 5.0m", "Total Qty": 14994.0, "UoM": "CuM", "Rate": 750.0},
        {"Code": "60b", "Item": "In hard rock - Chiselling 5m to 10m", "Total Qty": 19992.0, "UoM": "CuM", "Rate": 850.0},
        {"Code": "60c", "Item": "In hard rock - Chiselling 10m to 15m", "Total Qty": 29988.0, "UoM": "CuM", "Rate": 950.0},
        {"Code": "60d", "Item": "In hard rock - Chiselling 15m to 17m", "Total Qty": 34986.0, "UoM": "CuM", "Rate": 1100.0},
        {"Code": "70a", "Item": "In hard rock - Blasting 0m to 5.0m", "Total Qty": 292740.0, "UoM": "CuM", "Rate": 650.0},
        {"Code": "70b", "Item": "In hard rock - Blasting - Chiselling 5m to 10m", "Total Qty": 439110.0, "UoM": "CuM", "Rate": 780.0},
        {"Code": "70c", "Item": "In hard rock - Blasting - Chiselling 10m to 15m", "Total Qty": 512295.0, "UoM": "CuM", "Rate": 900.0},
        {"Code": "70d", "Item": "In hard rock - Blasting - Chiselling 15m to 17m", "Total Qty": 219555.0, "UoM": "CuM", "Rate": 1050.0},
        {"Code": "80", "Item": "extra over and above item no 20 to 70 for transportation", "Total Qty": 2850000.0, "UoM": "CuM", "Rate": 85.0},
        {"Code": "90", "Item": "Earthwork in filling for formation of embankment with", "Total Qty": 473333.0, "UoM": "CuM", "Rate": 140.0},
        {"Code": "90A", "Item": "bought out soil from outside plant area", "Total Qty": 236667.0, "UoM": "CuM", "Rate": 160.0},
        {"Code": "100", "Item": "Backfilling/ Filling for foundation trenches", "Total Qty": 5000.0, "UoM": "CuM", "Rate": 180.0},
        {"Code": "110", "Item": "Sand layer 50mm", "Total Qty": 13040.0, "UoM": "CuM", "Rate": 1200.0},
        {"Code": "120", "Item": "1000 micron HDPE Polyethylene sheet", "Total Qty": 444803.0, "UoM": "Sqm", "Rate": 320.0},
        {"Code": "130", "Item": "cement concrete liner 75mm", "Total Qty": 163000.0, "UoM": "Sqm", "Rate": 450.0},
        {"Code": "140", "Item": "Reservoir Bed with manual lining", "Total Qty": 260800.0, "UoM": "Sqm", "Rate": 480.0},
        {"Code": "150", "Item": "vertical expansion joint", "Total Qty": 31000.0, "UoM": "Rm", "Rate": 150.0},
        {"Code": "160", "Item": "PCC", "Total Qty": 150.0, "UoM": "CuM", "Rate": 4500.0},
        {"Code": "170", "Item": "M20", "Total Qty": 350.0, "UoM": "CuM", "Rate": 5200.0},
        {"Code": "180", "Item": "M25", "Total Qty": 210.0, "UoM": "CuM", "Rate": 5800.0},
        {"Code": "190", "Item": "Pre-cast M25", "Total Qty": 5.0, "UoM": "CuM", "Rate": 7500.0},
        {"Code": "200", "Item": "Steel", "Total Qty": 46.0, "UoM": "MT", "Rate": 65000.0},
        {"Code": "210", "Item": "PVC ribbed water stoppers", "Total Qty": 250.0, "UoM": "Rm", "Rate": 450.0},
        {"Code": "220", "Item": "hot bitumen", "Total Qty": 1000.0, "UoM": "Sqm", "Rate": 120.0},
        {"Code": "230", "Item": "Formwork below ground", "Total Qty": 1850.0, "UoM": "Sqm", "Rate": 350.0},
        {"Code": "240", "Item": "Formwork above ground", "Total Qty": 1080.0, "UoM": "Sqm", "Rate": 450.0},
        {"Code": "250", "Item": "Turfing", "Total Qty": 15000.0, "UoM": "Sqm", "Rate": 65.0},
        {"Code": "260", "Item": "Brick masonry", "Total Qty": 250.0, "UoM": "CuM", "Rate": 4500.0},
        {"Code": "270", "Item": "plaster", "Total Qty": 2040.0, "UoM": "Sqm", "Rate": 180.0},
        {"Code": "280", "Item": "Manual excavation brick drain", "Total Qty": 800.0, "UoM": "CuM", "Rate": 250.0},
        {"Code": "290", "Item": "GSB", "Total Qty": 1335.0, "UoM": "CuM", "Rate": 1500.0},
        {"Code": "300", "Item": "Guard post", "Total Qty": 2033.0, "UoM": "Nos", "Rate": 850.0},
        {"Code": "310", "Item": "kerb stone", "Total Qty": 915.0, "UoM": "Nos", "Rate": 450.0},
        {"Code": "320a", "Item": "1200mm OD MS Pipe RWPH", "Total Qty": 200.0, "UoM": "MT", "Rate": 95000.0},
        {"Code": "320b", "Item": "1200mm OD MS Pipe inlet", "Total Qty": 30.0, "UoM": "MT", "Rate": 95000.0},
        {"Code": "320c", "Item": "450mm OD MS Pipe spillway", "Total Qty": 75.0, "UoM": "MT", "Rate": 95000.0},
        {"Code": "330", "Item": "stone pitching 250mm", "Total Qty": 3140.0, "UoM": "CuM", "Rate": 1200.0},
        {"Code": "330a", "Item": "stone for pitching", "Total Qty": 4710.0, "UoM": "CuM", "Rate": 850.0},
        {"Code": "340", "Item": "sand filter", "Total Qty": 19745.0, "UoM": "CuM", "Rate": 1100.0},
        {"Code": "350", "Item": "graded aggregate", "Total Qty": 675.0, "UoM": "CuM", "Rate": 1800.0},
        {"Code": "510", "Item": "hand placed rock-toe", "Total Qty": 7220.0, "UoM": "CuM", "Rate": 950.0},
        {"Code": "370", "Item": "stone for rock-toe", "Total Qty": 10830.0, "UoM": "CuM", "Rate": 850.0}
    ])

# 2. Cumulative Progress Log (Synced to 05.04.2026)
if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        {"Date": "2026-04-04", "Code": "10", "Item": "Stripping (top soil)", "Done Qty": 63204.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "30a", "Item": "All types of soil 0m to 5.0m", "Done Qty": 100274.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-04", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 91693.0, "Remark": "PREV. CUMULATIVE"},
        {"Date": "2026-04-05", "Code": "30a", "Item": "All types of soil 0m to 5.0m", "Done Qty": 4466.0, "Remark": "DPR Entry"},
        {"Date": "2026-04-05", "Code": "90", "Item": "Embankment Layer Filling", "Done Qty": 1406.0, "Remark": "DPR Entry"}
    ]

# 3. FULL HISTORICAL DIESEL LOG (Receipts & Issues)
if 'receipt_log' not in st.session_state:
    st.session_state.receipt_log = [
        {"Date": "27/02/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 265.0, "Remark": "Initial Fill"},
        {"Date": "06/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 30.0, "Remark": "-"},
        {"Date": "08/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 30.0, "Remark": "-"},
        {"Date": "09/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 690.0, "Remark": "-"},
        {"Date": "10/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 713.16, "Remark": "-"},
        {"Date": "11/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 721.25, "Remark": "-"},
        {"Date": "12/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 552.8, "Remark": "-"},
        {"Date": "13/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 384.5, "Remark": "-"},
        {"Date": "14/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1165.0, "Remark": "-"},
        {"Date": "15/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1070.18, "Remark": "-"},
        {"Date": "16/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 874.0, "Remark": "-"},
        {"Date": "17/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1551.91, "Remark": "-"},
        {"Date": "18/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 441.78, "Remark": "-"},
        {"Date": "19/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1038.74, "Remark": "-"},
        {"Date": "20/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2501.01, "Remark": "-"},
        {"Date": "21/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1690.0, "Remark": "-"},
        {"Date": "22/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 500.0, "Remark": "-"},
        {"Date": "26/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1780.0, "Remark": "-"},
        {"Date": "27/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 995.0, "Remark": "-"},
        {"Date": "28/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2089.0, "Remark": "-"},
        {"Date": "29/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1950.5, "Remark": "-"},
        {"Date": "30/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2006.24, "Remark": "-"},
        {"Date": "31/03/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"},
        {"Date": "01/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"},
        {"Date": "02/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"},
        {"Date": "03/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 1200.0, "Remark": "-"},
        {"Date": "04/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"},
        {"Date": "05/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"},
        {"Date": "06/04/2026", "Vendor": "M/S Babulal Jaiswal Filling Fuel", "Qty (L)": 2000.0, "Remark": "-"}
    ]

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = [
        {"Date": "27/02/2026", "MACHINE NO": "Bolero CG16B-3244", "FILL HSD": 15.0, "Slip": "25801"},
        {"Date": "27/02/2026", "MACHINE NO": "Excavator XCMG", "FILL HSD": 100.0, "Slip": "25801"},
        {"Date": "27/02/2026", "MACHINE NO": "Trailor GJ05UU-1156", "FILL HSD": 150.0, "Slip": "25801"},
        {"Date": "01/03/2026", "MACHINE NO": "Swift UP51S-3399", "FILL HSD": 10.0, "Slip": "25803"},
        {"Date": "06/03/2026", "MACHINE NO": "Bolero CG16B-3244", "FILL HSD": 30.0, "Slip": "25805"},
        {"Date": "08/03/2026", "MACHINE NO": "Bolero CG16B-3244", "FILL HSD": 30.0, "Slip": "25806"},
        {"Date": "09/03/2026", "MACHINE NO": "Swift UP51S-3399", "FILL HSD": 40.0, "Slip": "25811"},
        {"Date": "09/03/2026", "MACHINE NO": "Excavator Kobelco-380", "FILL HSD": 150.0, "Slip": "25802"},
        {"Date": "14/03/2026", "MACHINE NO": "Chanaram Sub Contractor", "FILL HSD": 600.0, "Slip": "25840"},
        {"Date": "05/04/2026", "MACHINE NO": "Excavator Kobelco-380", "FILL HSD": 250.0, "Slip": "18228"},
        {"Date": "06/04/2026", "MACHINE NO": "Chanaram Sub Contractor", "FILL HSD": 600.0, "Slip": "18229"}
    ]

# 4. Trip Chart Module (SR 1-10 HYVAs, 42 Trips)
if 'trip_log' not in st.session_state:
    cols = ["SR", "Tipper", "Driver", "Start Reading", "Closed Reading", "HMR"] + [f"T-{i}" for i in range(1, 43)] + ["Total"]
    vehicles = ["HYVA 2218", "HYVA 2217", "HYVA 2649", "HYVA 3560", "HYVA 3511", "HYVA 1134", "HYVA 3101", "HYVA 3102", "HYVA 3103", "HYVA 9034"]
    data = []
    for i, v in enumerate(vehicles):
        row = {c: 0 for c in cols}; row["SR"] = i + 1; row["Tipper"] = v; row["Driver"] = f"Driver {i+1}"; row["Total"] = 0
        data.append(row)
    st.session_state.trip_log = pd.DataFrame(data)

# 5. Manpower & Machine Counts
if 'manpower_log' not in st.session_state: 
    st.session_state.manpower_log = [{"Date": "2026-04-05", "Staff": 15, "Operators": 20, "Skilled": 2, "Unskilled": 4, "Security": 2}]
if 'site_snapshot' not in st.session_state: 
    st.session_state.site_snapshot = [{"Date": "2026-04-05", "Excavator": 6, "Dumper": 20, "Road Roller": 2, "Drilling": 5, "Water Tanker": 4}]

if 'opening_stock' not in st.session_state: st.session_state.opening_stock = 0.0

# ---------------- CORE LOGIC ----------------
def get_boq_status():
    status = st.session_state.boq_master.copy()
    if not st.session_state.boq_progress:
        status["Done Qty"] = 0.0
    else:
        prog_df = pd.DataFrame(st.session_state.boq_progress)
        agg = prog_df.groupby("Code")["Done Qty"].sum().reset_index()
        status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    
    status["Remaining Qty"] = status["Total Qty"] - status["Done Qty"]
    status["Value (L)"] = (status["Done Qty"] * status["Rate"]) / 100000
    status["% Complete"] = (status["Done Qty"] / status["Total Qty"] * 100).fillna(0).round(2)
    return status

def get_fuel_balance():
    total_in = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    total_out = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
    return st.session_state.opening_stock + total_in - total_out

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL MEGA PROJECT ERP v10.2</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">RAW WATER RESERVOIR | ANUPPUR 3X800 MW | BHAIYALAL INFRASTRUCTURE PVT. LTD.</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("🏢 Site Command Center")
    status_df = get_boq_status()
    total_progress = status_df["% Complete"].mean()
    st.metric("Avg. Project Progress", f"{total_progress:.2f} %")
    
    st.markdown(f'<div class="card-amber"><b>Current HSD Stock</b><br>{get_fuel_balance():,.2f} L</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.header("📋 Export Reports")
    if st.button("📊 Export Comprehensive Excel"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            status_df.to_excel(writer, sheet_name='Summary', index=False)
            pd.DataFrame(st.session_state.boq_master).to_excel(writer, sheet_name='BOQ_Master', index=False)
            pd.DataFrame(st.session_state.receipt_log).to_excel(writer, sheet_name='Fuel_Receipts', index=False)
            pd.DataFrame(st.session_state.consumption_log).to_excel(writer, sheet_name='Fuel_Issues', index=False)
            st.session_state.trip_log.to_excel(writer, sheet_name='Trip_Chart', index=False)
        st.download_button(label="💾 Download Excel Report", data=output.getvalue(), file_name=f"CIDPL_Project_History_{datetime.now().strftime('%Y%m%d')}.xlsx")

    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["📊 Dashboard", "🚧 Work Progress", "🚛 Trip Matrix", "🚜 Diesel & Machine", "🛠️ Database"])

# --- TAB 1: DASHBOARD ---
with tabs[0]:
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.markdown(f'<div class="card-green"><b>Work Progress</b><br>{total_progress:.2f}%</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-blue"><b>Project Cost</b><br>58.09 Cr.</div>', unsafe_allow_html=True)
    with c3: st.markdown(f'<div class="card-amber"><b>Diesel Stock</b><br>{get_fuel_balance():,.0f} L</div>', unsafe_allow_html=True)
    with c4: st.markdown(f'<div class="card-red"><b>Total Trips</b><br>{st.session_state.trip_log["Total"].sum()}</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("Bill of Quantities (BOQ) Progress Summary")
    st.dataframe(status_df, use_container_width=True, hide_index=True)

    col_chart1, col_chart2 = st.columns(2)
    with col_chart1: st.subheader("Item-wise Completion (%)"); st.bar_chart(status_df.set_index("Item")["% Complete"])
    with col_chart2: st.subheader("Work Value (Lakhs)"); st.line_chart(status_df.set_index("Item")["Value (L)"])

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
    
    st.write("---")
    st.write("**Recent Progress Logs**")
    st.dataframe(pd.DataFrame(st.session_state.boq_progress).tail(10), use_container_width=True)

# --- TAB 3: TRIP MATRIX ---
with tabs[2]:
    st.subheader("Supervisors Trip Chart (42 Trips/Shift)")
    st.write("Edit Start/Closed Readings and Trip counts (T-1 to T-42)")
    e_trips = st.data_editor(st.session_state.trip_log, use_container_width=True)
    if st.button("💾 Save Trip Matrix"):
        for i in range(len(e_trips)):
            e_trips.loc[i, "Total"] = e_trips.loc[i, "T-1":"T-42"].sum()
            try:
                e_trips.loc[i, "HMR"] = float(e_trips.loc[i, "Closed Reading"]) - float(e_trips.loc[i, "Start Reading"])
            except: e_trips.loc[i, "HMR"] = 0
        st.session_state.trip_log = e_trips; st.success("Trips Saved!"); st.rerun()

# --- TAB 4: DIESEL ---
with tabs[3]:
    st.subheader("HSD Management & Site Snapshot")
    h1, h2 = st.tabs(["Diesel Issue", "Site Snapshot"])
    
    with h1:
        st.write(f"**Current Tank Balance: {get_fuel_balance():,.2f} L**")
        with st.form("diesel_form"):
            c1, c2, c3 = st.columns(3)
            dm_mach = c1.selectbox("Machine NO", ["HYVA 2218", "EX KOBELCO 380", "HYVA 2217", "BOLERO", "TRACTOR"])
            dm_qty = c2.number_input("Fuel Fill (L)", min_value=0.0)
            dm_slip = c3.text_input("Slip Number")
            if st.form_submit_button("Save Diesel Entry"):
                st.session_state.consumption_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "MACHINE NO": dm_mach, "FILL HSD": dm_qty, "Slip": dm_slip})
                st.success("HSD Issued!"); st.rerun()
        
        st.write("---")
        st.write("**Fuel Issue History**")
        st.dataframe(pd.DataFrame(st.session_state.consumption_log).tail(10), use_container_width=True)

    with h2:
        st.subheader("Daily Manpower & Machinery Deployment")
        m1, m2, m3 = st.columns(3)
        with m1:
            ms = st.number_input("Staff", 15); mo = st.number_input("Operators", 20)
        with m2:
            mk = st.number_input("Skilled", 2); mu = st.number_input("Unskilled", 4)
        with m3:
            s_ex = st.number_input("Excavators", 6); s_dum = st.number_input("Dumpers", 20)
            
        if st.button("📸 Save Snapshot"):
            st.session_state.manpower_log.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Staff": ms, "Operators": mo, "Skilled": mk, "Unskilled": mu})
            st.session_state.site_snapshot.append({"Date": datetime.now().strftime("%Y-%m-%d"), "Excavator": s_ex, "Dumper": s_dum})
            st.success("Snapshot Updated!"); st.rerun()

# --- TAB 5: DATABASE ---
with tabs[4]:
    st.subheader("🛠️ System Configuration")
    d1, d2 = st.tabs(["BOQ Master", "Fuel Receipts"])
    with d1:
        st.write("Edit Project Scopes and Unit Rates")
        eb = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save BOQ Database"): st.session_state.boq_master = eb; st.success("BOQ Updated!"); st.rerun()
    with d2:
        st.write("Fuel Receipt History (Babulal Jaiswal)")
        er = st.data_editor(pd.DataFrame(st.session_state.receipt_log), use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save Receipt Log"): st.session_state.receipt_log = er.to_dict('records'); st.success("Receipts Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL MEGA ERP v10.2</b> | Adani Power Ltd (Anuppur Project)<br>
        Developed by: <b>Upendra Singh</b> | Contractor: Bhaiyalal Infra<br>
        System Status: Secure & Synchronized
    </div>
""", unsafe_allow_html=True)
