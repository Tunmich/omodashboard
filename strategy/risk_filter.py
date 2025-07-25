# strategy/risk_filter.py

import logging
import os

# Filter mode: strict | relaxed | adaptive
FILTER_MODE = os.getenv("FILTER_MODE", "adaptive")

def is_strict_rug_score(rug_score):
    return rug_score <= 0.25

def is_relaxed_rug_score(rug_score):
    return rug_score <= 0.75

def should_allow_rug(token):
    rug_score = token.get("rug_score", 1.0)
    momentum = token.get("price_change_5min_pct", 0)

    if FILTER_MODE == "strict":
        return is_strict_rug_score(rug_score)

    elif FILTER_MODE == "relaxed":
        return is_relaxed_rug_score(rug_score)

    elif FILTER_MODE == "adaptive":
        if rug_score <= 0.25:
            return True
        elif rug_score <= 0.5 and momentum > 5:
            logging.info(f"🚀 Adaptive override: {token['symbol']} momentum={momentum:.2f}% rug={rug_score}")
            return True
        elif rug_score <= 0.75 and momentum > 10:
            logging.info(f"⚠️ High-momentum override: {token['symbol']} momentum={momentum:.2f}% rug={rug_score}")
            return True

    logging.info(f"⛔ SKIPPED: {token['symbol']} rug_score={rug_score} exceeds threshold ({FILTER_MODE})")
    return False
