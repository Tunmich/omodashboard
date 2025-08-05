import sys
import os
import pandas as pd
import altair as alt
import streamlit as st
from dotenv import load_dotenv

# ✅ Cached CSV loaders
@st.cache_data(ttl=300)
def load_historical_tokens():
    return pd.read_csv("logs/historical_tokens.csv", engine="python")

@st.cache_data(ttl=300)
def load_trade_logs():
    return pd.read_csv("logs/trades.csv")

# ✅ Load environment variables
load_dotenv()
sol_address = os.getenv("SOLANA_WALLET")
raw_key = os.getenv("WALLET_PRIVATE_KEY")
LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))

# 🔧 Fix Python path to find project modules
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)
sys.path.append(os.path.join(BASE_DIR, 'strategy'))

# 🔐 Wallet setup
from solders.keypair import Keypair
from utils.solana_balance import get_sol_balance
wallet = Keypair.from_base58_string(raw_key)
sol_balance = get_sol_balance(wallet.pubkey())

# 🔌 Core modules
from strategy.trade_decision_engine import should_buy
from utils.wallet_mapper import phantom_to_evm
from utils.chain_volume import get_chain_volumes
from utils.gas_tracker import get_gas_price
from utils.balance_checker import get_wallet_balance
from utils.trade_routing import select_optimal_chain
from modules.sniper_engine import scan_and_evaluate
from utils.csv_loader import load_trade_logs, load_historical_tokens

df_trades = load_trade_logs()
df_tokens = load_historical_tokens()

# 🧠 UI Config
st.set_page_config(page_title="OMO Dashboard", layout="wide")
st.title("Tunmich omodashboard")

# 🔐 Wallet display
st.sidebar.markdown("### 🔐 EVM Wallet")
if sol_address:
    try:
        evm_wallet = phantom_to_evm(sol_address)
        st.sidebar.code(evm_wallet, language='text')
    except Exception as e:
        st.sidebar.warning(f"⚠️ Failed to inject EVM wallet: {e}")
else:
    st.sidebar.info("⚠️ SOLANA_WALLET not found in .env")

# 🚨 Balance alert
if sol_balance < LOW_BALANCE_ALERT:
    st.sidebar.error(f"⚠️ LOW SOL Balance: {sol_balance:.5f}")
else:
    st.sidebar.success(f"💰 SOL Balance: {sol_balance:.5f} SOL")

# 🧬 Sniper scan trigger
if st.sidebar.button("🧬 Run Sniper CA Scan"):
    try:
        scan_and_evaluate()
        st.success("✅ Sniper CA Scan completed.")
    except Exception as e:
        st.error(f"❌ Sniper scan failed: {e}")
    st.experimental_rerun()

# 🧠 Chain metrics
st.sidebar.subheader("🧠 Chain Metrics Snapshot")
volumes = get_chain_volumes()
gas_prices = {c: get_gas_price(c) for c in volumes}
balances = {c: get_wallet_balance(c) for c in volumes}

for c in volumes:
    st.sidebar.markdown(f"**{c}**")
    st.sidebar.write(f"🌊 Volume: ${volumes[c]:,.0f}")
    st.sidebar.write(f"⛽ Gas: {gas_prices.get(c, 'N/A')} Gwei")
    st.sidebar.write(f"💰 Balance: {balances.get(c, 0):.5f}")

st.sidebar.markdown(f"### 🟢 Preferred Chain → `{select_optimal_chain()}`")

# 🧾 Historical scoring
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

# 📁 Upload + scoring
uploaded_file = st.file_uploader("📁 Upload Token CSV for Live Scoring", type=["csv"])
if uploaded_file:
    try:
        df = pd.read_csv(uploaded_file)
        df["Re-evaluated"] = df.apply(lambda row: should_buy(dict(row)), axis=1)
        st.dataframe(df)
    except Exception as e:
        st.error(f"❌ Failed to process uploaded file: {e}")

# 📈 ROI leaderboard
st.subheader("📈 Trade ROI Leaderboard")
try:
    roi_df = load_trade_logs()
    roi_df["Estimated_Payout_Score"] = pd.to_numeric(
        roi_df["Estimated_Payout"].astype(str)
        .str.replace("%", "").str.replace("Pending", "").str.strip(), errors="coerce")

    st.dataframe(
        roi_df.sort_values("Estimated_Payout_Score", ascending=False)[
            ["Token", "Chain", "Amount_ETH", "Estimated_Payout", "Tx_Link", "Status"]
        ],
        use_container_width=True
    )
except Exception as e:
    st.warning(f"⚠️ Could not load ROI leaderboard: {e}")

# 🏆 Confirmed ROI trades
st.subheader("🏆 Confirmed Trades ROI Leaderboard")
try:
    df = load_trade_logs()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Date"] = df["Timestamp"].dt.date
    df["P/L ($)"] = pd.to_numeric(df["estimated_pl"], errors="coerce")
    df["ROI"] = pd.to_numeric(df["ROI"], errors="coerce")

    st.dataframe(df.sort_values("ROI", ascending=False)[["name", "chain", "ROI", "estimated_return", "estimated_value", "P/L ($)"]]
        .rename(columns={"name": "Token", "chain": "Chain", "estimated_return": "$1 Output",
                         "estimated_value": "Market Value", "P/L ($)": "Profit/Loss"}),
        use_container_width=True)
except Exception as e:
    st.info(f"📦 No confirmed trades found yet. ({e})")

# 📊 ROI charts
st.subheader("📊 Profit & ROI Performance")
try:
    pl_chart = alt.Chart(df).mark_bar().encode(
        x="Timestamp:T", y="P/L ($):Q",
        tooltip=["name", "chain", "P/L ($)", "ROI"]
    ).properties(title="📆 P/L by Trade Timestamp", width=800, height=300)
    st.altair_chart(pl_chart, use_container_width=True)

    chain_summary = df.groupby("chain")["P/L ($)"].sum().reset_index()
    st.subheader("🚀 Chain Profit Summary")
    st.dataframe(chain_summary.rename(columns={"chain": "Chain", "P/L ($)": "Total Profit"}))

    roi_trend = df.groupby("Date")["ROI"].mean().reset_index()
    st.subheader("📈 Daily Average ROI")
    st.line_chart(roi_trend.set_index("Date"))
except Exception as e:
    st.warning(f"⚠️ Error loading charts: {e}")
