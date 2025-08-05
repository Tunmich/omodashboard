def get_market_volatility_index(market_data: dict) -> float:
    """
    Returns a scaled volatility index from 0.0 to 1.0.

    Args:
        market_data (dict): Contains price history, volume change, etc.

    Returns:
        float: Normalized volatility index.
    """
    try:
        price_change = abs(market_data["price_change_pct"])  # e.g., in last 30 min
        volume_change = abs(market_data["volume_change_pct"])

        # Weighted formula: you can customize the weights
        index = (0.6 * price_change + 0.4 * volume_change) / 100
        return min(index, 1.0)
    except (KeyError, TypeError):
        return 0.5  # Default to moderate volatility
