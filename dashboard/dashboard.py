# dashboard/dashboard.py
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import streamlit as st

# 🔌 Load all component renderers
from components.wallet_ui import render_wallet_info, render_chain_metrics
from components.sniper_trigger import render_sniper_trigger
from components.historical_review import render_historical_rescore
from components.upload_scoring import render_upload_and_scoring
from components.roi_leaderboard import render_roi_tables_and_charts
from phantom_connect.phantom_connect import connect_phantom

wallet_address = connect_phantom()

if wallet_address:
    st.sidebar.success(f"🔐 Wallet: {wallet_address}")
else:
    st.sidebar.warning("⚠️ Connect your Phantom wallet.")

# 🧠 UI Config
st.set_page_config(page_title="OMO Dashboard", layout="wide")
st.title("Tunmich omodashboard")

# 📦 Sidebar: Wallet + Chain info
render_wallet_info()
render_chain_metrics()

# 🔘 Main Panels
render_sniper_trigger()
render_historical_rescore()
render_upload_and_scoring()
render_roi_tables_and_charts()
