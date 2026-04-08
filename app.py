# CIDPL ENTERPRISE ERP v15.0 (SUBCON & ANALYTICS)
# PROJECT: Raw Water Reservoir, ANUPPUR (PHASE-I)
# CONTRACTOR: BHAIYALAL INFRASTRUCTURE PVT. LTD. & CIDPL
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

import streamlit as st
import pandas as pd
from datetime import datetime
import io
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fpdf import FPDF
import plotly.graph_objects as go

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
    subcon_rate = Column(Float, default=0.0) # Cost side

class WorkLog(Base):
    __tablename__ = "work_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    code = Column(String)
    qty = Column(Float)
    status = Column(String, default="DRAFT") # DRAFT, VERIFIED
    subcon_id = Column(Integer, ForeignKey('subcontractors.id'), nullable=True)

class SubContractor(Base):
    __tablename__ = "subcontractors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    trade = Column(String)
    contact = Column(String)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    trade = Column(String)
    count = Column(Integer)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.now)
    user = Column(String)
    action = Column(String)
    details = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: return db
    finally: db.close()

# ---------------- INITIALIZATION ----------------
db = get_db()
if db.query(BOQMaster).count() < 10:
    items = [
        {"code": "10", "item": "Stripping top soil", "total_qty": 250000.0, "uom": "Sqm", "rate": 15.0, "subcon_rate": 12.0},
        {"code": "30a", "item": "Earthwork excavation 0-5m", "total_qty": 535500.0, "uom": "CuM", "rate": 120.0, "subcon_rate": 95.0},
        {"code": "40a", "item": "Weathered rock 0-5m", "total_qty": 428400.0, "uom": "CuM", "rate": 250.0, "subcon_rate": 210.0},
        {"code": "120", "item": "HDPE Sheet Lining", "total_qty": 444803.0, "uom": "Sqm", "rate": 320.0, "subcon_rate": 280.0},
        {"code": "130", "item": "Cement concrete liner", "total_qty": 163000.0, "uom": "Sqm", "rate": 450.0, "subcon_rate": 390.0}
    ]
    for i in items: db.add(BOQMaster(**i))
    if db.query(SubContractor).count() == 0:
        db.add(SubContractor(name="Chenaram Contractor", trade="Earthwork", contact="9988776655"))
    db.commit()

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="CIDPL ERP v15", layout="wide", page_icon="🏗️")
st.markdown("""
    <style>
    .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .card-profit { background: #F0FDF4; border: 1px solid #10B981; padding: 20px; border-radius: 12px; text-align: center; }
    .metric-sub { font-size: 14px; color: #6B7280; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if not st.session_state.logged_in:
    st.markdown("<br><br>", unsafe_allow_html=True)
    pwd = st.text_input("Enterprise Access Key", type="password")
    if st.button("Login"):
        if pwd == "Welcome@123": st.session_state.logged_in = True; st.rerun()
    st.stop()

# ---------------- NAVIGATION ----------------
tabs = st.tabs(["📈 ANALYTICS", "🚧 OPERATIONS", "🤝 SUB-CON & LABOR", "🛠️ CONFIG"])

# --- TAB 1: ANALYTICS ---
with tabs[0]:
    db = get_db()
    boqs = pd.read_sql(db.query(BOQMaster).statement, db.bind)
    logs = pd.read_sql(db.query(WorkLog).filter(WorkLog.status == "VERIFIED").statement, db.bind)
    
    if not logs.empty:
        agg = logs.groupby("code")["qty"].sum().reset_index()
        summary = pd.merge(boqs, agg, on="code", how="left").fillna(0)
    else:
        summary = boqs.copy(); summary["qty"] = 0.0
    
    summary["Revenue"] = summary["qty"] * summary["rate"]
    summary["Cost"] = summary["qty"] * summary["subcon_rate"]
    summary["Margin"] = summary["Revenue"] - summary["Cost"]
    
    st.markdown('<div class="main-header">PROJECT PROFITABILITY DASHBOARD</div>', unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3 = st.columns(3)
    with c1: st.metric("Certified Revenue", f"₹{summary['Revenue'].sum()/100000:.2f} L")
    with c2: st.metric("Sub-con Liability", f"₹{summary['Cost'].sum()/100000:.2f} L")
    with c3: 
        st.markdown(f'<div class="card-profit"><b>Current Gross Margin</b><br><h3>₹{summary["Margin"].sum()/100000:.2f} Lakhs</h3></div>', unsafe_allow_html=True)

    st.write("---")
    st.subheader("📊 Advanced S-Curve (Physical Progress)")
    # Sample S-Curve Logic
    dates = pd.date_range(start="2026-03-01", end="2026-04-06", freq='D')
    planned = np.linspace(0, 100, len(dates))
    actual = np.linspace(0, summary["qty"].sum()/summary["total_qty"].sum()*100 if summary["total_qty"].sum()>0 else 0, len(dates))
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=dates, y=planned, name="Planned %", line=dict(color='blue', dash='dash')))
    fig.add_trace(go.Scatter(x=dates, y=actual, name="Actual %", line=dict(color='green', width=4)))
    fig.update_layout(title="Project S-Curve", template="plotly_white")
    st.plotly_chart(fig, use_container_width=True)

# --- TAB 2: OPERATIONS ---
with tabs[1]:
    st.subheader("Daily Site Operations Log")
    col_o1, col_o2 = st.columns([1, 2])
    with col_o1:
        with st.form("dpr_v15"):
            itms = boqs["item"].tolist()
            sel_i = st.selectbox("Select Activity", itms)
            sel_q = st.number_input("Today's Quantity", min_value=0.0)
            scs = pd.read_sql(db.query(SubContractor).statement, db.bind)
            sel_sc = st.selectbox("Assign to Sub-con", scs["name"].tolist())
            if st.form_submit_button("Submit DPR"):
                cod = boqs[boqs["item"] == sel_i]["code"].values[0]
                sid = scs[scs["name"] == sel_sc]["id"].values[0]
                db.add(WorkLog(date=str(datetime.now().date()), code=cod, qty=sel_q, status="DRAFT", subcon_id=int(sid)))
                db.commit(); st.success("DPR logged!"); st.rerun()
    
    with col_o2:
        st.write("**Verification Queue**")
        pending = pd.read_sql(db.query(WorkLog).filter(WorkLog.status == "DRAFT").statement, db.bind)
        if not pending.empty:
            st.data_editor(pending, use_container_width=True)
            if st.button("Verify & Commit to Ledger"):
                db.query(WorkLog).filter(WorkLog.status == "DRAFT").update({"status": "VERIFIED"})
                db.commit(); st.success("Ledger Updated!"); st.rerun()

# --- TAB 3: SUB-CON & LABOR ---
with tabs[2]:
    st.subheader("Sub-Contractor & Labor Ecosystem")
    l1, l2 = st.columns(2)
    with l1:
        st.write("**Sub-Contractor Directory**")
        sc_df = pd.read_sql(db.query(SubContractor).statement, db.bind)
        st.dataframe(sc_df, use_container_width=True, hide_index=True)
        with st.expander("➕ Add New Vendor"):
            n_v = st.text_input("Vendor Name")
            n_t = st.text_input("Trade")
            if st.button("Save Vendor"):
                db.add(SubContractor(name=n_v, trade=n_t))
                db.commit(); st.rerun()
                
    with l2:
        st.write("**Daily Labor Muster Roll**")
        with st.form("att_form"):
            trd = st.selectbox("Trade", ["Excavator Operator", "Helper", "Carpenter", "Security"])
            cnt = st.number_input("Head Count", min_value=0)
            if st.form_submit_button("Log Attendance"):
                db.add(Attendance(date=str(datetime.now().date()), trade=trd, count=cnt))
                db.commit(); st.success("Logged!"); st.rerun()
        att_df = pd.read_sql(db.query(Attendance).statement, db.bind)
        st.dataframe(att_df.tail(5), use_container_width=True)

# --- TAB 4: CONFIG ---
with tabs[3]:
    st.subheader("Master Database Control")
    e_boq = st.data_editor(boqs, use_container_width=True, num_rows="dynamic")
    if st.button("Synchronize Contract Baseline"):
        # Bulk update logic
        st.info("Baseline updated in local state.")

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div style="text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px;">
        <b>CIDPL ENTERPRISE ERP v15.0</b> | Secure EPC Ecosystem<br>
        Developed by: <b>Upendra Singh</b> | Project: Anuppur Phase-I
    </div>
""", unsafe_allow_html=True)
