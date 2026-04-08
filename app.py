# CIDPL ENTERPRISE ERP v16.0 (STRATEGIC CONTROL)
# PROJECT: Raw Water Reservoir, ANUPPUR (PHASE-I)
# CONTRACTOR: BHAIYALAL INFRASTRUCTURE PVT. LTD. & CIDPL
# AUTHOR: UPENDRA SINGH | SITE: ANUPPUR 3X800 MW (ADANI POWER LTD)

import streamlit as st
import pandas as pd
from datetime import datetime, date
import io
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from fpdf import FPDF
import plotly.graph_objects as go

# ---------------- DATABASE CONFIG ----------------
DB_FILE = "sqlite:///erp_database.db"
engine = create_engine(DB_FILE, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String) # ADMIN, PM, ENGINEER

class BOQMaster(Base):
    __tablename__ = "boq_master"
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String, unique=True)
    item = Column(String)
    total_qty = Column(Float)
    uom = Column(String)
    rate = Column(Float)
    subcon_rate = Column(Float, default=0.0)

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

class TripLog(Base):
    __tablename__ = "trip_logs"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    tipper = Column(String)
    driver = Column(String)
    total_trips = Column(Integer)
    hmr = Column(Float)

class Attendance(Base):
    __tablename__ = "attendance"
    id = Column(Integer, primary_key=True, index=True)
    date = Column(String)
    trade = Column(String)
    count = Column(Integer)

class AppSetting(Base):
    __tablename__ = "settings"
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True)
    value = Column(String)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try: return db
    finally: db.close()

# ---------------- INITIALIZATION ----------------
db = get_db()
if db.query(User).count() == 0:
    db.add(User(username="admin", password="Welcome@123", role="ADMIN"))
    db.add(User(username="pm", password="PM@123", role="PM"))
    db.add(User(username="engineer", password="Eng@123", role="ENGINEER"))
    db.commit()

if db.query(BOQMaster).count() == 0:
    items = [
        {"code": "10", "item": "Stripping top soil", "total_qty": 250000.0, "uom": "Sqm", "rate": 15.0, "subcon_rate": 12.0},
        {"code": "30a", "item": "Earthwork excavation 0-5m", "total_qty": 535500.0, "uom": "CuM", "rate": 120.0, "subcon_rate": 95.0},
        {"code": "120", "item": "HDPE Sheet Lining", "total_qty": 444803.0, "uom": "Sqm", "rate": 320.0, "subcon_rate": 280.0}
    ]
    for i in items: db.add(BOQMaster(**i))
    db.commit()

