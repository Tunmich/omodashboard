import sys
import os
import json
import pandas as pd
import altair as alt
import streamlit as st
import logging
import re
from modules.sniper_sniff import scan_and_evaluate

if st.sidebar.button("🧬 Run Sniper CA Scan"):
    scan_and_evaluate()

# 🔧 Add both parent and strategy folder to sys.path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
STRATEGY_DIR = os.path.join(BASE_DIR, 'strategy')
sys.path.append(BASE_DIR)
sys.path.append(STRATEGY_DIR)

# 🔌 Load decision logic and modules
from strategy.decision_engine import should_buy
from utils.chain_volume import get_chain_volumes
from utils.gas_tracker import get_gas_price
from utils.balance_checker import get_wallet_balance
from utils.solana_balance import get_sol_balance
from utils.trade_routing import select_optimal_chain

# 🧾 Load logs
LOG_FILE = os.path.join("logs", "terminal_log.txt")

st.set_page_config(page_title="OMO Dashboard", layout="wide")

# -----------------------------------
# 🧠 Sidebar: Smart Chain Metrics
# -----------------------------------
st.sidebar.subheader("🧠 Chain Metrics Snapshot")
volumes = get_chain_volumes()
gas_prices = {chain: get_gas_price(chain) for chain in volumes}
balances = {chain: get_wallet_balance(chain) for chain in volumes}
sol_balance = get_sol_balance()

for chain in volumes:
    st.sidebar.markdown(f"**{chain}**")
    st.sidebar.write(f"🌊 Volume: ${volumes[chain]:,.0f}")
    st.sidebar.write(f"⛽ Gas: {gas_prices.get(chain, 'N/A')} Gwei")
    st.sidebar.write(f"💰 Balance: {balances.get(chain, 0):.5f}")

st.sidebar.markdown("**Solana**")
st.sidebar.write(f"🌊 Volume: ${volumes.get('Solana', 0):,.0f}")
st.sidebar.write("⛽ Gas: negligible")
st.sidebar.write(f"💰 Balance: {sol_balance:.5f} SOL")

best_chain = select_optimal_chain()
st.sidebar.markdown(f"### 🟢 Preferred Chain → `{best_chain}`")

# -----------------------------------
# 🧾 Historical Token Review & Re-Scoring
# -----------------------------------
st.subheader("🧾 Historical Token Review & Re-Scoring")

try:
    hist_df = pd.read_csv("logs/historical_tokens.csv", engine="python")
    hist_df["Re-evaluated"] = hist_df.apply(lambda row: should_buy(dict(row)), axis=1)

    search_term = st.text_input("🔍 Search by Token Name", "")
    if search_term:
        hist_df = hist_df[hist_df["name"].str.contains(search_term, case=False)]

    show_pass_only = st.checkbox("✅ Show only tokens that now pass decision logic", value=False)
    if show_pass_only:
        hist_df = hist_df[hist_df["Re-evaluated"] == True]

    st.dataframe(
        hist_df[["name", "chain", "buzz_score", "risk_score", "estimated_return", "token_price_usd", "Re-evaluated"]]
        .rename(columns={
            "name": "Token",
            "chain": "Chain",
            "buzz_score": "Buzz",
            "risk_score": "Risk",
            "estimated_return": "$1 Output",
            "token_price_usd": "Price ($)",
            "Re-evaluated": "Passes Now"
        }),
        use_container_width=True
    )

except Exception as e:
    st.warning(f"⚠️ Could not load historical token log: {e}")

# -----------------------------------
# 📈 Trade ROI Leaderboard (Estimated Payout Focus)
# -----------------------------------
st.subheader("📈 Trade ROI Leaderboard")

try:
    roi_df = pd.read_csv("logs/trades.csv")

    if "Estimated_Payout" in roi_df.columns and "Token" in roi_df.columns:
        roi_df["Estimated_Payout_Score"] = (
            roi_df["Estimated_Payout"]
            .astype(str)
            .str.replace("%", "", regex=False)
            .str.replace("Pending", "", regex=False)
            .str.strip()
        )
        roi_df["Estimated_Payout_Score"] = pd.to_numeric(roi_df["Estimated_Payout_Score"], errors="coerce")

        st.dataframe(
            roi_df.sort_values(by="Estimated_Payout_Score", ascending=False)[
                ["Token", "Chain", "Amount_ETH", "Estimated_Payout", "Tx_Link", "Status"]
            ],
            use_container_width=True
        )
    else:
        st.info("📭 No Estimated_Payout or Token data found in trades.csv.")

except Exception as e:
    st.warning(f"⚠️ Could not load ROI leaderboard: {e}")

# -----------------------------------
# 🏆 Confirmed Trades ROI Leaderboard
# -----------------------------------
st.subheader("🏆 Confirmed Trades ROI Leaderboard")

try:
    df = pd.read_csv("logs/trades.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], format='mixed', dayfirst=True, errors='coerce')
    df["Date"] = df["Timestamp"].dt.date
    df["P/L ($)"] = pd.to_numeric(df["estimated_pl"], errors="coerce")
    roi_df = df.sort_values(by="ROI", ascending=False)

    st.dataframe(
        roi_df[["name", "chain", "ROI", "estimated_return", "estimated_value", "P/L ($)"]]
        .rename(columns={
            "name": "Token",
            "chain": "Chain",
            "estimated_return": "$1 Output",
            "estimated_value": "Market Value",
            "P/L ($)": "Profit/Loss"
        }),
        use_container_width=True
    )

except Exception as e:
    st.info(f"📦 No confirmed trades found yet. ({e})")

# -----------------------------------
# 📊 Profit & ROI Performance
# -----------------------------------
st.subheader("📊 Profit & ROI Performance")

try:
    df["P/L ($)"] = pd.to_numeric(df["estimated_pl"], errors="coerce")
    df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")

    pl_chart = alt.Chart(df).mark_bar().encode(
        x="Timestamp:T",
        y="P/L ($):Q",
        tooltip=["name", "chain", "P/L ($)", "ROI"]
    ).properties(
        title="📆 P/L by Trade Timestamp",
        width=800,
        height=300
    )
    st.altair_chart(pl_chart, use_container_width=True)

    chain_summary = df.groupby("chain")["P/L ($)"].sum().reset_index()
    st.subheader("🚀 Chain Profit Summary")
    st.dataframe(chain_summary.rename(columns={"chain": "Chain", "P/L ($)": "Total Profit"}))

    roi_trend = df.groupby("Date")["ROI"].mean().reset_index()
    st.subheader("📈 Daily Average ROI")
    st.line_chart(roi_trend.set_index("Date"))

except Exception as e:
    st.warning(f"⚠️ Error loading performance charts: {e}")

# -----------------------------------
# 🧪 Simulated Token Profit/Loss Estimates
# -----------------------------------
# -----------------------------------
# 📊 Top Simulated P/L Estimates
# -----------------------------------
st.subheader("📊 Top Simulated P/L Estimates")
try:
    top_sim = sim_df.sort_values(by="Est. Profit/Loss", ascending=False).head(10)

    chart = alt.Chart(top_sim).mark_bar().encode(
        x=alt.X("Token:N", title="Token"),
        y=alt.Y("Est. Profit/Loss:Q", title="Estimated Profit ($)"),
        color="Chain:N",
        tooltip=["Token", "Chain", "Est. Profit/Loss", "Market Value ($)"]
    ).properties(
        height=300,
        width=700,
        title="🔝 Top Simulated Profit Estimates"
    )

    st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not generate simulated profit chart: {e}")