import random
from datetime import datetime, timedelta


def enrich_token_data(token: dict) -> dict:
    enriched = token.copy()

    # 💧 Liquidity fallback
    enriched["liquidity_usd"] = token.get("liquidity_usd") or random.randint(5000, 50000)

    # ⏳ Simulate age detection
    if "mint_time" in token:
        minted = datetime.strptime(token["mint_time"], "%Y-%m-%d %H:%M:%S")
        enriched["age_seconds"] = int((datetime.utcnow() - minted).total_seconds())
    else:
        enriched["age_seconds"] = random.randint(600, 86400)

    # 🧮 ROI score based on volume + momentum
    volume = float(token.get("volume_usd", 10000))
    price_change = random.uniform(2, 25)
    enriched["momentum_5min_pct"] = price_change
    enriched["roi_score"] = min(int(volume / 1000 + price_change), 100)

    # ⚠️ Risk score based on liquidity + age
    liquidity = enriched["liquidity_usd"]
    age = enriched["age_seconds"]
    ruggedness = max(0, 100 - int((liquidity + age) / 1000))
    enriched["risk_score"] = min(ruggedness, 95)

    return enriched
