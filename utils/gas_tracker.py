# utils/gas_tracker.py

def get_gas_price(chain):
    """
    Return mocked gas price (Gwei) for the specified chain.
    Replace with actual API logic later.
    """
    gas_prices = {
        "Ethereum": 34.5,
        "BNB": 8.1,
        "Base": 12.3,
        "Solana": 0.0001  # not Gwei but placeholder for consistency
    }
    return gas_prices.get(chain, "N/A")