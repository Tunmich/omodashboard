import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import json
import pandas as pd
import altair as alt
import streamlit as st
import logging

# 🔌 Load decision logic
from strategy.decision_engine import should_buy

# 🔌 Load modules from utils
from utils.chain_volume import get_chain_volumes
from utils.gas_tracker import get_gas_price
from utils.balance_checker import get_wallet_balance
from utils.solana_balance import get_sol_balance
from utils.trade_routing import select_optimal_chain
# 🔌 Load decision logic
# 🔌 Load decision logic
from strategy.decision_engine import should_buy
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
# 🧾 Past Token Decision Review
# -----------------------------------
st.subheader("🧾 Historical Token Review & Re-Scoring")

try:
    hist_df = pd.read_csv("logs/historical_tokens.csv")
    hist_df["Re-evaluated"] = hist_df.apply(lambda row: should_buy(dict(row)), axis=1)

    # 🔍 Search bar for token name
    search_term = st.text_input("🔍 Search by Token Name", "")
    if search_term:
        hist_df = hist_df[hist_df["name"].str.contains(search_term, case=False)]

    # ✅ Filter to show only tokens that now pass
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
# 🏆 ROI Leaderboard for Confirmed Trades
# -----------------------------------
st.subheader("🏆 Confirmed Trades ROI Leaderboard")

try:
    df = pd.read_csv("logs/trades.csv")
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])
    df["Date"] = df["Timestamp"].dt.date

    roi_df = df.sort_values(by="ROI", ascending=False)
    roi_df["P/L ($)"] = roi_df["estimated_pl"]

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
except Exception:
    st.info("📦 No confirmed trades found yet.")

# -----------------------------------
# 📈 Performance Charts
# -----------------------------------
st.subheader("📊 Profit & ROI Performance")

try:
    # P/L Timeline
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

    # Chain Summary
    chain_summary = df.groupby("chain")["P/L ($)"].sum().sort_values(ascending=False).reset_index()
    st.subheader("🚀 Chain Profit Summary")
    st.dataframe(chain_summary.rename(columns={"chain": "Chain", "P/L ($)": "Total Profit"}))

    # Daily ROI Trend
    roi_trend = df.groupby("Date")["ROI"].mean().reset_index()
    st.subheader("📈 Daily Average ROI")
    st.line_chart(roi_trend.set_index("Date"))

except Exception as e:
    st.warning(f"⚠️ Error loading performance charts: {e}")

    # -----------------------------------
# 💡 Simulated Token Profit Analysis
# -----------------------------------
st.subheader("🧪 Simulated Token Profit/Loss Estimates")

try:
    with open("pl_simulated_results.json", "r") as sim_file:
        sim_tokens = json.load(sim_file)

    sim_df = pd.DataFrame(sim_tokens)
    sim_df["Estimated_Value"] = sim_df["estimated_return"] * sim_df["token_price_usd"]
    sim_df["P/L ($)"] = sim_df["Estimated_Value"] - sim_df["trade_amount_usd"]

    # 🔍 Search bar
    sim_search = st.text_input("🔍 Search simulated token", "")
    if sim_search:
        sim_df = sim_df[sim_df["name"].str.contains(sim_search, case=False)]

    # 🏆 Display table
    st.dataframe(
        sim_df[["name", "chain", "estimated_return", "token_price_usd", "Estimated_Value", "P/L ($)"]]
        .rename(columns={
            "name": "Token",
            "chain": "Chain",
            "estimated_return": "Est. Token Output",
            "token_price_usd": "Price ($)",
            "Estimated_Value": "Market Value ($)",
            "P/L ($)": "Est. Profit/Loss"
        })
        .sort_values(by="P/L ($)", ascending=False),
        use_container_width=True
    )

    # 📊 Optional: Bar chart of top P/L
    st.subheader("📊 Top Simulated P/L Estimates")
    top_sim = sim_df.sort_values(by="P/L ($)", ascending=False).head(10)
    chart = alt.Chart(top_sim).mark_bar().encode(
        x="Token:N",
        y="P/L ($):Q",
        color="Chain:N",
        tooltip=["Token", "Chain", "P/L ($)", "Estimated_Value"]
    ).properties(height=300)
    st.altair_chart(chart, use_container_width=True)

except Exception as e:
    st.warning(f"⚠️ Could not load simulated token results: {e}")
# -----------------------------------
# 🛠️ Utility Functions
# -----------------------------------
# 📜 Unified Terminal Log Viewer
# -----------------------------------
import os, re
import os

LOG_FILE = os.path.join("logs", "terminal_log.txt")

st.subheader("📜 Terminal Log Stream")

# 🔁 Read log file safely
def read_logs(file_path):
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r") as f:
        return f.readlines()

# 🔍 Parse log entries
def parse_logs(lines):
    entries = []
    for line in lines:
        match = re.search(r"(INFO|WARNING|ERROR).*?— (.*)", line)
        if match:
            level = match.group(1)
            message = match.group(2)
            timestamp = line.split("—")[0].strip()
            entries.append({"Time": timestamp, "Level": level, "Message": message})
    return pd.DataFrame(entries)

try:
    log_lines = read_logs(LOG_FILE)
    log_df = parse_logs(log_lines)

    # 🔄 Refresh button
    if st.button("🔄 Refresh Log Stream"):
        st.experimental_rerun()

    # 📋 Display full log table
    st.dataframe(log_df.tail(50), use_container_width=True)

    # ⚠️ Error + warning highlights
    st.subheader("⚠️ Alerts Summary")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Warnings", len(log_df[log_df["Level"] == "WARNING"]))
    with col2:
        st.metric("Errors", len(log_df[log_df["Level"] == "ERROR"]))

except Exception as e:
    st.warning(f"⚠️ Could not load terminal logs: {e}")