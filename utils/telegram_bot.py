# utils/telegram_bot.py

import os
import logging
import requests
from dotenv import load_dotenv

print("TELEGRAM_TOKEN:", os.getenv("TELEGRAM_TOKEN"))
print("TELEGRAM_CHAT_ID:", os.getenv("TELEGRAM_CHAT_ID"))

# 🔐 Load .env configuration
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def _send_raw(text):
    """Internal function to send raw text via Telegram Bot API."""
    if not TELEGRAM_TOKEN or not CHAT_ID:
        logging.warning("⚠️ Telegram not configured — check TELEGRAM_TOKEN and TELEGRAM_CHAT_ID in .env")
        return

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}

    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code == 200:
            logging.info("📡 Telegram message sent successfully.")
        else:
            logging.error(f"❌ Telegram failed — {res.status_code}: {res.text}")
    except Exception as e:
        logging.error(f"❌ Telegram exception: {e}")

def send_message(msg):
    """Public method for simple Telegram alert dispatch."""
    _send_raw(msg)

def send_trade_alert(symbol, chain, tx_url=None):
    """Formatted trade alert."""
    message = f"""
🚀 Trade Executed
Token: {symbol}
Chain: {chain.upper()}
Status: SUCCESS
Link: {tx_url if tx_url else 'N/A'}
"""
    _send_raw(message.strip())

def run_omo_bot():
    """Startup initialization alert."""
    startup_msg = "🟢 OMO Telegram interface is now online."
    _send_raw(startup_msg)
    send_message("📢 Bot is ready for action.")
