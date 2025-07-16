import os
import random
import requests
from datetime import datetime
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.types import TxOpts

# 🚀 Load environment
load_dotenv()

# 🔗 Solana RPC connection
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC)

# 📡 Jupiter API endpoints
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"

def get_wallet_balance(pubkey):
    try:
        balance = client.get_balance(pubkey)["result"]["value"]
        sol_balance = balance / 1e9
        print(f"🧮 Wallet balance: {sol_balance:.4f} SOL")
        return sol_balance
    except Exception as e:
        print(f"❌ Failed to fetch balance: {e}")
        return 0
# 📝 Sniper Log Function
def log_sniper_trade(mint, sol_amount, tx_signature, received_amount=None):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    roi_text = f"{received_amount} received" if received_amount else "N/A"
    log_entry = f"[{now}] Mint: {mint} | Spent: {sol_amount} SOL | ROI: {roi_text} | TX: {tx_signature}\n"

    try:
        with open("sniper_log.txt", "a") as f:
            f.write(log_entry)
        print("📒 Trade logged to sniper_log.txt")
    except Exception as e:
        print(f"❌ Failed to log trade: {e}")

# 📲 Telegram Alert Function
def send_telegram_alert(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("⚠️ Telegram credentials missing. Skipping alert.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        requests.post(url, json=payload)
        print("📡 Telegram alert sent.")
    except Exception as e:
        print(f"❌ Telegram alert failed: {e}")

# 🎯 Main Trade Execution Function
def execute_sol_trade(mint_address, amount_sol, wallet):
    print(f"🎯 OMO attempting sniper trade: {amount_sol} SOL ➝ {mint_address}")
    current_balance = get_wallet_balance(wallet.pubkey())
    
    if current_balance < amount_sol:
        warning = f"🛑 Insufficient balance. Need {amount_sol} SOL, but only have {current_balance:.4f} SOL.\nTrade skipped."
        print(warning)
        send_telegram_alert(warning)
        return
    lamports = int(amount_sol * 1e9)

    def attempt_swap(target_mint):
        print(f"🔍 Scanning for route ➝ {target_mint}")
        quote_params = {
            "inputMint": "So11111111111111111111111111111111111111112",
            "outputMint": target_mint,
            "amount": lamports,
            "slippageBps": 50,
            "onlyDirectRoutes": False
        }

        try:
            quote_response = requests.get(JUPITER_QUOTE_API, params=quote_params).json()
            routes = quote_response.get("data", [])
            if not routes:
                print(f"❌ Route unavailable for {target_mint}")
                return False

            best_route = routes[0]
            swap_request = {
                "route": best_route,
                "userPublicKey": str(wallet.pubkey())
            }

            swap_response = requests.post(JUPITER_SWAP_API, json=swap_request).json()
            swap_tx_hex = swap_response.get("swapTransaction")
            if not swap_tx_hex:
                print(f"❌ No payload returned for {target_mint}")
                return False

            tx_bytes = bytes.fromhex(swap_tx_hex)
            response = client.send_raw_transaction(tx_bytes, opts=TxOpts(skip_preflight=True))
            tx_signature = response.get("result")

            if tx_signature:
                print(f"✅ Trade confirmed ➝ {target_mint}: https://solscan.io/tx/{tx_signature}")
                log_sniper_trade(target_mint, amount_sol, tx_signature)

                report = f"""
🚀 *OMO Sniper Successful*

*Mint:* `{target_mint}`
*Amount:* {amount_sol} SOL
[🔗 View TX on Solscan](https://solscan.io/tx/{tx_signature})
"""
                send_telegram_alert(report)
                return True
            else:
                print("⚠️ TX submission failed. No signature returned.")
                return False

        except Exception as e:
            print(f"💥 Error during swap to {target_mint}: {e}")
            return False

    # 🔫 Attempt primary target
    if not attempt_swap(mint_address):
        print("🔁 Fallback activated — rotating targets...")
        fallback_raw = os.getenv("FALLBACK_TOKENS", "")
        fallback_mints = [mint.strip() for mint in fallback_raw.split(",") if mint.strip()]
        random.shuffle(fallback_mints)

        for fallback_mint in fallback_mints:
            if attempt_swap(fallback_mint):
                print(f"🚀 Fallback successful ➝ {fallback_mint}")
                return

        print("🛑 All fallback swaps failed. Target evaded.")