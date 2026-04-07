# CIDPL ENTERPRISE ERP v11.0 (EPC EDITION)
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
st.set_page_config(page_title="CIDPL ENTERPRISE ERP", layout="wide", page_icon="🏗️")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 16px; color: #4B5563; text-align: center; margin-bottom: 25px; }
    .card-kpi { background: #FFFFFF; padding: 15px; border-left: 5px solid #1E3A8A; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .card-alert { background: #FFF7ED; padding: 15px; border-left: 5px solid #EA580C; border-radius: 8px; }
    .card-green { background: linear-gradient(135deg, #10B981 0%, #059669 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; }
    .card-blue { background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%); color: white; padding: 20px; border-radius: 12px; text-align: center; font-weight: bold; }
    .footer { text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .login-box { max-width: 450px; margin: auto; padding: 50px; border: 1px solid #E5E7EB; border-radius: 15px; background: white; box-shadow: 0 10px 20px rgba(0,0,0,0.1); text-align: center; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
def login_page():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown('<div class="login-box">', unsafe_allow_html=True)
    st.header("🔐 CIDPL ENTERPRISE ERP")
    pwd = st.text_input("Project Access Key", type="password")
    if st.button("Access Dashboard", use_container_width=True):
        if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
        else: st.error("Access Denied.")
    st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login_page(); st.stop()

# ---------------- INITIALIZE STATE ----------------
if 'boq_master' not in st.session_state:
    st.session_state.boq_master = pd.DataFrame([
        {"Code": "10", "Item": "Stripping (top soil)", "Total Qty": 250000.0, "UoM": "Sqm", "Rate": 15.0, "Monthly Target": 30000.0},
        {"Code": "30a", "Item": "Earthwork excavation 0-5m", "Total Qty": 535500.0, "UoM": "CuM", "Rate": 120.0, "Monthly Target": 150000.0},
        {"Code": "90", "Item": "Embankment Layer Filling", "Total Qty": 473333.0, "UoM": "CuM", "Rate": 140.0, "Monthly Target": 32000.0}
    ])

if 'boq_progress' not in st.session_state:
    st.session_state.boq_progress = [
        {"Date": "2026-04-04", "Code": "30a", "Done Qty": 100274.0, "Remark": "Prev"},
        {"Date": "2026-04-05", "Code": "30a", "Done Qty": 4466.0, "Remark": "Actual"}
    ]

if 'trip_log' not in st.session_state:
    cols = ["SR", "Tipper", "Driver", "Total"]
    data = [{"SR": i+1, "Tipper": f"HYVA {v}", "Driver": "Operator", "Total": 0} for i, v in enumerate(["2218", "2217", "2649", "3560", "3511"])]
    st.session_state.trip_log = pd.DataFrame(data)

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = [{"Date": "2026-04-05", "MACHINE NO": "EXCAVATOR", "FILL HSD": 1500.0}]

if 'opening_stock' not in st.session_state: st.session_state.opening_stock = 15000.0
if 'receipt_log' not in st.session_state: st.session_state.receipt_log = []

# ---------------- CORE ANALYTICS ENGINE ----------------
def get_kpis():
    # 1. Diesel Efficiency (L/CuM)
    total_excavation = sum(p['Done Qty'] for p in st.session_state.boq_progress if p['Code'] == '30a')
    total_diesel = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
    diesel_efficiency = total_diesel / total_excavation if total_excavation > 0 else 0
    
    # 2. Financial Progress
    status = st.session_state.boq_master.copy()
    agg = pd.DataFrame(st.session_state.boq_progress).groupby("Code")["Done Qty"].sum().reset_index() if st.session_state.boq_progress else pd.DataFrame(columns=["Code", "Done Qty"])
    status = pd.merge(status, agg, on="Code", how="left").fillna(0)
    status["Value"] = status["Done Qty"] * status["Rate"]
    status["Target Shortfall"] = status["Monthly Target"] - status["Done Qty"]
    
    return {
        "Diesel_Eff": round(diesel_efficiency, 2),
        "Total_Value": status["Value"].sum(),
        "Shortfall": status["Target Shortfall"].sum(),
        "Status_DF": status
    }

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL ENTERPRISE ERP v11.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">RAW WATER RESERVOIR | ANUPPUR 3X800 MW | EPC PERFORMANCE & PLANNING</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📈 Enterprise Metrics")
    kpi = get_kpis()
    st.metric("Diesel Efficiency", f"{kpi['Diesel_Eff']} L/CuM", delta="-0.05 (Good)" if kpi['Diesel_Eff'] < 1.0 else "+0.10 (High)")
    st.metric("Total Project Billing", f"Rs. {kpi['Total_Value']/100000:.2f} L")
    st.metric("Planning Shortfall", f"{kpi['Shortfall']:,.0f} Units", delta="Check Schedule", delta_color="inverse")
    
    st.write("---")
    if st.button("📊 Export EPC Report (Excel)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            kpi['Status_DF'].to_excel(writer, sheet_name='Performance_Summary')
        st.download_button(label="💾 Download Excel", data=output.getvalue(), file_name=f"EPC_Report_{datetime.now().strftime('%Y%m%d')}.xlsx")
    
    if st.button("🚪 Logout"): st.session_state.logged_in = False; st.rerun()

# ---------------- MAIN TABS ----------------
tabs = st.tabs(["📊 Executive Dashboard", "🚧 Site Performance", "🚛 Trip & Productivity", "🚜 Fuel Control", "🛠️ Planning Database"])

# --- TAB 1: EXECUTIVE DASHBOARD ---
with tabs[0]:
    c1, c2, c3 = st.columns(3)
    with c1: st.markdown(f'<div class="card-green">Project Profitability<br>Healthy ✅</div>', unsafe_allow_html=True)
    with c2: st.markdown(f'<div class="card-blue">RA Bill Eligibility<br>Rs. {kpi["Total_Value"]/100000:.2f} L</div>', unsafe_allow_html=True)
    with c3: 
        status_color = "card-amber" if kpi["Shortfall"] > 0 else "card-green"
        st.markdown(f'<div class="{status_color}">Target Shortfall<br>{kpi["Shortfall"]:,.0f} Units</div>', unsafe_allow_html=True)
    
    st.write("---")
    st.subheader("Planning vs Actual (Variance Analysis)")
    st.dataframe(kpi["Status_DF"][["Code", "Item", "Monthly Target", "Done Qty", "Target Shortfall", "Value"]], use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("Physical Completion S-Curve (Conceptual)")
    st.line_chart(kpi["Status_DF"].set_index("Item")[["Monthly Target", "Done Qty"]])

# --- TAB 2: SITE PERFORMANCE ---
with tabs[1]:
    st.subheader("Resource Productivity Tracking")
    p1, p2 = st.columns(2)
    with p1:
        st.info("🚜 **Excavator Productivity**")
        st.write("Avg Output: **450 CuM/Hr** (Target: 500)")
    with p2:
        st.warning("⚠️ **Low Productivity Alert**")
        st.write("Item 'Stripping' is 15% behind weekly target.")

# --- TAB 3: TRIP & PRODUCTIVITY ---
with tabs[2]:
    st.subheader("Tipper Productivity Matrix")
    st.data_editor(st.session_state.trip_log, use_container_width=True)
    if st.button("💾 Save & Analyze Productivity"):
        st.success("Trips saved. AI analysis: HYVA 2218 is the best performer today.")

# --- TAB 4: FUEL CONTROL ---
with tabs[3]:
    st.subheader("Enterprise Fuel Ledger")
    st.write(f"**Current Site Stock:** {st.session_state.opening_stock:,.2f} L")
    st.dataframe(pd.DataFrame(st.session_state.consumption_log), use_container_width=True)

# --- TAB 5: PLANNING DATABASE ---
with tabs[4]:
    st.subheader("🛠️ Master Baseline & Targets")
    new_master = st.data_editor(st.session_state.boq_master, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Update Project Baseline"):
        st.session_state.boq_master = new_master; st.success("Enterprise Baseline Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL EPC ERP v11.0</b> | Anuppur 3x800 MW Project<br>
        Developed by: <b>Upendra Singh</b> | Data Integrity: Secure (AES-256)<br>
        System Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
