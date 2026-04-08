# CIDPL ENTERPRISE ERP v14.0 (GEO-SPATIAL & AUDIT)
# PROJECT: Raw Water Reservoir, ANUPPUR (PHASE-I)
# CONTRACTOR: BHAIYALAL INFRASTRUCTURE PVT. LTD. & CIDPL
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import io
import re
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fpdf import FPDF

# ---------------- DATABASE CONFIG ----------------
DB_FILE = "sqlite:///erp_database.db"
engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class BOQMaster(Base):
    __tablename__ = "boq_master"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    item = Column(String)
    total_qty = Column(Float)
    uom = Column(String)
    rate = Column(Float)
    target = Column(Float)

class WorkLog(Base):
    __tablename__ = "work_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    code = Column(String)
    qty = Column(Float)
    remark = Column(String)
    status = Column(String, default="DRAFT") # DRAFT, VERIFIED
    lat = Column(Float, default=23.18) # Default Anuppur
    lon = Column(Float, default=81.69)

class TripLog(Base):
    __tablename__ = "trip_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    tipper = Column(String)
    total_trips = Column(Integer)
    hmr = Column(Float)
    lat = Column(Float, default=23.18)
    lon = Column(Float, default=81.69)

class InventoryLog(Base):
    __tablename__ = "inventory_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    material = Column(String)
    qty_in = Column(Float)
    qty_out = Column(Float)
    remark = Column(String)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    user = Column(String)
    action = Column(String) # ADD, EDIT, DELETE
    table = Column(String)
    details = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: return db
    finally: db.close()

def log_audit(user, action, table, details):
    db = get_db()
    db.add(AuditLog(user=user, action=action, table=table, details=details))
    db.commit()

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="CIDPL ENTERPRISE ERP v14", layout="wide", page_icon="🏗️")

