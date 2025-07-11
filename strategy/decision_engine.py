# strategy/decision_engine.py

import json
import os

# Optional: load scoring weights from config file
CONFIG_PATH = os.path.join("config", "decision_rules.json")

def load_config():
    try:
        with open(CONFIG_PATH, "r") as f:
            return json.load(f)
    except Exception:
        return {
            "buzz_score": 0.6,
            "risk_score": 0.4,
            "min_roi": 1.2,
            "max_price_impact": 15,
            "min_liquidity_usd": 10000,
            "social_score_min": 3,
            "allow_non_renounced": False,
            "flag_rugged_tokens": True
        }

def should_buy(token):
    """
    Returns True if a token passes decision logic.
    Includes price impact, liquidity, sentiment, social presence, owner flags.
    """
    cfg = load_config()

    try:
        buzz = token.get("buzz_score", 0)
        risk = token.get("risk_score", 1)
        roi = token.get("estimated_return", 0)
        price_impact = token.get("price_impact_pct", 100)
        liquidity = token.get("liquidity_usd", 0)
        social_score = token.get("social_score_x", 0)
        renounced = token.get("owner_renounced", False)
        is_flagged_rug = token.get("rug_check", False)

        if buzz < cfg["buzz_score"]:
            return False
        if risk > cfg["risk_score"]:
            return False
        if roi < cfg["min_roi"]:
            return False
        if price_impact > cfg["max_price_impact"]:
            return False
        if liquidity < cfg["min_liquidity_usd"]:
            return False
        if social_score < cfg["social_score_min"]:
            return False
        if not cfg["allow_non_renounced"] and not renounced:
            return False
        if cfg["flag_rugged_tokens"] and is_flagged_rug:
            return False

        return True

    except Exception:
        return False