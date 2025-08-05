import os
from dotenv import load_dotenv

# 🔧 Load environment variables
load_dotenv()

# 🚀 Real logic budget parameters
MAX_DAILY_SOL = float(os.getenv("MAX_DAILY_SOL", "0.02"))
USD_PER_TRADE = float(os.getenv("USD_PER_TRADE", "0.0062"))
LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "1800"))
ETH_PER_TRADE = float(os.getenv("ETH_PER_TRADE", "0.00027"))
SLIPPAGE_TOLERANCE = float(os.getenv("SLIPPAGE_TOLERANCE", "0.00015"))

def get_sol_trade_allocation(wallet_sol_balance: float) -> float:
    """
    Determines how much SOL to allocate for a trade based on USD_PER_TRADE and current balance.

    Args:
        wallet_sol_balance (float): Current wallet SOL balance.

    Returns:
        float: SOL amount to use for next trade.
    """
    if wallet_sol_balance < LOW_BALANCE_ALERT:
        return 0.0  # Block trade due to low balance

    sol_price_usd = get_live_sol_price()
    if not sol_price_usd:
        return 0.0  # Fail-safe for missing price

    sol_allocation = round(USD_PER_TRADE / sol_price_usd, 6)
    if wallet_sol_balance < sol_allocation + 0.001:
        return 0.0  # Not enough buffer for transaction cost

    return min(sol_allocation, wallet_sol_balance)

def get_eth_trade_allocation(wallet_eth_balance: float) -> float:
    """
    Determines how much ETH to allocate for a trade.

    Args:
        wallet_eth_balance (float): Current wallet ETH balance.

    Returns:
        float: ETH amount to use for next trade.
    """
    if wallet_eth_balance < LOW_BALANCE_ALERT:
        return 0.0

    return min(ETH_PER_TRADE, wallet_eth_balance)

def is_trade_allowed(last_trade_timestamp: float, current_timestamp: float, daily_spent: float) -> bool:
    """
    Checks whether trade can be executed based on cooldown and daily limits.

    Args:
        last_trade_timestamp (float): Epoch time of last trade.
        current_timestamp (float): Current epoch time.
        daily_spent (float): Total SOL spent today.

    Returns:
        bool: True if trade is allowed, else False.
    """
    cooldown_passed = (current_timestamp - last_trade_timestamp) >= COOLDOWN_SECONDS
    daily_cap_ok = daily_spent < MAX_DAILY_SOL
    return cooldown_passed and daily_cap_ok

def get_slippage_tolerance() -> float:
    """
    Returns slippage tolerance value.

    Returns:
        float: Slippage tolerance setting.
    """
    return SLIPPAGE_TOLERANCE

def get_live_sol_price() -> float:
    """
    Retrieves live SOL price in USD using external price feed.

    Returns:
        float: SOL price in USD.
    """
    try:
        from utils.sol_price_feed import fetch_sol_usd_price
        return fetch_sol_usd_price()
    except Exception:
        return None
