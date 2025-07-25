# utils/budget_manager.py

def get_trade_allocation(total_usd: float, win_streak: int = 0) -> float:
    """
    Allocates trade budget based on current win streak.

    Strategy:
    - Starts at $1.
    - Increases incrementally per win.
    - Resets to $1 on a loss.
    - Capped at $5.
    
    Args:
        total_usd (float): Available wallet balance.
        win_streak (int): Current consecutive win count.
        
    Returns:
        float: Allocation for next trade.
    """
    # Ensure wallet cap — test bot runs on <$10 budget
    simulated_budget = min(total_usd, 5.0)

    # Define win-streak-based increments
    streak_map = {
        0: 1.0,
        1: 1.5,
        2: 2.0,
        3: 3.0,
        4: 4.0
    }

    # Use streak map or $5 max for streaks ≥ 5
    allocation = streak_map.get(win_streak, 5.0)

    # Final guard against exceeding wallet
    return min(allocation, simulated_budget)
