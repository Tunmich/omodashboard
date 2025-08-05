from telegram.ext import ApplicationBuilder, CommandHandler

async def start(update, context):
    await update.message.reply_text("Bot is alive!")

app = ApplicationBuilder().token('8124408929:AAGFYC-J0kjJL-ablU5qeE_BNu9ICUAaRNo').build()
app.add_handler(CommandHandler("start", start))
app.run_polling()
