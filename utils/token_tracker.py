# utils/token_tracker.py

import time

# 🧠 Store token prices over time
token_history = {}  # e.g. {mint: [{"price": 0.0021, "ts": 1691200000}, ...]}

def record_token_price(mint: str, price: float):
    now = time.time()
    if mint not in token_history:
        token_history[mint] = []
    token_history[mint].append({"price": price, "ts": now})

    # 🧹 Keep only last 10 minutes of history
    token_history[mint] = [p for p in token_history[mint] if now - p["ts"] <= 600]

def get_price_change_5min(mint: str) -> float:
    now = time.time()
    history = token_history.get(mint, [])
    recent = [p for p in history if now - p["ts"] >= 300]
    if not recent or len(history) < 2:
        return 0.0

    earliest = sorted(recent, key=lambda x: x["ts"])[0]
    latest = history[-1]

    if earliest["price"] == 0:
        return 0.0

    return ((latest["price"] - earliest["price"]) / earliest["price"]) * 100
