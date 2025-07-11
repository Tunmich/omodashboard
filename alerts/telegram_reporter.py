import os
from dotenv import load_dotenv
from telegram import Bot
from datetime import datetime
import pandas as pd

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot = Bot(token=BOT_TOKEN)

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