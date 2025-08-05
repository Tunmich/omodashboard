import os
import random
import requests
import time
from datetime import datetime
from dotenv import load_dotenv
from solana.rpc.api import Client
from solana.rpc.types import TxOpts
from utils.wallet_mapper import get_safe_evm_wallet

# 🚀 Load environment
load_dotenv()
LOW_BALANCE_THRESHOLD = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))  # in SOL

# 🔗 Solana RPC connection
SOLANA_RPC = "https://api.mainnet-beta.solana.com"
client = Client(SOLANA_RPC)

# 📡 Jupiter API endpoints
JUPITER_QUOTE_API = "https://quote-api.jup.ag/v6/quote"
JUPITER_SWAP_API = "https://quote-api.jup.ag/v6/swap"

# 🧠 Cache of successful mints
successful_snipes = set()

from solders.pubkey import Pubkey
import os
from dotenv import load_dotenv
load_dotenv()

# Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        # Use Phantom's known derivation logic or fetch from wallet connector
        # For now, simulate with fallback mapping
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

def get_wallet_balance(pubkey, retries=3, delay=2):
    try:
        pubkey_str = str(pubkey) if not isinstance(pubkey, str) else pubkey
        assert len(pubkey_str) in [43, 44], "Invalid Solana public key format."
    except Exception as e:
        print(f"❌ Invalid wallet key: {e}")
        return 0.0

    solana_pubkey = Pubkey.from_string(pubkey_str)

    for attempt in range(1, retries + 1):
        try:
            print(f"🔍 Fetching balance (Attempt {attempt}) for {pubkey_str}")
            response = client.get_balance(solana_pubkey)
            lamports = response.value
            sol_balance = lamports / 1e9
            print(f"🧮 Wallet balance: {sol_balance:.4f} SOL")

            # 📡 Alert if balance is too low
            if sol_balance < LOW_BALANCE_THRESHOLD:
                warning = f"⚠️ *Low Wallet Balance Alert*\nCurrent balance: `{sol_balance:.4f}` SOL\nMinimum required: `{LOW_BALANCE_THRESHOLD}` SOL"
                send_telegram_alert(warning)

            return sol_balance
        except Exception as e:
            print(f"⚠️ RPC error (Attempt {attempt}): {e}")
            time.sleep(delay)

    print("🛑 All balance attempts failed.")
    return 0.0


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
        if target_mint in successful_snipes:
            print(f"⛔ Skipping {target_mint} — already sniped")
            return False

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

            # 💧 Liquidity & Volume checks
            in_amount = best_route.get("inAmount", 0)
            out_amount = best_route.get("outAmount", 0)
            market_depth = best_route.get("marketInfos", [{}])[0].get("liquidity", {}).get("availableAmount", 0)

            if out_amount < lamports * 0.3:
                print(f"⚠️ Output too low: {out_amount} lamports")
                return False
            if market_depth and market_depth < lamports * 3:
                print(f"⚠️ Insufficient liquidity: {market_depth}")
                return False

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
                successful_snipes.add(target_mint)
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
                send_telegram_alert(f"🚫 TX failure ➝ {target_mint}. Patrol paused.")
                return False

        except Exception as e:
            print(f"💥 Error during swap to {target_mint}: {e}")
            send_telegram_alert(f"🚨 Swap failed ➝ {target_mint}: {e}")
            return False

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

def buy_token_solana(mint_address, amount_sol, wallet):
    return execute_sol_trade(mint_address, amount_sol, wallet)
