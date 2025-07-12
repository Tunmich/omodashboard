from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from modules.sniper_engine import sniper_loop
from modules.token_feed import fetch_recent_tokens  # Your token sourcing logic

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN"
AUTHORIZED_USER_ID = 123456789  # Your Telegram user ID

async def send_trade_alert(context, token_name, chain, tx_link):
    message = f"🚀 Trade executed!\nToken: {token_name}\nChain: {chain.upper()}\n📦 TX: {tx_link}"
    await context.bot.send_message(chat_id=AUTHORIZED_USER_ID, text=message)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📡 Sniper Bot is online.")

async def sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != AUTHORIZED_USER_ID:
        await update.message.reply_text("⛔ Unauthorized.")
        return
    await update.message.reply_text("🎯 Running Sniper Logic...")
    tokens = fetch_recent_tokens()  # Use your CA feed or DexScreener fetch
    sniper_loop(tokens)
    await update.message.reply_text("✅ Sniper run complete.")

app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("snipe", sniper))

app.run_polling()