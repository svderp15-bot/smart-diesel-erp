# CIDPL SMART DIESEL ERP (ANUPPUR PROJECT SPECIAL)
# PROJECT: ANUPPUR 3X800 MW THERMAL POWER PROJECT (ADANI POWER LTD)
# AUTHOR: UPENDRA SINGH | ORGANIZATION: CIDPL

import streamlit as st
import pandas as pd
import os
from datetime import datetime
import io
import re

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
    .ai-box { background-color: #f0fdf4; border: 1px solid #bbf7d0; padding: 10px; border-radius: 8px; margin-bottom: 10px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- INITIALIZE STATE ----------------
if 'machine_master' not in st.session_state:
    st.session_state.machine_master = pd.DataFrame([
        {"MACHINE NO": "EX KOBEELCO 380", "MACHINERY TYPE": "EXCAVATOR", "AVG": 22.5},
        {"MACHINE NO": "EX KOMATSU 300", "MACHINERY TYPE": "EXCAVATOR", "AVG": 20.0},
        {"MACHINE NO": "EX XCMG 210", "MACHINERY TYPE": "EXCAVATOR", "AVG": 12.5},
        {"MACHINE NO": "EX TATA HITACHI 370 (HIRE)", "MACHINERY TYPE": "EXCAVATOR", "AVG": 25.0},
        {"MACHINE NO": "GRADER 4180D", "MACHINERY TYPE": "GRADER", "AVG": 16.0},
        {"MACHINE NO": "HAMM ROLLER", "MACHINERY TYPE": "SOIL COMPACTOR", "AVG": 8.2},
        {"MACHINE NO": "HYVA 2218", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 2217", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 2649", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 3560", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 3511", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 1134", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 3101", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 3102", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 3103", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "HYVA 9034", "MACHINERY TYPE": "TIPPER", "AVG": 2.3},
        {"MACHINE NO": "CAMPER", "MACHINERY TYPE": "LMV", "AVG": 14.0},
        {"MACHINE NO": "BULERO 3995 (HIRE)", "MACHINERY TYPE": "LMV", "AVG": 15.0},
        {"MACHINE NO": "BULERO HIRE (HIRE)", "MACHINERY TYPE": "LMV", "AVG": 15.0},
        {"MACHINE NO": "DG 62.5 KVA", "MACHINERY TYPE": "DG SET", "AVG": 0.0},
        {"MACHINE NO": "DOZER (HIRE)", "MACHINERY TYPE": "DOZER", "AVG": 0.0},
        {"MACHINE NO": "TRACTOR WT 9785", "MACHINERY TYPE": "WATER TANKER", "AVG": 4.0},
        {"MACHINE NO": "TRACTOR WT 4125", "MACHINERY TYPE": "WATER TANKER", "AVG": 3.0},
        {"MACHINE NO": "TRACTOR WT 3757", "MACHINERY TYPE": "WATER TANKER", "AVG": 3.0},
        {"MACHINE NO": "CHENARAM", "MACHINERY TYPE": "CONTRACTOR", "AVG": 0.0}
    ])

if 'consumption_log' not in st.session_state:
    st.session_state.consumption_log = []

if 'receipt_log' not in st.session_state:
    st.session_state.receipt_log = []

if 'opening_stock' not in st.session_state:
    st.session_state.opening_stock = 5000.0

# ---------------- CORE LOGIC ----------------
def get_last_reading(machine_name):
    if not st.session_state.consumption_log:
        return 0.0
    df = pd.DataFrame(st.session_state.consumption_log)
    machine_data = df[df["MACHINE NO"] == machine_name]
    if not machine_data.empty:
        return float(machine_data.iloc[-1]["CURRENT READING"])
    return 0.0

def calculate_stock():
    total_received = sum(r['Qty (L)'] for r in st.session_state.receipt_log)
    total_issued = sum(c['FILL HSD'] for c in st.session_state.consumption_log)
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

# ---------------- SIDEBAR: AI ASSISTANT ----------------
with st.sidebar:
    st.header("📊 Site Statistics")
    current_stock = calculate_stock()
    st.metric("Current Tank Stock", f"{current_stock:,.2f} L")
    
    st.write("---")
    st.markdown('<div class="ai-box"><b>🤖 CIDPL Smart Assistant</b><br>Try: "EX KOBELCO reading 1500, filled 300L"</div>', unsafe_allow_html=True)
    ai_input = st.text_input("Talk to ERP (AI)", placeholder="Type details here...")
    
    # Simple Parsing Logic (Local AI Simulation)
    parsed_machine = ""
    parsed_curr = 0.0
    parsed_fill = 0.0
    if ai_input:
        # Match machine name from master
        for m in st.session_state.machine_master["MACHINE NO"]:
            if m.split()[0].lower() in ai_input.lower():
                parsed_machine = m
                break
        # Match numbers
        nums = re.findall(r'\d+', ai_input)
        if len(nums) >= 1: parsed_curr = float(nums[0])
        if len(nums) >= 2: parsed_fill = float(nums[1])
        st.success(f"Parsed: {parsed_machine} | Curr: {parsed_curr} | Fill: {parsed_fill}")

    st.write("---")
    st.subheader("⚙️ Settings")
    st.session_state.opening_stock = st.number_input("Opening Stock", value=float(st.session_state.opening_stock))
    
    if st.button("🗑️ Reset All Data", type="secondary"):
        st.session_state.consumption_log = []; st.session_state.receipt_log = []; st.rerun()

    if st.button("📥 Download Excel Report"):
        data_xl = to_excel([pd.DataFrame(st.session_state.consumption_log), pd.DataFrame(st.session_state.receipt_log), st.session_state.machine_master], 
                          ['HSD ISSUE REPORT', 'Receipts', 'Machine_Master'])
        st.download_button(label="💾 Download Report", data=data_xl, file_name=f"HSD_REPORT_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

# ---------------- MAIN APP TABS ----------------
tab1, tab2, tab3, tab4 = st.tabs(["🚜 HSD Issue Log", "⛽ Diesel Receipts", "📋 Log Management", "🛠️ Master Setup"])

# --- TAB 1: MACHINE CONSUMPTION ---
with tab1:
    st.subheader("HSD ISSUE REPORT DAY/NIGHT")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("DATED", datetime.now())
        machine_list = st.session_state.machine_master["MACHINE NO"].tolist()
        machine = st.selectbox("MACHINE NO", machine_list, index=machine_list.index(parsed_machine) if parsed_machine else 0)
        
        m_row = st.session_state.machine_master[st.session_state.machine_master["MACHINE NO"] == machine]
        avg = st.number_input("AVG", value=float(m_row["AVG"].values[0]), step=0.1)
        m_type = m_row["MACHINERY TYPE"].values[0]
        
    with col2:
        last_rd = get_last_reading(machine)
        prv = st.number_input("PRV.READING", value=last_rd, step=0.01)
        curr = st.number_input("CURRENT READING", value=parsed_curr if parsed_curr > 0 else prv, min_value=0.0, step=0.01)
        
    with col3:
        hmr = curr - prv if curr >= prv else 0.0
        cons_theor = hmr * avg
        st.write(f"**HMR (6-5):** `{hmr:.2f}`")
        st.write(f"**CONSUPTION (7x4):** `{cons_theor:.2f} L`")
        
        fill = st.number_input("FILL HSD", value=parsed_fill if parsed_fill > 0 else 0.0, step=1.0)
        balance = st.number_input("BALNCE HSD", value=0.0, step=1.0)
        remark = st.text_input("Remarks", placeholder="Shift/Location")

    if st.button("➕ Save Entry", use_container_width=True, type="primary"):
        # Match user's 1-11 SR format
        sr = len(st.session_state.consumption_log) + 1
        entry = {
            "SR-": sr,
            "MACHINE NO": machine,
            "MACHINERY TYPE": m_type,
            "AVG": avg,
            "PRV.READING": prv,
            "CURRENT READING": curr,
            "HMR (6-5)": round(hmr, 2),
            "CUNSUPTION (7x4)": round(cons_theor, 2),
            "BALNCE HSD": balance,
            "FILL HSD": fill,
            "Remarks": remark,
            "DATE": date.strftime("%Y-%m-%d")
        }
        st.session_state.consumption_log.append(entry)
        st.success(f"Log for {machine} Saved!")
        st.rerun()

# --- TAB 2: DIESEL RECEIPTS ---
with tab2:
    st.subheader("Diesel Received (Dispenser Stock)")
    col1, col2, col3 = st.columns(3)
    with col1:
        r_date = st.date_input("Receipt Date", datetime.now()); challan = st.text_input("Challan No.")
    with col2:
        qty = st.number_input("Quantity Received (Liters)", min_value=0.0, step=10.0); vendor = st.text_input("Vendor Name", "IOCL / BPCL")
    with col3:
        vehicle = st.text_input("Tanker No."); r_remark = st.text_input("Receipt Remarks")

    if st.button("📥 Add Receipt", use_container_width=True):
        st.session_state.receipt_log.append({"Date": r_date.strftime("%Y-%m-%d"), "Challan": challan, "Qty (L)": qty, "Vendor": vendor, "Tanker": vehicle, "Remark": r_remark})
        st.success("Stock Updated!"); st.rerun()

# --- TAB 3: LOG MANAGEMENT ---
with tab3:
    st.subheader("📋 Data Management")
    with st.expander("⬆️ Bulk Upload Excel (Anuppur Format)"):
        st.write("Upload your Excel. Ensure headers match the report columns.")
        up_file = st.file_uploader("Choose Excel File", type="xlsx")
        if up_file:
            new_data = pd.read_excel(up_file)
            if st.button("✅ Import to Logs"):
                st.session_state.consumption_log.extend(new_data.to_dict('records'))
                st.success("Data Imported!"); st.rerun()

    st.write("---")
    if st.session_state.consumption_log:
        df_c = pd.DataFrame(st.session_state.consumption_log)
        edited = st.data_editor(df_c, use_container_width=True, num_rows="dynamic")
        if st.button("💾 Save All Changes"):
            st.session_state.consumption_log = edited.to_dict('records'); st.success("Updated!"); st.rerun()
    else: st.info("No records yet.")

# --- TAB 4: MASTER SETUP ---
with tab4:
    st.subheader("🛠️ Machinery Master Setup")
    edited_master = st.data_editor(st.session_state.machine_master, use_container_width=True, num_rows="dynamic")
    if st.button("💾 Save Master"):
        st.session_state.machine_master = edited_master; st.success("Master List Updated!"); st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL SMART DIESEL ERP</b> | Site: Anuppur 3x800 MW (Adani Power Ltd)<br>
        Developed by: <b>Upendra Singh</b><br>
        Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    </div>
""", unsafe_allow_html=True)
