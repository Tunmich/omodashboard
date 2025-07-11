# utils/trade_predictor.py

from utils.roi_predictor import estimate_roi
from utils.risk_score import score_token_risk
from utils.filters import apply_filters

def predict_success(token):
    """
    Predict trade success using ROI + risk + filters
    """
    filters_passed = apply_filters(token)
    roi = estimate_roi(token)
    risk = score_token_risk(token)

    decision = roi > 1.05 and risk < 0.5 and filters_passed
    return {
        "roi": roi,
        "risk": risk,
        "filters_passed": filters_passed,
        "should_trade": decision
    }