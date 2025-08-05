import requests
import time
import logging
import os
import pandas as pd
from dotenv import load_dotenv
from solders.keypair import Keypair

# 🔌 Strategy & Scoring
from strategy.trade_decision_engine import should_buy
from strategy.risk_filter import should_allow_rug

# 🛒 Execution & Alerts
from modules.solana_executor import buy_token_solana
from utils.telegram_bot import send_message, send_trade_alert
from utils.trade_logger import log_trade

# 📊 Metrics & Tracking
from utils.sol_price_feed import fetch_sol_usd_price
from utils.solana_balance import get_sol_balance
from utils.token_scanner import scan_solana_tokens
from utils.token_security import (
    get_token_age, get_creator_wallet, check_token_security,
    is_good_contract, is_bundled_supply
)
from utils.creator_tracker import update_creator_score, get_creator_history_score
from utils.token_tracker import record_token_price
from utils.logger_config import setup_logger
from utils.wallet_mapper import get_safe_evm_wallet
from utils.chain_volume import get_chain_volumes
from utils.balance_checker import get_wallet_balance

# 📈 Budget & Volatility Logic
from utils.budget_manager import (
    get_sol_trade_allocation,
    get_eth_trade_allocation,
    is_trade_allowed,
    get_slippage_tolerance
)
from utils.volatility import get_market_volatility_index

# ✅ Load .env settings
load_dotenv()

# 🔐 Phantom → EVM Wallet Injection
if not os.getenv("EVM_WALLET_ADDRESS"):
    sol_address = os.getenv("WALLET_ADDRESS")
    evm_address = get_safe_evm_wallet(sol_address)
    os.environ["EVM_WALLET_ADDRESS"] = evm_address
    print(f"🔐 EVM wallet injected from Phantom: {evm_address}")

# 🧠 Keypair for signing trades
raw_key = os.getenv("WALLET_PRIVATE_KEY")
wallet = Keypair.from_base58_string(raw_key)

# ⚙️ Config params
USD_PER_TRADE = float(os.getenv("USD_PER_TRADE", "0.20"))
MAX_DAILY_SOL = float(os.getenv("MAX_DAILY_SOL", "0.05"))
LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
RUGCHECK_API_KEY = os.getenv("RUGCHECK_API_KEY")
SAFE_OVERRIDES = os.getenv("SAFE_MINT_OVERRIDES", "").split(",")
MIN_COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "1800"))

last_trade_time = 0
total_sol_spent = 0

logger = setup_logger("sniper")
logger.info("Sniper engine initialized.")

# 🔮 Strategy Execution Logic
def execute_trade_logic(
    wallet_sol_balance: float,
    wallet_eth_balance: float,
    last_trade_time: float,
    current_time: float,
    daily_sol_spent: float,
    market_data: dict
) -> dict:
    if not is_trade_allowed(last_trade_time, current_time, daily_sol_spent):
        return {"action": "skip", "reason": "cooldown_or_daily_limit"}

    volatility_index = get_market_volatility_index(market_data)

    sol_allocation = get_sol_trade_allocation(wallet_sol_balance)
    eth_allocation = get_eth_trade_allocation(wallet_eth_balance)

    if volatility_index > 0.7:
        sol_allocation *= 0.5
        eth_allocation *= 0.5
        aggressiveness = "low"
    elif volatility_index > 0.4:
        sol_allocation *= 0.8
        eth_allocation *= 0.8
        aggressiveness = "medium"
    else:
        aggressiveness = "high"

    return {
        "action": "execute_trade",
        "sol_allocation": round(sol_allocation, 6),
        "eth_allocation": round(eth_allocation, 6),
        "slippage_tolerance": get_slippage_tolerance(),
        "aggressiveness": aggressiveness,
    }

# 🧬 Evaluate historical token log (Streamlit compatible)
def scan_and_evaluate(token_file: str = "logs/historical_tokens.csv"):
    try:
        df = pd.read_csv(token_file)
        df["Re-evaluated"] = df.apply(lambda row: should_buy(dict(row)), axis=1)

        print("✅ Re-evaluation complete. Passing tokens:")
        print(df[df["Re-evaluated"] == True][["name", "chain", "estimated_return"]])
    except Exception as e:
        print(f"❌ Error during scan_and_evaluate: {e}")

