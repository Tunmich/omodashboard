import os
from dotenv import load_dotenv

# Load .env configurations
load_dotenv()

# 💰 Budget Parameters (from .env)
MAX_DAILY_SOL = float(os.getenv("MAX_DAILY_SOL", "0.02"))
USD_PER_TRADE = float(os.getenv("USD_PER_TRADE", "0.0062"))
LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "1800"))
ETH_PER_TRADE = float(os.getenv("ETH_PER_TRADE", "0.00027"))
SLIPPAGE_TOLERANCE = float(os.getenv("SLIPPAGE_TOLERANCE", "0.00015"))

def get_sol_trade_allocation(wallet_sol_balance: float) -> float:
    """
    Calculates SOL allocation per trade based on USD value.

    Args:
        wallet_sol_balance (float): Current SOL balance.

    Returns:
        float: SOL amount to trade.
    """
    if wallet_sol_balance < LOW_BALANCE_ALERT:
        return 0.0

    sol_price = get_live_sol_price()
    if not sol_price or sol_price == 0.0:
        return 0.0

    sol_equivalent = round(USD_PER_TRADE / sol_price, 6)
    buffer = 0.001

    if wallet_sol_balance < sol_equivalent + buffer:
        return 0.0

    return min(sol_equivalent, wallet_sol_balance)

def get_eth_trade_allocation(wallet_eth_balance: float) -> float:
    """
    Calculates ETH allocation based on ETH_PER_TRADE.

    Args:
        wallet_eth_balance (float): Current ETH balance.

    Returns:
        float: ETH amount to trade.
    """
    if wallet_eth_balance < LOW_BALANCE_ALERT:
        return 0.0

    return min(ETH_PER_TRADE, wallet_eth_balance)

def is_trade_allowed(last_trade_time: float, current_time: float, daily_sol_spent: float) -> bool:
    """
    Validates whether trade is permitted by cooldown and daily cap.

    Args:
        last_trade_time (float): Epoch time of last trade.
        current_time (float): Current epoch time.
        daily_sol_spent (float): Total SOL spent today.

    Returns:
        bool: True if trade is permitted.
    """
    cooldown_ok = (current_time - last_trade_time) >= COOLDOWN_SECONDS
    daily_limit_ok = daily_sol_spent < MAX_DAILY_SOL
    return cooldown_ok and daily_limit_ok

def get_slippage_tolerance() -> float:
    """
    Returns current slippage tolerance setting.

    Returns:
        float: Slippage percentage.
    """
    return SLIPPAGE_TOLERANCE

def get_live_sol_price() -> float:
    """
    Fetches current live SOL/USD price from strategy/sol_price_feed.

    Returns:
        float: SOL price in USD.
    """
    try:
        from strategy.sol_price_feed import fetch_sol_usd_price
        return fetch_sol_usd_price()
    except Exception:
        return None
