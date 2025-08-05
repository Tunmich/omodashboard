# dashboard/historical_review.py
import streamlit as st
import pandas as pd
from strategy.trade_decision_engine import should_buy
from utils.csv_loader import load_historical_tokens


def render_historical_rescore():
    st.subheader("🧾 Historical Token Review & Re-Scoring")
    try:
        hist_df = load_historical_tokens()
        hist_df["Re-evaluated"] = hist_df.apply(lambda row: should_buy(dict(row)), axis=1)

        term = st.text_input("🔍 Search by Token Name", "")
        if term:
            hist_df = hist_df[hist_df["name"].str.contains(term, case=False)]

        if st.checkbox("✅ Show only tokens that now pass", value=False):
            hist_df = hist_df[hist_df["Re-evaluated"] == True]

        st.dataframe(hist_df[["name", "chain", "buzz_score", "risk_score", "estimated_return", "token_price_usd", "Re-evaluated"]]
            .rename(columns={"name": "Token", "chain": "Chain", "buzz_score": "Buzz", "risk_score": "Risk",
                             "estimated_return": "$1 Output", "token_price_usd": "Price ($)", "Re-evaluated": "Passes Now"}),
            use_container_width=True)
    except Exception as e:
        st.warning(f"⚠️ Could not load token log: {e}")
