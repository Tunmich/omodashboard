# alerts/telegram_bot.py

import os
import logging
import requests
from dotenv import load_dotenv
from utils.alloc import get_trade_allocation
from utils.wallet_mapper import get_safe_evm_wallet
# 🧬 Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

import os
from dotenv import load_dotenv
load_dotenv()

# Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        # Use Phantom's known derivation logic or fetch from wallet connector
        # For now, simulate with fallback mapping
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

def send_startup_ping(mode: str):
    message = f"📡 OMO Sniper Activated\n\nChain Mode: {mode.upper()}\nStatus: ✅ Online\nTimestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    send_message(message)

def send_message(msg: str):
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.warning("⚠️ Telegram not configured — check .env for TELEGRAM_TOKEN and TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": msg}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            logging.info("📡 Telegram message sent successfully.")
        else:
            logging.error(f"❌ Telegram send failure: {res.status_code} — {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram error: {e}")

def run_omo_bot():
    # 🔁 Reload env vars to guarantee they're fresh
    load_dotenv()
    token = os.getenv("TELEGRAM_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not token or not chat_id:
        logging.warning("⚠️ Telegram not configured — check .env for TELEGRAM_TOKEN and TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": "🟢 Telegram alert bot is now online."}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            logging.info("📡 Telegram startup message sent.")
        else:
            logging.error(f"❌ Startup message failure: {res.status_code} — {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram startup error: {e}")

    send_message("📢 Bot is ready for action.")

def send_token_alert(token: dict):
    """
    Sends a formatted alert for a new token.
    """
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.warning("⚠️ Telegram not configured")
        return

    message = f"""
📢 New Token Discovered!
🧬 Name: {token.get('name', 'Unknown')}
🔗 Chain: {token.get('chain', 'N/A')}
🏷️ Symbol: {token.get('symbol', '')}
📦 Address: {token.get('address')}
🔥 Buzz Score: {token.get('buzz_score', 'N/A')}
📈 ROI Score: {token.get('roi_score', 'N/A')}
⚠️ Risk Score: {token.get('risk_score', 'N/A')}
💵 Price (USD): {token.get('token_price_usd', 'N/A')}
"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message.strip()}
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            logging.info("🚀 Token alert sent to Telegram.")
        else:
            logging.error(f"❌ Alert failure: {res.status_code} — {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram alert error: {e}")
