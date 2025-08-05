# dashboard/upload_scoring.py
import streamlit as st
import pandas as pd
from strategy.trade_decision_engine import should_buy


def render_upload_and_scoring():
    st.subheader("📁 Upload Token CSV for Live Scoring")
    uploaded_file = st.file_uploader("📁 Upload Token CSV", type=["csv"])
    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)

            required_fields = ['Estimated_Payout', 'estimated_return']
            missing = [field for field in required_fields if field not in df.columns]
            if missing:
                st.warning(f"Missing columns: {', '.join(missing)}")
                st.stop()

            df["Re-evaluated"] = df.apply(lambda row: should_buy(dict(row)), axis=1)
            st.dataframe(df)

        except Exception as e:
            st.error(f"❌ Failed to process uploaded file: {e}")
