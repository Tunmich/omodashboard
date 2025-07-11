# utils/balance_checker.py
from web3 import Web3

def get_wallet_balance(chain="Ethereum"):
    # 👻 Placeholder value; add actual web3 logic later
    return 0.05

def wallet_check():
    print(f"🔎 Wallet balance check:")
    chains = ["Ethereum", "BNB", "Base"]
    for c in chains:
        print(f"{c}: {get_wallet_balance(c)} ETH")