import logging

# utils/risk_score.py

def score_token_risk(token):
    """
    Score risk from 0 (safe) to 1 (dangerous).
    """
    risk = 0.0

    if token.get("honeypot", False):
        risk += 0.9
    if token.get("new_token", True):
        risk += 0.3
    if token.get("owner_percent", 0) > 5:
        risk += 0.4
    if token.get("social_score", 0) >= 0.5:
        risk -= 0.2

    return max(0.0, min(risk, 1.0))