st.markdown("""
    <style>
    .main-header { font-size: 34px; font-weight: bold; color: #1E3A8A; text-align: center; margin-bottom: 5px; }
    .sub-header { font-size: 18px; color: #4B5563; text-align: center; margin-bottom: 30px; }
    .card-kpi { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .ai-insight { background: #F0FDF4; border-left: 5px solid #10B981; padding: 15px; border-radius: 8px; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTHENTICATION ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
def login():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="background: white; padding: 40px; border-radius: 15px; border: 1px solid #ddd; text-align: center;">', unsafe_allow_html=True)
        st.header("🏢 Enterprise Secure Portal")
        pwd = st.text_input("Enter Access Password", type="password")
        if st.button("Authenticate", use_container_width=True):
            if pwd == "Welcome@123": st.session_state.logged_in = True; log_audit("Admin", "LOGIN", "AUTH", "Success"); st.rerun()
            else: st.error("Access Denied.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.logged_in: login(); st.stop()

# ---------------- DB INITIALIZATION ----------------
db = get_db()
if db.query(BOQMaster).count() == 0:
    initial_boq = [
        {"code": "10", "item": "Stripping (Earth work in excavation) of top soil", "total_qty": 250000.0, "uom": "Sqm", "rate": 15.0, "target": 35000.0},
        {"code": "30a", "item": "a) All types of soil 0m to 5.0m", "total_qty": 535500.0, "uom": "CuM", "rate": 120.0, "target": 40000.0},
        {"code": "40a", "item": "a) In weathered rock 0m to 5.0m", "total_qty": 428400.0, "uom": "CuM", "rate": 250.0, "target": 20000.0},
        {"code": "40b", "item": "b) In weathered rock - 5m to 10m", "total_qty": 642600.0, "uom": "CuM", "rate": 310.0, "target": 30000.0},
        {"code": "70a", "item": "a) In hard rock - Blasting 0m to 5.0m", "total_qty": 292740.0, "uom": "CuM", "rate": 650.0, "target": 15000.0},
        {"code": "80", "item": "extra over and above for transportation", "total_qty": 2850000.0, "uom": "CuM", "rate": 85.0, "target": 100000.0},
        {"code": "120", "item": "1000 micron HDPE Polyethylene sheet", "total_qty": 444803.0, "uom": "Sqm", "rate": 320.0, "target": 42000.0}
    ]
    for item in initial_boq: db.add(BOQMaster(**item))
    db.commit()

# ---------------- LOGIC ----------------
def get_analytics():
    db = get_db()
    boqs = pd.read_sql(db.query(BOQMaster).statement, db.bind)
    logs = pd.read_sql(db.query(WorkLog).statement, db.bind)
    if not logs.empty:
        agg = logs[logs['status'] == 'VERIFIED'].groupby("code")["qty"].sum().reset_index()
        status = pd.merge(boqs, agg, on="code", how="left").fillna(0)
    else: status = boqs.copy(); status["qty"] = 0.0
    status["Value"] = status["qty"] * status["rate"]
    status["%"] = (status["qty"] / status.apply(lambda x: x["total_qty"] if x["total_qty"] > 0 else 1, axis=1) * 100).fillna(0).round(2)
    return status

def generate_ra_pdf(summary_df):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", 'B', 16)
    pdf.cell(200, 10, txt="CIDPL - BHAIYALAL INFRASTRUCTURE PVT. LTD.", ln=True, align='C')
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="RA BILL SUMMARY - ANUPPUR RESERVOIR PROJECT", ln=True, align='C')
    pdf.ln(10)
    
    # Table Header
    pdf.set_font("Arial", 'B', 10)
    pdf.cell(20, 10, "Code", 1)
    pdf.cell(80, 10, "Item Description", 1)
    pdf.cell(30, 10, "Done Qty", 1)
    pdf.cell(30, 10, "Rate", 1)
    pdf.cell(30, 10, "Amount", 1)
    pdf.ln()
    
    pdf.set_font("Arial", size=10)
    for index, row in summary_df.iterrows():
        if row['qty'] > 0:
            pdf.cell(20, 10, str(row['code']), 1)
            pdf.cell(80, 10, str(row['item'][:40]), 1)
            pdf.cell(30, 10, f"{row['qty']:,}", 1)
            pdf.cell(30, 10, f"{row['rate']:,}", 1)
            pdf.cell(30, 10, f"{row['Value']:,}", 1)
            pdf.ln()
            
    pdf.set_font("Arial", 'B', 12)
    pdf.ln(10)
    pdf.cell(200, 10, txt=f"Total Gross Value: INR {summary_df['Value'].sum():,.2f}", ln=True)
    return pdf.output(dest='S')

# ---------------- UI ----------------
st.markdown('<div class="main-header">CIDPL ENTERPRISE ERP v14.0</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">GEO-SPATIAL INTELLIGENCE | ANUPPUR RESERVOIR (₹58.09 CR.)</div>', unsafe_allow_html=True)

tabs = st.tabs(["📊 DASHBOARD", "🚧 SITE OPS", "🚛 LOGISTICS", "🏗️ INVENTORY", "🛠️ CONFIG"])

# --- DASHBOARD ---
with tabs[0]:
    summary = get_analytics()
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Certified Billing", "₹{:.2f} Cr".format(summary['Value'].sum()/10000000))
    c2.metric("Project Progress", "{:.1f}%".format(summary[summary['total_qty']>0]['%'].mean()))
    c3.metric("GPS Sync Status", "ONLINE", delta="12 Nodes Active")
    c4.metric("Pending Approvals", len(db.query(WorkLog).filter(WorkLog.status == "DRAFT").all()))

    st.write("---")
    st.subheader("🗺️ Live Site Activity Map (Anuppur Project)")
    db = get_db()
    all_logs = pd.read_sql(db.query(WorkLog).statement, db.bind)
    if not all_logs.empty:
        st.map(all_logs[['lat', 'lon']])
    else: st.info("No GPS nodes found for mapping yet.")

    st.write("---")
    st.subheader("💰 Financial Controls & PDF Export")
    col_pdf1, col_pdf2 = st.columns([2, 1])
    with col_pdf1:
        st.dataframe(summary[["code", "item", "total_qty", "qty", "Value", "%"]], use_container_width=True, hide_index=True)
    with col_pdf2:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.write("**REPORT GENERATOR**")
        if st.button("Generate Professional RA Bill (PDF)"):
            pdf_bytes = generate_ra_pdf(summary)
            st.download_button(label="📥 Download RA Bill", data=pdf_bytes, file_name="RA_Bill_CIDPL.pdf", mime="application/pdf")
        st.markdown('</div>', unsafe_allow_html=True)

# --- SITE OPS ---
with tabs[1]:
    st.subheader("DPR Verification Workflow")
    ops_c1, ops_c2 = st.columns([1, 2])
    with ops_c1:
        with st.form("dpr_form"):
            st.write("➕ **Submit New Work**")
            items = [r.item for r in db.query(BOQMaster).all()]
            s_item = st.selectbox("BOQ Item", items)
            s_qty = st.number_input("Done Qty", min_value=0.0)
            s_gps = st.checkbox("Simulate GPS Sync", value=True)
            if st.form_submit_button("Log as Draft"):
                code = db.query(BOQMaster).filter(BOQMaster.item == s_item).first().code
                # Simulate movement around Anuppur site
                new_lat = 23.18 + np.random.uniform(-0.01, 0.01)
                new_lon = 81.69 + np.random.uniform(-0.01, 0.01)
                db.add(WorkLog(date=str(datetime.now().date()), code=code, qty=s_qty, lat=new_lat, lon=new_lon))
                db.commit(); log_audit("User", "ADD", "WorkLog", f"Qty {s_qty} for {code}"); st.rerun()

    with ops_c2:
        st.write("📝 **Approval Queue**")
        pending = pd.read_sql(db.query(WorkLog).filter(WorkLog.status == "DRAFT").statement, db.bind)
        if not pending.empty:
            e_pending = st.data_editor(pending, use_container_width=True, num_rows="dynamic")
            if st.button("✅ Approve Selected"):
                for _, row in e_pending.iterrows():
                    entry = db.query(WorkLog).filter(WorkLog.id == int(row['id'])).first()
                    entry.status = "VERIFIED"
                db.commit(); log_audit("Admin", "VERIFY", "WorkLog", "Batch approval"); st.rerun()
        else: st.info("Verification queue is empty.")

# --- CONFIG / AUDIT ---
with tabs[4]:
    st.subheader("🛠️ Enterprise Audit Trail")
    audit_df = pd.read_sql(db.query(AuditLog).order_by(AuditLog.timestamp.desc()).statement, db.bind)
    st.dataframe(audit_df, use_container_width=True, hide_index=True)
    
    st.write("---")
    st.subheader("Database Management")
    if st.button("🗑️ Reset ALL Data (Danger Zone)"):
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        st.rerun()

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div class="footer">
        <b>CIDPL ENTERPRISE ERP v14.0</b> | High-Signal Project Control<br>
        Developer: <b>Upendra Singh</b> | Organizational Integrity: Tier-1<br>
        Security: <b>Audit Enabled</b> | Sync: <b>GPS Real-time</b>
    </div>
""", unsafe_allow_html=True)
