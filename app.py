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
    .footer { text-align: center; font-size: 14px; color: #9CA3AF; margin-top: 50px; border-top: 1px solid #E5E7EB; padding-top: 20px; }
    .stTabs [data-baseweb="tab-list"] { gap: 24px; }
    .stTabs [data-baseweb="tab"] { height: 50px; white-space: pre-wrap; background-color: #f0f2f6; border-radius: 4px 4px 0px 0px; padding: 10px 20px; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE STATE ----------------
if 'machine_master' not in st.session_state:
    # Default Machinery List for CIDPL
    st.session_state.machine_master = pd.DataFrame([
        {"Machine": "EX KOBELCO 380", "Type": "EXCAVATOR", "Default_AVG": 25.0},
        {"Machine": "EX KOMATSU 300", "Type": "EXCAVATOR", "Default_AVG": 22.0},
        {"Machine": "HYVA 2218", "Type": "TIPPER", "Default_AVG": 2.5},
        {"Machine": "BOLERO", "Type": "LMV", "Default_AVG": 0.1},
        {"Machine": "DG 62.5 KVA", "Type": "DG", "Default_AVG": 8.0},
        {"Machine": "DOZER", "Type": "DOZER", "Default_AVG": 18.0},
        {"Machine": "GRADER 4180D", "Type": "GRADER", "Default_AVG": 15.0}
    ])

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = [
        {"Date": "2026-04-05", "Machine": "EX KOBELCO 380", "AVG": 25.0, "PRV": 1200.0, "CURR": 1210.0, "HMR": 10.0, "CONS (L)": 250.0, "REMARK": "Day Shift", "TIMESTAMP": "08:30:00"},
        {"Date": "2026-04-05", "Machine": "HYVA 2218", "AVG": 2.5, "PRV": 5000.0, "CURR": 5050.0, "HMR": 50.0, "CONS (L)": 125.0, "REMARK": "Haulage Road", "TIMESTAMP": "09:15:00"},
        {"Date": "2026-04-05", "Machine": "DG 62.5 KVA", "AVG": 8.0, "PRV": 450.0, "CURR": 455.0, "HMR": 5.0, "CONS (L)": 40.0, "REMARK": "Night Backup", "TIMESTAMP": "18:45:00"}
    ]

if 'receipt_log' not in st.session_state:
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

def to_excel(df_list, sheet_names):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        for df, name in zip(df_list, sheet_names):
            df.to_excel(writer, sheet_name=name, index=False)
    return output.getvalue()

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
        data_xl = to_excel([pd.DataFrame(st.session_state.consumption_log), pd.DataFrame(st.session_state.receipt_log), st.session_state.machine_master], 
                          ['Consumption', 'Receipts', 'Machine_Master'])
        st.download_button(label="💾 Download Final Excel", data=data_xl, file_name=f"CIDPL_Diesel_Report_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------- MAIN APP TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["🚜 Machine Consumption", "⛽ Diesel Receipts", "📋 Log Management", "🛠️ Master Setup"])

# --- TAB 1: MACHINE CONSUMPTION ---
with tab1:
    st.subheader("Add Daily Machinery Issue Log")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        date = st.date_input("Date", datetime.now())
        machine_list = st.session_state.machine_master["Machine"].tolist()
        machine = st.selectbox("Select Machinery", machine_list)
        
        # Auto-fetch default AVG from master
        default_avg = st.session_state.machine_master[st.session_state.machine_master["Machine"] == machine]["Default_AVG"].values[0]
        avg = st.number_input("Average Consumption", value=float(default_avg), step=0.1)
        
    with col2:
        last_rd = get_last_reading(machine)
        prv = st.number_input("Previous Reading", value=last_rd, step=0.01)
        curr = st.number_input("Current Reading", min_value=prv, step=0.01)
        
    with col3:
        fill = st.number_input("Diesel Fill (L)", min_value=0.0, step=1.0)
        remark = st.text_input("Remarks", placeholder="Site location/Shift")

    hmr = curr - prv
    st.info(f"💡 **Calculated HMR:** `{hmr:.2f}` | **Actual Fill:** `{fill:.2f} L`")

    if st.button("➕ Save Consumption Entry", use_container_width=True, type="primary"):
        if curr <= prv and hmr != 0:
            st.error("Error: Current reading must be greater than previous.")
        else:
            entry = {
                "Date": date.strftime("%Y-%m-%d"), "Machine": machine, "AVG": avg, "PRV": prv, "CURR": curr,
                "HMR": round(hmr, 2), "CONS (L)": fill, "REMARK": remark, "TIMESTAMP": datetime.now().strftime("%H:%M:%S")
            }
            st.session_state.consumption_log.append(entry)
            st.success(f"Entry saved for {machine}!")
            st.rerun()

# --- TAB 2: DIESEL RECEIPTS ---
with tab2:
    st.subheader("Diesel Received (Incoming from Outside)")
    col1, col2, col3 = st.columns(3)
    with col1:
        r_date = st.date_input("Receipt Date", datetime.now()); challan = st.text_input("Challan No.")
    with col2:
        qty = st.number_input("Quantity Received (Liters)", min_value=0.0, step=10.0); vendor = st.text_input("Vendor Name", "IOCL / BPCL")
    with col3:
        vehicle = st.text_input("Tanker Vehicle No."); r_remark = st.text_input("Receipt Remarks")

    if st.button("📥 Add Diesel Receipt", use_container_width=True):
        if qty <= 0: st.error("Please enter a valid quantity.")
        else:
            r_entry = {"Date": r_date.strftime("%Y-%m-%d"), "Challan": challan, "Qty (L)": qty, "Vendor": vendor, "Tanker": vehicle, "Remark": r_remark}
            st.session_state.receipt_log.append(r_entry)
            st.success(f"Receipt of {qty}L added successfully!"); st.rerun()

# --- TAB 3: LOG MANAGEMENT ---
with tab3:
    st.subheader("Manage Logs (Edit/Delete/Bulk Upload)")
    
    # Bulk Upload Logs
    with st.expander("⬆️ Bulk Upload Consumption Logs"):
        st.write("Upload an Excel file with headers: Date, Machine, AVG, PRV, CURR, HMR, CONS (L), REMARK")
        # Template Download
        template_log = to_excel([pd.DataFrame(columns=["Date", "Machine", "AVG", "PRV", "CURR", "HMR", "CONS (L)", "REMARK"])], ["Template"])
        st.download_button("📂 Download Log Template", template_log, "log_template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        uploaded_logs = st.file_uploader("Choose Excel File for Logs", type="xlsx")
        if uploaded_logs:
            new_logs = pd.read_excel(uploaded_logs)
            if st.button("✅ Import Logs Now"):
                st.session_state.consumption_log.extend(new_logs.to_dict('records'))
                st.success("Bulk Logs Imported!"); st.rerun()

    st.write("---")
    st.write("**Machinery Consumption Log**")
    if st.session_state.consumption_log:
        df_c = pd.DataFrame(st.session_state.consumption_log)
        edited_c = st.data_editor(df_c, use_container_width=True, num_rows="dynamic")
        if st.button("Save Changes to Consumption Log"):
            st.session_state.consumption_log = edited_c.to_dict('records'); st.success("Log Updated!"); st.rerun()
    else: st.info("No consumption records yet.")

# --- TAB 4: MASTER SETUP ---
with tab4:
    st.subheader("🛠️ Machinery Master Setup")
    
    with st.expander("⬆️ Bulk Upload Machine Master"):
        st.write("Upload an Excel file with headers: Machine, Type, Default_AVG")
        template_master = to_excel([pd.DataFrame(columns=["Machine", "Type", "Default_AVG"])], ["Template"])
        st.download_button("📂 Download Master Template", template_master, "master_template.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        uploaded_master = st.file_uploader("Choose Excel File for Master", type="xlsx")
        if uploaded_master:
            new_master = pd.read_excel(uploaded_master)
            if st.button("✅ Overwrite Master List"):
                st.session_state.machine_master = new_master
                st.success("Master List Updated!"); st.rerun()

    st.write("---")
    st.write("**Existing Machinery Master**")
    edited_master = st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Master Changes"):
        st.session_state.machine_master = edited_master
        st.success("Machinery Master Saved!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL SMART DIESEL ERP</b><br>
        Developed by: <b>Upendra Singh</b><br>
        Site: Anuppur 3x800 MW Thermal Power Project (Adani Power Ltd)<br>
        Last Sync: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
