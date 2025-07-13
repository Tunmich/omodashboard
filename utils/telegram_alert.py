import os
from dotenv import load_dotenv
from telegram import Bot

# 📥 Load environment variables
load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
AUTHORIZED_USER_ID = int(os.getenv("TELEGRAM_CHAT_ID", 0))  # Use TELEGRAM_CHAT_ID per your .env

# ✅ Fallback check
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("🚨 Missing TELEGRAM_BOT_TOKEN in .env file")
if not AUTHORIZED_USER_ID:
    raise ValueError("🚨 Missing TELEGRAM_CHAT_ID in .env file")

# 🚀 Initialize bot
bot = Bot(token=TELEGRAM_BOT_TOKEN)

# 📲 Trade alert
def send_trade_alert(token_name, chain, tx_link):
    message = (
        f"🚀 Trade executed!\n"
        f"Token: {token_name}\n"
        f"Chain: {chain.upper()}\n"
        f"📦 TX: {tx_link}"
    )
    try:
        bot.send_message(chat_id=AUTHORIZED_USER_ID, text=message)
    except Exception as e:
        print(f"⚠️ Failed to send trade alert: {e}")

# 📊 ROI alert
def send_roi_alert(token_name, roi, tx_link):
    try:
        roi_value = float(roi)
        emoji = "🟢" if roi_value > 0 else "🔴" if roi_value < 0 else "⚪"
        roi_text = f"{roi_value:.2f}%"
    except (ValueError, TypeError):
        emoji = "⚪"
        roi_text = "N/A"

    message = (
        f"{emoji} Sold {token_name}\n"
        f"ROI: {roi_text}\n"
        f"🔗 TX: {tx_link}"
    )
    try:
        bot.send_message(chat_id=AUTHORIZED_USER_ID, text=message)
    except Exception as e:
        print(f"⚠️ Failed to send ROI alert: {e}")