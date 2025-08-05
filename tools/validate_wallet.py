# validate_wallet.py
import os
import logging

from eth_account import Account
from dotenv import load_dotenv
from utils.wallet_mapper import get_safe_evm_wallet

load_dotenv()
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

def validate():
    pk = os.getenv("PRIVATE_KEY")
    wallet_env = os.getenv("WALLET_ADDRESS")

    if not pk or not wallet_env:
        print("❌ PRIVATE_KEY or WALLET_ADDRESS not found in .env")
        return

    try:
        # Create account object from private key
        account = Account.from_key(pk)
        derived_address = account.address

        # Compare derived vs stored
        print(f"🔍 Derived Address: {derived_address}")
        print(f"📦 .env Address:     {wallet_env}")

        if derived_address.lower() == wallet_env.lower():
            print("✅ Addresses match! Your wallet is properly configured.")
        else:
            print("❌ Address mismatch! Double-check your .env values.")
    except Exception as e:
        print(f"⚠️ Error during validation: {e}")

if __name__ == "__main__":
    validate()