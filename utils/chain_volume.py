import logging

# utils/chain_volume.py

def get_chain_activity():
    """
    Return fake normalized chain volume values for now.
    Later use GeckoTerminal or DexScreener APIs.
    """
    return {
        "Ethereum": 0.95,
        "BNB": 0.75,
        "Base": 0.60,
        "Solana": 0.20  # placeholder
    }