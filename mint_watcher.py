import re
import os
import time
import requests
from dotenv import load_dotenv
from telegram.ext import Updater, MessageHandler, Filters, CallbackContext
from telegram import Update

# 🔍 Validate mint using Dex Screener API
def validate_mint_on_dexscreener(mint):
    try:
        url = f"https://api.dexscreener.com/latest/dex/pairs/solana/{mint}"
        res = requests.get(url).json()
        data = res.get("pair")

        if not data:
            return False  # No valid market info

        liquidity = float(data.get("liquidity", 0))
        volume = float(data.get("volume", {}).get("h1", 0))
        age_text = data.get("age", "").lower()
        age_minutes = int(age_text.replace("m", "")) if "m" in age_text else 999

        print(f"🔎 Validating {mint} ➝ Age: {age_minutes} min | Volume: ${volume} | Liquidity: ${liquidity}")

        return liquidity > 1000 and volume > 500 and age_minutes < 30
    except Exception as e:
        print(f"⚠️ Dex Screener validation failed: {e}")
        return False

# ⚙️ Setup
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
AUTO_MINT_FILE = "auto_mints.txt"

# 🔍 Extract mint from text or Solscan link
def extract_mint(text):
    mint_matches = re.findall(r"[A-HJ-NP-Za-km-z1-9]{32,44}", text)
    solscan_links = re.findall(r"solscan\.io/token/([A-Za-z0-9]{32,44})", text)
    return list(set(mint_matches + solscan_links))

# 📩 Handle incoming Telegram message
def handle_message(update: Update, context: CallbackContext):
    text = update.message.text or ""
    mints = extract_mint(text)
    if not mints:
        return

    for mint in mints:
        # 🔒 Only accept sniper-grade tokens
        is_valid = validate_mint_on_dexscreener(mint)
        if not is_valid:
            update.message.reply_text(
                f"🧤 Mint rejected — sniper criteria not met: `{mint}`",
                parse_mode="Markdown"
            )
            continue

        with open(AUTO_MINT_FILE, "a+") as f:
            f.seek(0)
            existing = f.read().splitlines()
            if mint not in existing:
                f.write(f"{mint}\n")
                update.message.reply_text(
                    f"🎯 Valid mint added to OMO's patrol: `{mint}`",
                    parse_mode="Markdown"
                )

# 🚀 Start listener
def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(MessageHandler(Filters.text & (~Filters.command), handle_message))
    print("🧭 OMO intelligence listener active...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()