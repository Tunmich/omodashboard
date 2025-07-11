# utils/roi_predictor.py

def estimate_roi(token):
    """
    Predict ROI based on basic token price projection.
    Later upgrade to use chart data, volume, buzz, etc.
    """
    current_price = float(token.get("token_price_usd", 0.003))
    projected_price = float(token.get("target_price_usd", current_price * 1.2))
    roi = projected_price / current_price
    return round(roi, 4)