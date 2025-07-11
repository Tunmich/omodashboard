import os
import time
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from scheduler.job_runner import process_tokens
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
bot_running = False

async def startbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_running
    if bot_running:
        await update.message.reply_text("🚀 Bot already running.")
        return
    bot_running = True
    await update.message.reply_text("✅ Starting Meme Sniper Bot...")
    while bot_running:
        process_tokens()
        await update.message.reply_text("🕒 Waiting 10 minutes before next scan.")
        time.sleep(600)

async def stopbot(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_running
    bot_running = False
    await update.message.reply_text("🛑 Sniper bot stopped.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    state = "🟢 Running" if bot_running else "🔴 Idle"
    await update.message.reply_text(f"📊 Bot Status: {state}")

def start_controller():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("startbot", startbot))
    app.add_handler(CommandHandler("stopbot", stopbot))
    app.add_handler(CommandHandler("status", status))
    print("✅ Telegram Controller Active")
    app.run_polling()