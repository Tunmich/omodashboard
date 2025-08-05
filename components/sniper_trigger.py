# dashboard/sniper_trigger.py
import streamlit as st
from modules.sniper_engine import scan_and_evaluate


def render_sniper_trigger():
    st.sidebar.markdown("## 🧬 Sniper Scan")
    if st.sidebar.button("🧬 Run Sniper CA Scan"):
        try:
            scan_and_evaluate()
            st.success("✅ Sniper CA Scan completed.")
        except Exception as e:
            st.error(f"❌ Sniper scan failed: {e}")
        st.rerun()