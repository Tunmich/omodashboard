import logging
import json
import os

# 📁 Config path
CONFIG_PATH = os.path.join("config", "decision_rules.json")

# ✅ Default config profiles
DEFAULT_PROFILE = {
    "min_liquidity_usd": 1000,
    "min_social_score": 0,
    "max_price_impact": 90,
    "require_renounced": False,
    "flag_rugged": False,
    "min_age_seconds": 60,
    "momentum_gain_pct": 5,
    "momentum_window_seconds": 300,
    "max_rug_score": 1.0,
    "fuzzy_margin": 0.1,
    "thresholds": {
        "buzz_score": 70,
        "roi_score": 65,
        "risk_score": 35,
        "total_score": 120
    }
}

CHAIN_PROFILES = {
    "Solana": {**DEFAULT_PROFILE},
    "Ethereum": {
        **DEFAULT_PROFILE,
        "min_liquidity_usd": 5000,
        "require_renounced": True,
        "thresholds": {
            "buzz_score": 75,
            "roi_score": 70,
            "risk_score": 30,
            "total_score": 125
        }
    },
    "Base": {
        **DEFAULT_PROFILE,
        "min_liquidity_usd": 3000,
        "thresholds": {
            "buzz_score": 72,
            "roi_score": 68,
            "risk_score": 34,
            "total_score": 122
        }
    }
}

def load_config(chain: str) -> dict:
    try:
        with open(CONFIG_PATH, "r") as f:
            user_cfg = json.load(f)
            chain_cfg = user_cfg.get(chain, {})
            default = CHAIN_PROFILES.get(chain, DEFAULT_PROFILE)
            return {k: chain_cfg.get(k, default[k]) for k in default}
    except Exception:
        return CHAIN_PROFILES.get(chain, DEFAULT_PROFILE)

def boost_score(token: dict) -> float:
    boost = 0
    chain = token.get("chain", "")
    name = token.get("name", "").lower()
    volume = float(token.get("volume_usd", 0))
    liquidity = float(token.get("liquidity_usd", 0))

    if chain == "Solana":
        if token.get("tweet_text"):
            boost += 15
        if name.startswith("sol"):
            boost += 5
    else:
        if token.get("source") == "Twitter":
            boost += 10
        if "pair_url" in token:
            boost += 15
        if volume > 50000:
            boost += 10
        if liquidity > 10000:
            boost += 5

    return boost

def log_rejection(token: dict, reason: str):
    logging.info(f"❌ Rejected [{token.get('address', 'unknown')}]: {reason}")

def within_fuzzy(actual: float, target: float, margin: float) -> bool:
    return actual >= target - (target * margin)

# 🧠 Memory cache for last token decision
LAST_TRACE = {}

def trace_decision(token, fusion_boost, final_score, result):
    address = token.get("address", "unknown")
    verdict = "APPROVED" if result else "REJECTED"

    log = f"""
📡 Token: {address}
🔢 Buzz: {token.get("buzz_score", '?')} | ROI: {token.get("roi_score", '?')} | Risk: {token.get("risk_score", '?')}
⚡ Fusion Boost: {fusion_boost}
📊 Final Score: {final_score}
🎯 Verdict: {verdict}
"""

    logging.info(log)
    LAST_TRACE["trace"] = log
    LAST_TRACE["result"] = verdict

def evaluate_signal(signal_payload: dict):
    print(f"🧠 Evaluating signal: {signal_payload['source']}")
    # Add full strategy logic later — this prevents import error

def should_buy(token: dict) -> bool:
    try:
        required_keys = ["buzz_score", "risk_score", "roi_score", "symbol"]
        if not all(k in token and token[k] != "" for k in required_keys):
            log_rejection(token, "missing fields")
            return False

        chain = token.get("chain", "Solana")
        cfg = load_config(chain)
        th = cfg["thresholds"]
        margin = cfg.get("fuzzy_margin", 0.1)

        buzz = float(token.get("buzz_score", 0))
        roi = float(token.get("roi_score", 0))
        risk = float(token.get("risk_score", 100))
        fusion_boost = boost_score(token)

        liquidity = float(token.get("liquidity_usd", 0))
        age = float(token.get("age_seconds", 999999))
        social = float(token.get("social_score", 0))
        renounced = token.get("is_renounced", True)
        flagged_rug = token.get("rug_flag", False)
        price_impact = float(token.get("price_impact_pct", 0))
        momentum = float(token.get("momentum_5min_pct", 0))

        # 🧠 Config filters
        if liquidity < cfg["min_liquidity_usd"]:
            log_rejection(token, "liquidity too low")
            return False
        if social < cfg["min_social_score"]:
            log_rejection(token, "low social score")
            return False
        if age < cfg["min_age_seconds"]:
            log_rejection(token, "token too young")
            return False
        if cfg["require_renounced"] and not renounced:
            log_rejection(token, "contract not renounced")
            return False
        if cfg["flag_rugged"] and flagged_rug:
            log_rejection(token, "flagged as rug")
            return False
        if price_impact > cfg["max_price_impact"]:
            log_rejection(token, "high price impact")
            return False
        if momentum < cfg["momentum_gain_pct"]:
            log_rejection(token, "momentum weak")
            return False

        # 🧮 Final score
        total = buzz + roi - risk + fusion_boost

        decision_result = (
            within_fuzzy(buzz, th["buzz_score"], margin) and
            within_fuzzy(roi, th["roi_score"], margin) and
            risk <= th["risk_score"] * (1 + margin) and
            total >= th["total_score"] * (1 - margin)
        )

        trace_decision(token, fusion_boost, total, decision_result)

        if decision_result:
            return True

        log_rejection(token, f"score below target ({total:.1f})")
        return False

    except Exception as e:
        logging.error(f"🔥 Decision error: {e}")
        return False
