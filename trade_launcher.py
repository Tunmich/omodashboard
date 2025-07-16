import os
import time
import random
import requests
from dotenv import load_dotenv
from solders.keypair import Keypair
from modules.solana_executor import execute_sol_trade, send_telegram_alert, log_sniper_trade

# 🚀 Load .env
load_dotenv()

# 🔑 Wallet
raw_key = os.getenv("WALLET_PRIVATE_KEY")
wallet = Keypair.from_base58_string(raw_key)

# Updated mint loader
file_mints = []
if os.path.exists("auto_mints.txt"):
    with open("auto_mints.txt", "r") as f:
        file_mints = [line.strip() for line in f.readlines() if line.strip()]

env_mints = [mint.strip() for mint in os.getenv("AUTO_MINT_LIST", "").split(",") if mint.strip()]
mint_targets = list(set(env_mints + file_mints))  # Merge & de-dupe
if not mint_targets:
    print("❌ No mints found in AUTO_MINT_LIST.")
    exit()

# 💰 Per-trade amount
sol_amount = float(os.getenv("USD_PER_TRADE", "0.05"))

# 📊 Summary log
daily_report = []

# 🕵️‍♂️ Mint name lookup
def get_token_name(mint):
    try:
        url = f"https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [mint, {"encoding": "jsonParsed"}]
        }
        res = requests.post(url, json=payload, headers=headers).json()
        name = res["result"]["value"]["data"]["parsed"]["info"]["name"]
        return name
    except:
        return "UnknownToken"

# 📤 Telegram daily summary
def send_daily_summary():
    if not daily_report:
        return

    summary_text = "*📊 Daily Sniper Summary*\n\n"
    for entry in daily_report:
        summary_text += f"✅ `{entry['name']}`\nMint: `{entry['mint']}`\nAmount: {entry['amount']} SOL\nTX: [View](https://solscan.io/tx/{entry['tx']})\n\n"

    send_telegram_alert(summary_text)

# 🔁 Patrol loop
print(f"🧭 OMO patrol initiated. Targets loaded.")
counter = 0
while True:
    mint = random.choice(mint_targets)
    token_name = get_token_name(mint)

    print(f"\n⏳ Cycle {counter + 1} ➝ {token_name} ({mint})")

    success = execute_sol_trade(mint, sol_amount, wallet)
    if success:
        daily_report.append({
            "mint": mint,
            "name": token_name,
            "amount": sol_amount,
            "tx": "Logged"  # TX included inside `execute_sol_trade`
        })
    else:
        print(f"🔁 Retrying ➝ {token_name}")
        time.sleep(10)
        retry = execute_sol_trade(mint, sol_amount, wallet)
        if retry:
            daily_report.append({
                "mint": mint,
                "name": token_name,
                "amount": sol_amount,
                "tx": "Logged"
            })
        else:
            print(f"🛑 Failed after retry: {token_name}")

    counter += 1

    # 💤 Sleep 1 hour per cycle
    print("🕒 OMO resting for 1 hour...\n")
    time.sleep(3600)

    # 📤 Send daily summary every 6 cycles
    if counter % 6 == 0:
        send_daily_summary()
        daily_report = []