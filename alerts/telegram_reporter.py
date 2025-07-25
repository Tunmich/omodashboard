import os
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
import pandas as pd
from utils.alloc import get_trade_allocation
from utils.wallet_mapper import get_safe_evm_wallet

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=BOT_TOKEN)

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

def send_hourly_report():
    try:
        df = pd.read_csv("logs/trades.csv")
        df["Timestamp"] = pd.to_datetime(df["Timestamp"])
        recent = df[df["Timestamp"] > pd.Timestamp.now() - pd.Timedelta(hours=1)]

        traded = len(recent)
        skipped = "-"  # Optional: track if you log skipped tokens

        avg_roi = recent["roi_score"].mean() if traded else 0
        total_pl = recent["estimated_pl"].sum() if traded else 0

        report = f"""
🕒 Hourly Report ({datetime.now().strftime('%Y-%m-%d %H:%M')})
✅ Trades: {traded}
📉 Skipped: {skipped}
📊 Avg ROI: {round(avg_roi, 2)}%
💰 Total P/L: ${round(total_pl, 2)}
"""
        bot.send_message(chat_id=CHAT_ID, text=report.strip())
        print("📤 Hourly report sent.")

    except Exception as e:
        bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Failed to send report: {e}")