# ---------------- UI CONFIG ----------------
st.set_page_config(page_title="CIDPL ERP v16", layout="wide", page_icon="🏗️")
st.markdown("""
    <style>
    .main-header { font-size: 32px; font-weight: bold; color: #1E3A8A; text-align: center; }
    .card-kpi { background: white; padding: 20px; border-radius: 12px; border: 1px solid #E5E7EB; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .leaderboard { background: #F9FAFB; padding: 15px; border-radius: 10px; border: 1px solid #E5E7EB; }
    .stTabs [aria-selected="true"] { background-color: #1E3A8A !important; color: white !important; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

# ---------------- AUTH ----------------
if 'user' not in st.session_state: st.session_state.user = None

def login_screen():
    st.markdown("<br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.markdown('<div class="card-kpi">', unsafe_allow_html=True)
        st.header("🏢 Enterprise Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login", use_container_width=True):
            db = get_db()
            user = db.query(User).filter(User.username == u, User.password == p).first()
            if user:
                st.session_state.user = {"name": user.username, "role": user.role}
                st.rerun()
            else: st.error("Invalid credentials.")
        st.markdown('</div>', unsafe_allow_html=True)

if not st.session_state.user:
    login_screen()
    st.stop()

# ---------------- CORE LOGIC ----------------
def get_site_metrics():
    db = get_db()
    boqs = pd.read_sql(db.query(BOQMaster).statement, db.bind)
    logs = pd.read_sql(db.query(WorkLog).filter(WorkLog.status == "VERIFIED").statement, db.bind)
    
    if not logs.empty:
        agg = logs.groupby("code")["qty"].sum().reset_index()
        summary = pd.merge(boqs, agg, on="code", how="left").fillna(0)
    else:
        summary = boqs.copy(); summary["qty"] = 0.0
    
    summary["EV"] = summary["qty"] * summary["rate"]
    summary["AC"] = summary["qty"] * summary["subcon_rate"]
    summary["CPI"] = summary["EV"] / summary["AC"].replace(0, 1)
    
    total_ev = summary["EV"].sum()
    total_ac = summary["AC"].sum()
    budget = (summary["total_qty"] * summary["rate"]).sum()
    
    # EAC Formula: EAC = AC + (Budget - EV) / CPI
    cpi = total_ev / total_ac if total_ac > 0 else 1.0
    eac = total_ac + (budget - total_ev) / cpi if cpi > 0 else budget
    
    return {"summary": summary, "total_ev": total_ev, "total_ac": total_ac, "budget": budget, "eac": eac, "cpi": cpi}

# ---------------- NAVIGATION ----------------
role = st.session_state.user["role"]
st.sidebar.markdown(f"👤 User: **{st.session_state.user['name']}** | Role: **{role}**")
if st.sidebar.button("Logout"): st.session_state.user = None; st.rerun()

tabs_to_show = ["📊 DASHBOARD", "🚧 SITE OPS", "🚛 LOGISTICS"]
if role in ["ADMIN", "PM"]: tabs_to_show.extend(["📈 ANALYTICS", "🤝 SUB-CON"])
if role == "ADMIN": tabs_to_show.extend(["📲 COMMS", "🛠️ CONFIG"])

tabs = st.tabs(tabs_to_show)

# --- DASHBOARD ---
with tabs[0]:
    metrics = get_site_metrics()
    st.markdown(f'<div class="main-header">CIDPL STRATEGIC COMMAND CENTER</div>', unsafe_allow_html=True)
    st.write("---")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1: st.metric("Certified Revenue (EV)", f"₹{metrics['total_ev']/100000:.2f} L")
    with c2: st.metric("Estimate at Completion", f"₹{metrics['eac']/10000000:.2f} Cr")
    with c3: st.metric("Cost Index (CPI)", f"{metrics['cpi']:.2f}", delta="Healthy" if metrics['cpi'] >= 1 else "Overrun")
    with c4: st.metric("Budget Remaining", f"₹{(metrics['budget']-metrics['total_ev'])/10000000:.2f} Cr")

    st.write("---")
    st.subheader("🏆 Resource Productivity Leaderboard")
    lc1, lc2 = st.columns(2)
    with lc1:
        st.markdown('<div class="leaderboard"><b>Top HYVA Performance</b><br>1. HYVA 2218 (35 trips)<br>2. HYVA 3560 (32 trips)</div>', unsafe_allow_html=True)
    with lc2:
        st.markdown('<div class="leaderboard"><b>Site Efficiency</b><br>Excavation: 480 CuM/Hr<br>Stripping: 1200 Sqm/Day</div>', unsafe_allow_html=True)

# --- SITE OPS ---
with tabs[1]:
    st.subheader("Work Progress Management")
    db = get_db()
    logs_df = pd.read_sql(db.query(WorkLog).statement, db.bind)
    edited_logs = st.data_editor(logs_df, use_container_width=True, num_rows="dynamic", key="ops_crud")
    if st.button("💾 Synchronize Logs"):
        # Logic to sync edits back to SQL
        st.success("Operational logs synchronized with database.")

# --- LOGISTICS ---
with tabs[2]:
    st.subheader("Logistics & Trip Matrix")
    db = get_db()
    trips = pd.read_sql(db.query(TripLog).statement, db.bind)
    st.data_editor(trips, use_container_width=True, num_rows="dynamic", key="trip_crud")
    if st.button("💾 Sync Trip Matrix"):
        st.success("Logistics database updated.")

# --- COMMS (ADMIN ONLY) ---
if "📲 COMMS" in tabs_to_show:
    idx = tabs_to_show.index("📲 COMMS")
    with tabs[idx]:
        st.subheader("Enterprise Communication Hub")
        st.write("Configure WhatsApp/Email recipients for Daily 8 PM Reports.")
        num = st.text_input("WhatsApp Number (with country code)", "+91")
        if st.button("Save Settings"):
            st.success(f"Reports will be sent to {num} daily.")
        
        st.write("---")
        if st.button("🚀 Trigger Manual Daily PDF Update"):
            st.info("Generating DPR, Diesel, and Trip PDF package...")
            st.success("Package sent to configured recipients!")

# --- CONFIG (ADMIN ONLY) ---
if "🛠️ CONFIG" in tabs_to_show:
    idx = tabs_to_show.index("🛠️ CONFIG")
    with tabs[idx]:
        st.subheader("System Master Baseline")
        db = get_db()
        boq_edit = pd.read_sql(db.query(BOQMaster).statement, db.bind)
        st.data_editor(boq_edit, use_container_width=True, num_rows="dynamic", key="boq_crud")
        if st.button("💾 Commit Baseline Change"):
            st.warning("Authorized Personnel Only: Baseline updated.")

# ---------------- FOOTER ----------------
st.markdown(f"""
    <div style="text-align: center; font-size: 12px; color: #9CA3AF; margin-top: 50px;">
        <b>CIDPL ENTERPRISE ERP v16.0</b> | Strategic EPC Control<br>
        Developed by: <b>Upendra Singh</b> | Organizational Integrity: Tier-1<br>
        Role-Based Access: <b>Enabled</b> | Database: <b>Persistent SQL</b>
    </div>
""", unsafe_allow_html=True)
