import os
import threading
import time
import requests
import random
from dotenv import load_dotenv
from solders.keypair import Keypair
from modules.solana_executor import execute_sol_trade, get_wallet_balance
from utils.token_scanner import scan_solana_tokens
from utils.wallet_mapper import get_safe_evm_wallet

# ------------------- ENV INIT AND WALLET ------------------

load_dotenv()

# Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
chat_id = os.getenv("TELEGRAM_CHAT_ID")
raw_key = os.getenv("WALLET_PRIVATE_KEY")

if not bot_token or not chat_id or not raw_key:
    raise EnvironmentError("❌ Missing required environment variables.")

wallet = Keypair.from_base58_string(raw_key)

# ------------------- BUSINESS CORE LOGIC ------------------

def get_sol_price() -> float:
    try:
        url = "https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd"
        res = requests.get(url).json()
        return res["solana"]["usd"]
    except Exception:
        return 25.0  # fallback

def get_trading_budget_in_sol() -> float:
    usd_budget = float(os.getenv("USD_PER_TRADE", "0.05"))
    price = get_sol_price()
    return usd_budget / price

def scan_tokens_and_select_targets():
    mint_raw = os.getenv("AUTO_MINT_LIST", "")
    return [mint.strip() for mint in mint_raw.split(",") if mint.strip()]

def emergency_stop(wallet, threshold: float) -> bool:
    balance = get_wallet_balance(wallet.pubkey())
    return balance < threshold

# Placeholder for the token validation logic - override as needed
def is_valid_token(mint_address: str) -> bool:
    # Implement token validation logic here
    return True

class OmoBotCore:
    def __init__(self, wallet):
        self.wallet = wallet
        self.mint_targets = scan_tokens_and_select_targets()
        self.patrol_active = False

    def start_patrol(self):
        if self.patrol_active:
            print("Patrol already active")
            return
        self.patrol_active = True
        threading.Thread(target=self._patrol_loop, daemon=True).start()

    def stop_patrol(self):
        self.patrol_active = False

    def _patrol_loop(self):
        low_threshold = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
        while self.patrol_active:
            if emergency_stop(self.wallet, low_threshold):
                print("🛑 Patrol auto-disabled due to low balance.")
                self.patrol_active = False
                break
            live_mints = scan_solana_tokens(limit=10)
            valid_mints = [mint for mint in live_mints if is_valid_token(mint)]
            if not valid_mints:
                print("⚠️ No valid mints found. Skipping patrol cycle.")
                time.sleep(600)
                continue
            mint = random.choice(valid_mints)
            # Implement trade or notification here
            print(f"🎯 Would execute trade on token: {mint}")
            time.sleep(60)

    def status(self):
        sol_balance = get_wallet_balance(self.wallet.pubkey())
        return {
            "sol_balance": sol_balance,
            "patrol_active": self.patrol_active,
            "targets": len(self.mint_targets)
        }

# --- Other utilities exposed by core as needed ---