# 🔭 Alias for backward compatibility
scan_and_snipe = scan_and_evaluate

# 🔍 Fetch latest token drops
def fetch_new_pairs(limit=20):
    mints = scan_solana_tokens(limit=limit)
    return [{
        "name": "Unknown",
        "symbol": mint[:4] + "...",
        "address": mint,
        "chain": "solana",
        "liquidity_usd": 15000,
        "price": round(0.0005 + (0.0001 * time.time() % 1), 6),
        "social_score_x": 8,
        "owner_renounced": False,
        "rug_check": False
    } for mint in mints]

# ⏸️ Pause check
def is_sniper_paused():
    return os.getenv("SNIPER_PAUSED", "False") == "True"

# 📈 Rate of Change calculator
def calculate_roc(address, interval=30):
    price_now = round(0.0005 + (0.0001 * time.time() % 1), 6)
    record_token_price(address, price_now)
    time.sleep(interval)
    price_later = round(0.0005 + (0.0001 * time.time() % 1), 6)
    record_token_price(address, price_later)
    try:
        return round(((price_later - price_now) / price_now) * 100, 2)
    except ZeroDivisionError:
        return 0.0

# 🎯 Real-time sniper engine
def execute_sniper_loop(roc_threshold=5.0):
    global total_sol_spent, last_trade_time

    now = time.time()

    if now - last_trade_time < MIN_COOLDOWN_SECONDS:
        logger.info("⏳ Cooldown active.")
        return

    if is_sniper_paused():
        logger.info("⏸️ Sniper paused.")
        time.sleep(300)
        return

    sol_price = fetch_sol_usd_price()
    if not sol_price:
        logger.warning("⚠️ SOL price unavailable.")
        return

    wallet_sol = get_sol_balance(wallet.pubkey())
    wallet_eth = 0.0  # ETH logic placeholder

    market_data = {
        "price_change_pct": 4.2,
        "volume_change_pct": 3.8
    }

    trade_decision = execute_trade_logic(
        wallet_sol_balance=wallet_sol,
        wallet_eth_balance=wallet_eth,
        last_trade_time=last_trade_time,
        current_time=now,
        daily_sol_spent=total_sol_spent,
        market_data=market_data
    )

    if trade_decision["action"] == "skip":
        logger.info(f"⏳ Trade skipped: {trade_decision['reason']}")
        return

    amount_sol = trade_decision["sol_allocation"]
    slippage = trade_decision["slippage_tolerance"]
    aggressiveness = trade_decision["aggressiveness"]

    logger.info(f"💡 Trade Aggressiveness: {aggressiveness}")

    if wallet_sol < LOW_BALANCE_ALERT or wallet_sol < amount_sol + 0.01:
        logger.warning(f"🛑 Low SOL balance: {wallet_sol}")
        return

    pairs = fetch_new_pairs()
    passed_count = 0

    for token in pairs:
        try:
            symbol = token["symbol"]
            address = token["address"]
            logger.info(f"🔍 Evaluating {symbol} ({address})")

            token["roc_30s"] = calculate_roc(address)
            logger.info(f"📈 ROC: {token['roc_30s']}%")

            if token["roc_30s"] < roc_threshold:
                logger.info("⛔ ROC too low.")
                continue

            token["age_seconds"] = get_token_age(address, RUGCHECK_API_KEY)
            creator = get_creator_wallet(address, RUGCHECK_API_KEY)
            token["creator_wallet"] = creator
            token["creator_score"] = get_creator_history_score(creator)

            if token["creator_score"] < 30:
                logger.info("⛔ Poor creator score.")
                continue

            if address in SAFE_OVERRIDES:
                token["rug_score"] = 0.0
                logger.info("✅ Safe override applied.")

            token_data = check_token_security(address, api_key=RUGCHECK_API_KEY)
            if token_data:
                if not is_good_contract(token_data):
                    logger.info("⛔ Contract flagged.")
                    continue
                if not is_bundled_supply(token_data):
                    logger.info("⛔ Supply bundle issues.")
                    continue

            if token["liquidity_usd"] < 15000:
    logger.info("⛔ Liquidity too low.")
    continue
