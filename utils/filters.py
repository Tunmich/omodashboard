import logging

# utils/filters.py

def apply_filters(token):
    """
    Filter out tokens that are low quality, honeypots, or suspicious.
    """
    if token.get("liquidity_usd", 0) < 1000:
        return False
    if token.get("buyers_1h", 0) < 10:
        return False
    if token.get("honeypot", False):
        return False
    return True