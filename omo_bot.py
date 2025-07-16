import os
import threading
import time
import requests
from dotenv import load_dotenv
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
from solders.keypair import Keypair
from modules.solana_executor import execute_sol_trade, get_wallet_balance

load_dotenv()

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
raw_key = os.getenv("WALLET_PRIVATE_KEY")
wallet = Keypair.from_base58_string(raw_key)
sol_amount = float(os.getenv("USD_PER_TRADE", "0.05"))
mint_raw = os.getenv("AUTO_MINT_LIST", "")
mint_targets = [mint.strip() for mint in mint_raw.split(",") if mint.strip()]
patrol_active = False

def patrol_loop():
    global patrol_active
    while patrol_active:
        mint = random.choice(mint_targets)
        execute_sol_trade(mint, sol_amount, wallet)
        time.sleep(3600)

def start_patrol(update: Update, context: CallbackContext):
    global patrol_active
    if patrol_active:
        update.message.reply_text("🚀 OMO is already active.")
        return
    patrol_active = True
    threading.Thread(target=patrol_loop).start()
    update.message.reply_text("🟢 Patrol started. OMO on the hunt.")

def stop_patrol(update: Update, context: CallbackContext):
    global patrol_active
    patrol_active = False
    update.message.reply_text("🛑 Patrol stopped. OMO standing down.")

def status(update: Update, context: CallbackContext):
    sol_balance = get_wallet_balance(wallet.pubkey())
    msg = f"👤 *OMO STATUS*\n\nBalance: `{sol_balance:.4f}` SOL\nPatrol Active: `{patrol_active}`\nTargets: `{len(mint_targets)}`"
    update.message.reply_text(msg, parse_mode='Markdown')

def killfeed(update: Update, context: CallbackContext):
    if not os.path.exists("sniper_log.txt"):
        update.message.reply_text("📄 No kill logs found yet.")
        return
    with open("sniper_log.txt", "r") as f:
        lines = f.readlines()[-5:]  # Send last 5 kills
    feed = "*🔫 OMO Killfeed*\n\n" + "".join(lines)
    update.message.reply_text(feed, parse_mode='Markdown')

def main():
    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start_patrol))
    dp.add_handler(CommandHandler("stop", stop_patrol))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("killfeed", killfeed))
    updater.start_polling()
    print("📡 OMO Telegram interface live.")
    updater.idle()

if __name__ == "__main__":
    main()