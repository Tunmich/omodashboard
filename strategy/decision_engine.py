import logging

def should_trade(token, risk_score, filters_passed, roi):
    """
    Final decision logic to trigger trade based on combined factors.
    """
    if not filters_passed:
        return False
    if risk_score < 0.3:
        return False
    if roi < 1.05:
        return False
    return True
