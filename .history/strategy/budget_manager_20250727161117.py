import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

MAX_DAILY_SOL = float(os.getenv("MAX_DAILY_SOL", "0.02"))
USD_PER_TRADE = float(os.getenv("USD_PER_TRADE", "0.0062"))
LOW_BALANCE_ALERT = float(os.getenv("LOW_BALANCE_ALERT", "0.01"))
COOLDOWN_SECONDS = int(os.getenv("COOLDOWN_SECONDS", "1800"))
ETH_PER_TRADE = float(os.getenv("ETH_PER_TRADE", "0.00027"))
SLIPPAGE_TOLERANCE = float(os.getenv("SLIPPAGE_TOLERANCE", "0.00015"))

def get_trade_allocation(total_usd: float, win_streak: int = 0) -> float:
    """
    Legacy allocation logic for trade sizing. Used by PatrolManager & HeartbeatMonitor.

    Args:
        total_usd (float): Available USD balance.
        win_streak (int): Current win streak.

    Returns:
        float: USD allocation amount.
    """
    capped_balance = min(total_usd, 5.0)

    streak_map = {
        0: 1.0,
        1: 1.5,
        2: 2.0,
        3: 3.0,
        4: 4.0,
    }

    allocation = streak_map.get(win_streak, 5.0)
    return min(allocation, capped_balance)

def get_sol_trade_allocation(wallet_sol_balance: float) -> float:
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
    if wallet_eth_balance < LOW_BALANCE_ALERT:
        return 0.0

    return min(ETH_PER_TRADE, wallet_eth_balance)

def is_trade_allowed(last_trade_time: float, current_time: float, daily_sol_spent: float) -> bool:
    cooldown_ok = (current_time - last_trade_time) >= COOLDOWN_SECONDS
    daily_limit_ok = daily_sol_spent < MAX_DAILY_SOL
    return cooldown_ok and daily_limit_ok

def get_slippage_tolerance() -> float:
    return SLIPPAGE_TOLERANCE

def get_live_sol_price() -> float:
    try:
        from utils.sol_price_feed import fetch_sol_usd_price
        return fetch_sol_usd_price()
    except Exception:
        return None
