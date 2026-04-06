# SMART DIESEL ERP (WEB VERSION)
# Built for Streamlit & Render Deployment

import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ---------------- CONFIG ----------------
st.set_page_config(page_title="SMART DIESEL ERP", layout="wide", page_icon="🚜")

DB_FILE = "machine_db.xlsx"
DEFAULT_STOCK = 5000.0

# ---------------- INITIALIZE STATE ----------------
if 'data' not in st.session_state:
    st.session_state.data = []

if 'tank_stock' not in st.session_state:
    st.session_state.tank_stock = DEFAULT_STOCK

# ---------------- DATABASE ----------------
def load_db():
    if os.path.exists(DB_FILE):
        try:
            return pd.read_excel(DB_FILE)
        except:
            return pd.DataFrame(columns=["Machine", "Last_Reading"])
    else:
        return pd.DataFrame(columns=["Machine", "Last_Reading"])

def update_db(machine, current):
    df = load_db()
    if machine in df["Machine"].values:
        df.loc[df["Machine"] == machine, "Last_Reading"] = current
    else:
        new_row = pd.DataFrame([{"Machine": machine, "Last_Reading": current}])
        df = pd.concat([df, new_row], ignore_index=True)
    df.to_excel(DB_FILE, index=False)

# ---------------- DATA & OPTIONS ----------------
MACHINES = [
    "EX KOBELCO 380", "EX KOMATSU 300", "EX XCMG 210", "EX TATA HITACHI 370",
    "GRADER 4180D", "HAMM ROLLER", "HYVA 2218", "HYVA 2217", "HYVA 2649",
    "HYVA 3560", "HYVA 3511", "HYVA 1134", "HYVA 3101", "HYVA 3102",
    "HYVA 3103", "HYVA 9034", "CAMPER", "BOLERO", "DG 62.5 KVA",
    "DOZER", "TRACTOR WT 9785", "TRACTOR WT 4125", "TRACTOR WT 3757"
]

TYPES = ["EXCAVATOR", "TIPPER", "GRADER", "ROLLER", "DOZER", "LMV", "DG"]

# ---------------- UI ----------------
st.title("🚜 SMART DIESEL ERP SYSTEM")
st.markdown("Designed for Construction Projects | *Developed for Web*")
st.write("---")

# Sidebar: Stock and Summary
with st.sidebar:
    st.header("🏢 Site Summary")
    st.metric("Current Tank Stock", f"{st.session_state.tank_stock:.2f} L")
    
    st.write("---")
    
    if st.button("Reset Stock (Testing Only)"):
        st.session_state.tank_stock = DEFAULT_STOCK
        st.rerun()

    if st.button("Generate Download Link"):
        if st.session_state.data:
            df_final = pd.DataFrame(st.session_state.data)
            filename = f"HSD_Report_{datetime.now().strftime('%Y%m%d_%H%M')}.xlsx"
            df_final.to_excel(filename, index=False)
            with open(filename, "rb") as file:
                st.download_button(
                    label="📥 Click to Download Excel",
                    data=file,
                    file_name=filename,
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
        else:
            st.warning("No data entries to export.")

# Main Input Section
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        machine = st.selectbox("Select Machine", MACHINES)
        mtype = st.selectbox("Type", TYPES)
        avg = st.number_input("Average Consumption (L/H or L/KM)", min_value=0.0, step=0.1, format="%.2f")
        
        # Auto-fetch previous reading
        db_df = load_db()
        last_val = db_df.loc[db_df["Machine"] == machine, "Last_Reading"].values
        prv = last_val[0] if len(last_val) > 0 else 0.0
        
        entry_prv = st.number_input("Previous Reading (PRV)", value=float(prv), step=0.01)

    with col2:
        entry_curr = st.number_input("Current Reading (CURR)", min_value=0.0, step=1.0)
        entry_fill = st.number_input("Diesel Fill (FILL) - Liters", min_value=0.0, step=1.0)
        remark = st.text_input("Remarks", placeholder="Site location, shift, etc.")

    # Calculations
    hmr = entry_curr - entry_prv
    cons = hmr * avg

    st.info(f"💡 **Calculated HMR:** {hmr:.2f} | **Calculated Consumption:** {cons:.2f} L")

    if st.button("➕ Add Entry to Log", use_container_width=True):
        if entry_curr < entry_prv:
            st.error("❌ Error: Current reading cannot be less than previous.")
        elif entry_curr == 0 and entry_prv == 0:
            st.error("❌ Please enter valid reading data.")
        else:
            # Check Alert
            expected = avg * hmr
            if cons > expected * 1.2:
                st.warning("⚠️ ALERT: High Diesel Consumption Detected!")
            elif cons < expected * 0.5 and hmr > 0:
                st.warning("⚠️ ALERT: Check Reading Data - Unusually Low Consumption.")

            # Append data
            row = {
                "Machine": machine, "Type": mtype, "AVG": avg, 
                "PRV": entry_prv, "CURR": entry_curr, "HMR": hmr, 
                "CONS": cons, "FILL": entry_fill, "REMARK": remark
            }
            st.session_state.data.append(row)
            
            # Update DB and Stock
            update_db(machine, entry_curr)
            st.session_state.tank_stock = st.session_state.tank_stock + entry_fill - cons
            
            st.success(f"✅ Entry for {machine} added successfully!")
            st.rerun()

# ---------------- DISPLAY TABLE ----------------
st.write("---")
st.subheader("📋 Daily Log")
if st.session_state.data:
    df_display = pd.DataFrame(st.session_state.data)
    st.dataframe(df_display, use_container_width=True)
else:
    st.info("No entries recorded for this session yet.")
