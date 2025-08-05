import os
import time
import random
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes
)
from utils.wallet_mapper import get_safe_evm_wallet
from solders.keypair import Keypair
from modules.solana_executor import get_wallet_balance
from utils.token_scanner import scan_solana_tokens

# ------------------- INIT -------------------
load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
RAW_KEY = os.getenv("WALLET_PRIVATE_KEY")

if not BOT_TOKEN or not CHAT_ID or not RAW_KEY:
    raise EnvironmentError("❌ Missing required environment variables.")

# Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

wallet = Keypair.from_base58_string(RAW_KEY)
patrol_active = False
mint_targets = []
reload_env = lambda: load_dotenv(override=True)  # Overwrite env vars

# ------------------- HELPERS -------------------

def get_sol_price():
    try:
        import requests
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        res = requests.get(url).json()
        return res["solana"]["usd"]
    except Exception:
        return 25.0  # fallback

def get_trading_budget_in_sol():
    usd_budget = float(os.getenv("USD_PER_TRADE", "0.05"))
    price = get_sol_price()
    return usd_budget / price

def scan_targets():
    mint_raw = os.getenv("AUTO_MINT_LIST", "")
    return [mint.strip() for mint in mint_raw.split(",") if mint.strip()]

# Placeholders for missing business logic, fill as needed
def is_valid_token(mint):
    return True
def update_env_flag(*args, **kwargs):
    """Implement as needed or stub."""

# ------------------- TELEGRAM HANDLERS -------------------

async def start_patrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global patrol_active
    if patrol_active:
        await update.message.reply_text("🚀 OMO is already active.")
        return
    patrol_active = True
    context.application.create_task(patrol_loop(update))
    await update.message.reply_text("🟢 Patrol started. OMO on the hunt.")

async def patrol_loop(update: Update):
    global patrol_active
    while patrol_active:
        balance = get_wallet_balance(wallet.pubkey())
        low_threshold = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
        if balance < low_threshold:
            patrol_active = False
            await update.message.reply_text("🛑 Patrol auto-disabled due to low balance.")
            print("🛑 Patrol stopped due to low balance.")
            break
        live_mints = scan_solana_tokens(limit=10)
        valid_mints = [mint for mint in live_mints if is_valid_token(mint)]
        if not valid_mints:
            print("⚠️ No valid mints found. Skipping patrol cycle.")
            await update.message.reply_text("⚠️ No valid mints found. Patrol waiting...")
            await asyncio.sleep(600)
            continue
        mint = random.choice(valid_mints)
        print(f"🎯 Would execute trade on {mint}")
        # TODO: Execute trade logic
        await asyncio.sleep(60)

