# utils/budget_manager.py
import logging

def get_trade_allocation(total_usd, win_streak=0):
    """
    Allocates trade budget based on current win streak.
    - Starts at $1.
    - Increases gradually per win.
    - Resets to $1 on a loss.
    - Capped at $5.
    """
    # Cap wallet to $5 max for low-stake test strategy
    simulated_budget = min(total_usd, 5.0)

    # Define win-streak based increments
    streak_map = {
        0: 1.0,
        1: 1.5,
        2: 2.0,
        3: 3.0,
        4: 4.0,
    }

    # Get allocation based on win streak, default to $5 for >= 5 wins
    allocation = streak_map.get(win_streak, 5.0)

    # Ensure we don’t exceed wallet amount
    return min(allocation, simulated_budget)
