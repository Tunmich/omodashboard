import os
import re
import requests
import threading
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, MessageHandler,filters, CallbackContext, CommandHandler
from solders.keypair import Keypair
from modules.solana_executor import execute_sol_trade, get_wallet_balance
from utils.wallet_mapper import get_safe_evm_wallet
from utils.thread_launcher import THREAD_STATUS
from strategy.trade_decision_engine import should_buy, LAST_TRACE
from health_check import health_monitor_loop
from utils.alloc import get_trade_allocation

# 🧬 Load environment
load_dotenv()

# ✅ Inject EVM Wallet
wallet_detected = False
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        wallet_detected = True
        print(f"🔐 EVM wallet injected: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

# 🔧 Config
bot_token = os.getenv("TELEGRAM_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
group_ids = os.getenv("INTEL_GROUP_IDS", "").split(",")
raw_key = os.getenv("WALLET_PRIVATE_KEY")
wallet = Keypair.from_base58_string(raw_key)
auto_patrol = os.getenv("AUTO_PATROL_ENABLED", "False") == "True"
low_threshold = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
usd_budget = float(os.getenv("USD_PER_TRADE", "0.05"))
rugcheck_api_key = os.getenv("RUGCHECK_API_KEY")
blacklist = os.getenv("CREATOR_BLACKLIST", "").split(",")

sol_amount = usd_budget / (
    requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
    .json().get("solana", {}).get("usd", 25.0)
)

# ✅ Telegram alert utility
def send_telegram_alert(message):
    Bot(token=bot_token).send_message(chat_id=chat_id, text=message)

# ✅ Send wallet ping if injected
if wallet_detected:
    send_telegram_alert("🔐 Wallet injected ✅")

# ✅ Startup ping
def send_startup_ping(mode="multi"):
    msg = (
        f"📡 OMO Sniper Activated\n\n"
        f"Chain Mode: {mode.upper()}\n"
        f"Status: ✅ Online\n"
        f"Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}"
    )
    send_telegram_alert(msg)

# 🧠 Regex for mint detection
MINT_REGEX = r"\b[1-9A-HJ-NP-Za-km-z]{43,44}\b"

# 🧪 Mint filters
def is_valid_token(mint):
    def get_token_age(m): ...
    def get_creator_wallet(m): ...
    def check_token_security(addr, chain="solana"): ...

    age = get_token_age(mint)
    if age < 300:
        return False
    creator = get_creator_wallet(mint)
    if creator in blacklist:
        return False
    token_data = check_token_security(mint)
    if token_data:
        if not token_data.get("is_open_source") or token_data.get("is_proxy"):
            return False
        if float(token_data.get("top10_holders_percentage", 0)) > 80:
            return False
    return True

# 📲 Telegram mint handler
def handle_message(update: Update, context: CallbackContext):
    chat_id = str(update.effective_chat.id)
    if chat_id not in group_ids:
        return

    text = update.message.text
    found = re.findall(MINT_REGEX, text)
    for mint in found:
        balance = get_wallet_balance(wallet.pubkey())
        if balance < low_threshold:
            send_telegram_alert("🛑 Low balance, auto-patrol disabled.")
            continue

        if is_valid_token(mint) and auto_patrol:
            health_thread = threading.Thread(target=health_monitor_loop)
            health_thread.start()

# 🧠 /ping diagnostics
def ping_live(update: Update, context: CallbackContext):
    from health_check import MODULES
    message = "🧠 OMO /ping\n\n"
    failed = []

    for mod, func in MODULES.items():
        try:
            m = __import__(mod, fromlist=[func])
            assert callable(getattr(m, func))
            message += f"✅ {mod}\n"
        except Exception:
            message += f"❌ {mod}\n"
            failed.append(mod)

    message += "\n🧵 Threads:\n"
    for name, status in THREAD_STATUS.items():
        uptime = int(status.get("uptime", 5))
        retries = status.get("retries", 0)
        active = "✅" if status.get("active") else "❌"
        message += f"{active} {name} | {uptime}s up, {retries} retries\n"

    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# 🧠 /flow
def flow_last(update: Update, context: CallbackContext):
    message = LAST_TRACE.get("trace", "📭 No recent token scored yet.")
    context.bot.send_message(chat_id=update.effective_chat.id, text=message)

# 🧠 /score
def score_token(update: Update, context: CallbackContext):
    args = context.args
    if not args:
        update.message.reply_text("Usage: /score <mint_address>")
        return

    mint = args[0]
    token = {
        "chain": "Solana",
        "address": mint,
        "symbol": "INT",
        "buzz_score": 72,
        "roi_score": 68,
        "risk_score": 26,
        "liquidity_usd": 1200,
        "volume_usd": 50000,
        "name": "SolINT",
        "tweet_text": "Fresh mint spotted",
        "source": "Telegram",
    }

    should_buy(token)
    trace = LAST_TRACE.get("trace", "📭 No scoring trace available.")
    update.message.reply_text(trace)

# 🚀 Launch patrol listener
def start_telegram_listener():
    try:
        updater = Updater(bot_token, use_context=True)
        dp = updater.dispatcher

        dp.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        dp.add_handler(CommandHandler("ping", ping_live))
        dp.add_handler(CommandHandler("flow", flow_last))
        dp.add_handler(CommandHandler("score", score_token))

        send_startup_ping()
        updater.start_polling()
        print("🧠 Telegram patrol running.")
        updater.idle()
    except Exception as e:
        logging.warning(f"Telegram listener error: {e}")

# ✅ External alias
PatrolManager = start_telegram_listener
