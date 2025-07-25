import os
import time
import random
import requests
from dotenv import load_dotenv
from solders.keypair import Keypair
from modules.solana_executor import execute_sol_trade, send_telegram_alert
from utils.wallet_mapper import get_safe_evm_wallet

# 🚀 Load environment
load_dotenv()

# 🔐 Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    sol_address = os.getenv("SOLANA_WALLET") or os.getenv("WALLET_ADDRESS")
    evm_address = get_safe_evm_wallet(sol_address)
    if evm_address:
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    else:
        print("⚠️ Failed to inject EVM wallet.")

# 🔑 Load Solana wallet
raw_key = os.getenv("WALLET_PRIVATE_KEY")
wallet = Keypair.from_base58_string(raw_key)

# 📥 Load mint targets
file_mints = []
if os.path.exists("auto_mints.txt"):
    with open("auto_mints.txt", "r") as f:
        file_mints = [line.strip() for line in f if line.strip()]

env_mints = [mint.strip() for mint in os.getenv("AUTO_MINT_LIST", "").split(",") if mint.strip()]
mint_targets = list(set(env_mints + file_mints))  # Merge & dedupe

if not mint_targets:
    print("❌ No mints found in AUTO_MINT_LIST.")
    exit()

# 💰 Trade parameters
sol_amount = float(os.getenv("USD_PER_TRADE", "0.05"))

# 📊 Summary log
daily_report = []

# 🕵️‍♂️ Token name lookup
def get_token_name(mint):
    try:
        url = "https://api.mainnet-beta.solana.com"
        headers = {"Content-Type": "application/json"}
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getAccountInfo",
            "params": [mint, {"encoding": "jsonParsed"}]
        }
        res = requests.post(url, json=payload, headers=headers).json()
        return res["result"]["value"]["data"]["parsed"]["info"]["name"]
    except:
        return "UnknownToken"

# 📤 Telegram daily summary
def send_daily_summary():
    if not daily_report:
        return
    summary = "*📊 Daily Sniper Summary*\n\n"
    for entry in daily_report:
        summary += f"✅ `{entry['name']}`\nMint: `{entry['mint']}`\nAmount: {entry['amount']} SOL\nTX: [View](https://solscan.io/tx/{entry['tx']})\n\n"
    send_telegram_alert(summary)

# 🔁 Main patrol loop
print("🧭 OMO patrol initiated. Targets loaded.")
counter = 0

while True:
    mint = random.choice(mint_targets)
    token_name = get_token_name(mint)
    print(f"\n⏳ Cycle {counter + 1} ➝ {token_name} ({mint})")

    success = execute_sol_trade(mint, sol_amount, wallet)
    if not success:
        print(f"🔁 Retrying ➝ {token_name}")
        time.sleep(10)
        success = execute_sol_trade(mint, sol_amount, wallet)

    if success:
        daily_report.append({
            "mint": mint,
            "name": token_name,
            "amount": sol_amount,
            "tx": "Logged"
        })
    else:
        print(f"🛑 Failed after retry: {token_name}")

    counter += 1
    print("🕒 OMO resting for 1 hour...\n")
    time.sleep(3600)

    if counter % 6 == 0:
        send_daily_summary()
        daily_report = []
