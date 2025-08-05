import streamlit as st
from utils.wallet_mapper import phantom_to_evm
from utils.solana_balance import get_sol_balance
from utils.chain_volume import get_chain_volumes
from utils.gas_tracker import get_gas_price
from utils.balance_checker import get_wallet_balance
from utils.trade_routing import select_optimal_chain
from solders.keypair import Keypair
import os


def render_wallet_info():
    sol_address = os.getenv("SOLANA_WALLET")
    raw_key = os.getenv("WALLET_PRIVATE_KEY")
    LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))

    st.sidebar.markdown("### 🔐 EVM Wallet")
    if sol_address:
        try:
            evm_wallet = phantom_to_evm(sol_address)
            st.sidebar.code(evm_wallet, language='text')
        except Exception as e:
            st.sidebar.warning(f"⚠️ Failed to inject EVM wallet: {e}")
    else:
        st.sidebar.info("⚠️ SOLANA_WALLET not found in .env")

    if raw_key:
        wallet = Keypair.from_base58_string(raw_key)
        sol_balance = get_sol_balance(wallet.pubkey())
        if sol_balance < LOW_BALANCE_ALERT:
            st.sidebar.error(f"⚠️ LOW SOL Balance: {sol_balance:.5f}")
        else:
            st.sidebar.success(f"💰 SOL Balance: {sol_balance:.5f} SOL")


def render_chain_metrics():
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
