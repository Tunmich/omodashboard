# validate_wallet.py
import os
import logging

from eth_account import Account
from dotenv import load_dotenv

load_dotenv()

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