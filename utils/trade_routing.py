# utils/trade_routing.py

def select_optimal_chain():
    """
    Return the name of the chain with highest combined score.
    Placeholder logic for routing. Later replace with real conditions.
    """
    scores = {
        "Ethereum": 0.85,
        "BNB": 0.65,
        "Base": 0.50,
        "Solana": 0.70
    }
    return max(scores, key=scores.get)