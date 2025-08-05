# tools/env_inspector.py

import os
import re
from dotenv import load_dotenv
from utils.wallet_mapper import get_safe_evm_wallet

load_dotenv()

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

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

def scan_env_usage():
    print("🔎 Scanning .env usage across project...\n")
    for root, _, files in os.walk(PROJECT_ROOT):
        for file in files:
            if file.endswith(".py"):
                full_path = os.path.join(root, file)
                with open(full_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    if "load_dotenv" in content or "os.getenv" in content:
                        print(f"🧠 {full_path.replace(PROJECT_ROOT, '')} uses `.env`")

def show_env_snapshot():
    print("\n📦 Current .env snapshot loaded in runtime:\n")
    for key in os.environ:
        if key.upper().startswith("RPC_") or key.upper() in [
            "OMO_CHAIN_MODE", "WALLET_ADDRESS", "EVM_WALLET_ADDRESS",
            "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID", "USD_PER_TRADE",
            "INFURA_PROJECT_ID", "HELIUS_API_KEY", "RUGCHECK_API_KEY"
        ]:
            print(f"{key} = {os.getenv(key)}")

if __name__ == "__main__":
    scan_env_usage()
    show_env_snapshot()
