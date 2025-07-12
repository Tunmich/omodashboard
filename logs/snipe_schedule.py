from telegram import Bot
from modules.sniper_engine import sniper_loop
from modules.token_feed import fetch_recent_tokens

BOT = Bot("YOUR_BOT_TOKEN")
USER_ID = 123456789  # Your Telegram ID

def run_job():
    try:
        tokens = fetch_recent_tokens()
        sniper_loop(tokens)
        BOT.send_message(chat_id=USER_ID, text="✅ Scheduled sniper run complete.")
    except Exception as e:
        BOT.send_message(chat_id=USER_ID, text=f"🔥 Sniper run failed: {e}")