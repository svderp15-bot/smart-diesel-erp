# CIDPL SMART DIESEL ERP (ADVANCED VERSION)
# PROJECT: ANUPPUR 3X800 MW THERMAL POWER PROJECT (ADANI POWER LTD)
# AUTHOR: UPENDRA SINGH | ORGANIZATION: CIDPL

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CIDPL DIESEL ERP", layout="wide", page_icon="🚜")

# Custom CSS for Professional Branding
st.markdown("""
    <style>
    .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 0px; }
    .sub-header { font-size: 18px; color: #4B5563; text-align: center; margin-bottom: 20px; }
    .card { background-color: #F3F4F6; padding: 20px; border-radius: 10px; margin-bottom: 20px; border: 1px solid #E5E7EB; }
    .metric-box { text-align: center; padding: 10px; border-radius: 5px; background: white; border: 1px solid #D1D5DB; }
    .footer { text-align: center; font-size: 14px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE STATE ----------------
if 'consumption_log' not in st.session_state:
    # Adding Demo Data for CIDPL
    st.session_state.consumption_log = [
        {"Date": "2026-04-05", "Machine": "EX KOBELCO 380", "AVG": 25.0, "PRV": 1200.0, "CURR": 1210.0, "HMR": 10.0, "CONS (L)": 250.0, "REMARK": "Day Shift", "TIMESTAMP": "08:30:00"},
        {"Date": "2026-04-05", "Machine": "HYVA 2218", "AVG": 2.5, "PRV": 5000.0, "CURR": 5050.0, "HMR": 50.0, "CONS (L)": 125.0, "REMARK": "Haulage Road", "TIMESTAMP": "09:15:00"},
        {"Date": "2026-04-05", "Machine": "DG 62.5 KVA", "AVG": 8.0, "PRV": 450.0, "CURR": 455.0, "HMR": 5.0, "CONS (L)": 40.0, "REMARK": "Night Backup", "TIMESTAMP": "18:45:00"}
    ]

if 'receipt_log' not in st.session_state:
    # Adding Demo Diesel Receipt
    st.session_state.receipt_log = [
        {"Date": "2026-04-04", "Challan": "CH-998877", "Qty (L)": 2000.0, "Vendor": "IOCL", "Tanker": "MP 18 GA 1234", "Remark": "Fresh Stock"}
    ]

if 'opening_stock' not in st.session_state:
    st.session_state.opening_stock = 5000.0

# ---------------- CORE LOGIC ----------------
def get_last_reading(machine_name):
    if not st.session_state.consumption_log:
        return 0.0
    df = pd.DataFrame(st.session_state.consumption_log)
    machine_data = df[df["Machine"] == machine_name]
    if not machine_data.empty:
        return float(machine_data.iloc[-1]["CURR"])
    return 0.0

def calculate_stock():
    total_received = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    total_issued = sum(c['CONS (L)'] for c in st.session_state.consumption_log)
    return st.session_state.opening_stock + total_received - total_issued

# ---------------- BRANDING HEADER ----------------
st.markdown('<div class="main-header">CIDPL SMART DIESEL ERP</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">CLASSIC INFRASTRUCTURE PRIVATE LIMITED | ANUPPUR 3X800 MW THERMAL POWER PROJECT (ADANI POWER LTD)</div>', unsafe_allow_html=True)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.header("📊 Site Statistics")
    current_stock = calculate_stock()
    st.metric("Current Tank Stock", f"{current_stock:,.2f} L")
    
    st.write("---")
    st.subheader("⚙️ Settings")
    st.session_state.opening_stock = st.number_input("Update Opening Stock (Initial)", value=float(st.session_state.opening_stock))
    
    if st.button("🗑️ Reset All Data", type="secondary"):
        st.session_state.consumption_log = []
        st.session_state.receipt_log = []
        st.rerun()

    st.write("---")
    if st.button("📥 Export Full Report (Excel)"):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            pd.DataFrame(st.session_state.consumption_log).to_excel(writer, sheet_name='Consumption', index=False)
            pd.DataFrame(st.session_state.receipt_log).to_excel(writer, sheet_name='Receipts', index=False)
        
        st.download_button(
            label="💾 Download Final Excel",
            data=output.getvalue(),
            file_name=f"CIDPL_Diesel_Report_{datetime.now().strftime('%Y%m%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

# ---------------- MAIN APP TABS ----------------
tab1, tab2, tab3 = st.tabs(["🚜 Machine Consumption", "⛽ Diesel Receipts", "📋 Log Management"])

# --- TAB 1: MACHINE CONSUMPTION ---
with tab1:
    st.subheader("Add Daily Machinery Issue Log")
    
    MACHINES = [
        "EX KOBELCO 380", "EX KOMATSU 300", "EX XCMG 210", "EX TATA HITACHI 370",
        "GRADER 4180D", "HAMM ROLLER", "HYVA 2218", "HYVA 2217", "HYVA 2649",
        "HYVA 3560", "HYVA 3511", "HYVA 1134", "BOLERO", "DG 62.5 KVA", "DOZER"
    ]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        machine = st.selectbox("Select Machinery", MACHINES)
        avg = st.number_input("Average Consumption", min_value=0.0, step=0.1, key="cons_avg")
        
    with col2:
        last_rd = get_last_reading(machine)
        prv = st.number_input("Previous Reading", value=last_rd, step=0.01)
        curr = st.number_input("Current Reading", min_value=prv, step=0.01)
        
    with col3:
        fill = st.number_input("Diesel Fill (L)", min_value=0.0, step=1.0)
        remark = st.text_input("Remarks", placeholder="Site location/Shift")

    hmr = curr - prv
    cons = hmr * avg
    
    st.markdown(f"**Calculated HMR:** `{hmr:.2f}` | **Theoretical Consumption:** `{cons:.2f} L` | **Actual Fill:** `{fill:.2f} L`")

    if st.button("➕ Save Consumption Entry", use_container_width=True, type="primary"):
        if curr <= prv and hmr != 0:
            st.error("Error: Current reading must be greater than previous.")
        else:
            entry = {
                "Date": date.strftime("%Y-%m-%d"),
                "Machine": machine,
                "AVG": avg,
                "PRV": prv,
                "CURR": curr,
                "HMR": round(hmr, 2),
                "CONS (L)": fill, # Logic: We use 'Fill' as the actual issue amount
                "REMARK": remark,
                "TIMESTAMP": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.consumption_log.append(entry)
            st.success(f"Entry saved for {machine}!")
            st.rerun()

# --- TAB 2: DIESEL RECEIPTS ---
with tab2:
    st.subheader("Diesel Received (Incoming from Outside)")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        r_date = st.date_input("Receipt Date", datetime.now())
        challan = st.text_input("Challan No.")
    with col2:
        qty = st.number_input("Quantity Received (Liters)", min_value=0.0, step=10.0)
        vendor = st.text_input("Vendor Name", "IOCL / BPCL")
    with col3:
        vehicle = st.text_input("Tanker Vehicle No.")
        r_remark = st.text_input("Receipt Remarks")

    if st.button("📥 Add Diesel Receipt", use_container_width=True):
        if qty <= 0:
            st.error("Please enter a valid quantity.")
        else:
            r_entry = {
                "Date": r_date.strftime("%Y-%m-%d"),
                "Challan": challan,
                "Qty (L)": qty,
                "Vendor": vendor,
                "Tanker": vehicle,
                "Remark": r_remark
            }
            st.session_state.receipt_log.append(r_entry)
            st.success(f"Receipt of {qty}L added successfully!")
            st.rerun()

# --- TAB 3: LOG MANAGEMENT ---
with tab3:
    st.subheader("Manage Logs (Edit/Delete)")
    
    st.write("**Machinery Consumption Log**")
    if st.session_state.consumption_log:
        df_c = pd.DataFrame(st.session_state.consumption_log)
        edited_c = st.data_editor(df_c, use_container_width=True, num_rows="dynamic")
        if st.button("Save Changes to Consumption Log"):
            st.session_state.consumption_log = edited_c.to_dict('records')
            st.success("Log Updated!")
            st.rerun()
    else:
        st.info("No consumption records yet.")

    st.write("---")
    st.write("**Diesel Receipt Log**")
    if st.session_state.receipt_log:
        df_r = pd.DataFrame(st.session_state.receipt_log)
        edited_r = st.data_editor(df_r, use_container_width=True, num_rows="dynamic")
        if st.button("Save Changes to Receipt Log"):
            st.session_state.receipt_log = edited_r.to_dict('records')
            st.success("Receipts Updated!")
            st.rerun()
    else:
        st.info("No receipt records yet.")

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL SMART DIESEL ERP</b><br>
        Developed by: <b>Upendra Singh</b><br>
        Site: Anuppur 3x800 MW Thermal Power Project (Adani Power Ltd)<br>
        Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