async def stop_patrol(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global patrol_active
    patrol_active = False
    await update.message.reply_text("🛑 Patrol stopped. OMO standing down.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sol_balance = get_wallet_balance(wallet.pubkey())
    msg = (
        f"👤 *OMO STATUS*\n\n"
        f"Balance: `{sol_balance:.4f}` SOL\n"
        f"Patrol Active: `{patrol_active}`\n"
        f"Targets: `{len(mint_targets)}`"
    )
    await update.message.reply_text(msg, parse_mode='Markdown')

async def wallet_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pubkey = str(wallet.pubkey())
    balance = get_wallet_balance(wallet.pubkey())
    trade_amount = os.getenv("USD_PER_TRADE", "0.05")
    low_threshold = os.getenv("LOW_BALANCE_ALERT", "0.01")
    msg = f"""
*📊 OMO Wallet Status*

🔑 Wallet: `{pubkey}`
💰 Balance: `{balance:.4f}` SOL
🎯 Trade Amount: `{trade_amount}` SOL
🛡 Low Balance Alert: `{low_threshold}` SOL
"""
    await update.message.reply_text(msg, parse_mode="Markdown")

async def killfeed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("sniper_log.txt"):
        await update.message.reply_text("📄 No kill logs found yet.")
        return
    with open("sniper_log.txt", "r") as f:
        lines = f.readlines()[-5:]
    feed = "*🔫 OMO Killfeed*\n\n" + "".join(lines)
    await update.message.reply_text(feed, parse_mode='Markdown')

async def intel_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not os.path.exists("tracked_groups.txt"):
        await update.message.reply_text("📡 No intel groups tracked yet.")
        return
    with open("tracked_groups.txt", "r") as f:
        lines = f.readlines()
    if not lines:
        await update.message.reply_text("📡 No intel activity recorded.")
        return
    msg = "*🧠 OMO Intel Status*\n\n"
    for line in lines:
        parts = line.strip().split("|")
        if len(parts) == 3:
            group_id, name, timestamp = parts
            msg += f"• `{name}` (`{group_id}`)\n  Last seen: `{timestamp}`\n"
    await update.message.reply_text(msg, parse_mode="Markdown")

async def track_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = str(update.effective_chat.id)
    chat_title = update.effective_chat.title or "Unknown"
    with open("tracked_groups.txt", "a+") as f:
        f.seek(0)
        known_ids = f.read().splitlines()
        if chat_id not in known_ids:
            f.write(chat_id + "\n")
            await update.message.reply_text(f"📡 Group tracked: {chat_title} ({chat_id})")
        else:
            await update.message.reply_text(f"✅ Already tracking: {chat_title} ({chat_id})")

async def set_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        args = context.args
        if not args:
            await update.message.reply_text("⚠️ Usage: `/settrade 0.05`", parse_mode="Markdown")
            return
        new_amount = float(args[0])
        if new_amount < 0.001 or new_amount > 10:
            await update.message.reply_text("❌ Trade amount must be between `0.001` and `10.0` SOL", parse_mode="Markdown")
            return
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            updated = False
            for line in lines:
                if line.startswith("USD_PER_TRADE="):
                    f.write(f"USD_PER_TRADE={new_amount}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"USD_PER_TRADE={new_amount}\n")
        await update.message.reply_text(f"✅ Trade amount updated to `{new_amount}` SOL", parse_mode="Markdown")
        reload_env()
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to update trade amount: {e}")

async def get_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("USD_PER_TRADE="):
                    value = line.strip().split("=")[1]
                    await update.message.reply_text(f"💰 Current trade amount: `{value}` SOL", parse_mode="Markdown")
                    return
        await update.message.reply_text("⚠️ Trade amount not set in `.env`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to read trade amount: {e}")

async def reset_trade_amount(update: Update, context: ContextTypes.DEFAULT_TYPE):
    default_value = "0.05"
    try:
        with open(".env", "r") as f:
            lines = f.readlines()
        with open(".env", "w") as f:
            updated = False
            for line in lines:
                if line.startswith("USD_PER_TRADE="):
                    f.write(f"USD_PER_TRADE={default_value}\n")
                    updated = True
                else:
                    f.write(line)
            if not updated:
                f.write(f"USD_PER_TRADE={default_value}\n")
        await update.message.reply_text(f"🔄 Trade amount reset to `{default_value}` SOL", parse_mode="Markdown")
        reload_env()
    except Exception as e:
        await update.message.reply_text(f"❌ Failed to reset trade amount: {e}")

async def sniper_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    trade_size = get_trading_budget_in_sol()
    msg = (
        f"*🎯 OMO Sniper Status*\n\n"
        f"Patrol: `{patrol_active}`\n"
        f"Trade Size: `{trade_size:.4f}` SOL\n"
        f"Targets: `{len(mint_targets)}`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def intel_pause(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global patrol_active
    patrol_active = False
    await update.message.reply_text("🛑 Intel patrol paused.")

async def reload_env_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reload_env()
    await update.message.reply_text("🔄 Environment reloaded.")

async def pause_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_env_flag("SNIPER_PAUSED", "True")
    await update.message.reply_text("⏸️ Sniper paused.")

async def resume_sniper(update: Update, context: ContextTypes.DEFAULT_TYPE):
    update_env_flag("SNIPER_PAUSED", "False")
    await update.message.reply_text("▶️ Sniper resumed.")

async def discover(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mints = scan_solana_tokens(limit=5)
    msg = "*🧠 Discovered Tokens:*\n\n" + "\n".join(f"`{mint}`" for mint in mints)
    await update.message.reply_text(msg, parse_mode="Markdown")

# ------------------- APP BOOTSTRAP -------------------

def main():
    import asyncio
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_patrol))
    app.add_handler(CommandHandler("stop", stop_patrol))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("walletstatus", wallet_status))
    app.add_handler(CommandHandler("killfeed", killfeed))
    app.add_handler(CommandHandler("intelstatus", intel_status))
    app.add_handler(CommandHandler("trackgroup", track_group))
    app.add_handler(CommandHandler("settrade", set_trade_amount))
    app.add_handler(CommandHandler("gettrade", get_trade_amount))
    app.add_handler(CommandHandler("resettrade", reset_trade_amount))
    app.add_handler(CommandHandler("sniperstatus", sniper_status))
    app.add_handler(CommandHandler("intelpause", intel_pause))
    app.add_handler(CommandHandler("reloadenv", reload_env_handler))
    app.add_handler(CommandHandler("discover", discover))
    app.add_handler(CommandHandler("pause", pause_sniper))
    app.add_handler(CommandHandler("resume", resume_sniper))

    print("✅ Telegram Controller Active")
    app.run_polling()

if __name__ == "__main__":
    main()
