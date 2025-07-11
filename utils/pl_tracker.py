import logging


def estimate_trade_pl(token):
    """
    Estimate profit/loss in USD based on token output and price.
    Requires:
        - token["estimated_return"]
        - token["token_price_usd"]
        - token["trade_amount_usd"]
    """
    try:
        output = float(token.get("estimated_return", 0))
        price = float(token.get("token_price_usd", 0))
        budget = float(token.get("trade_amount_usd", 0))

        estimated_value = output * price
        pl = estimated_value - budget
        return pl

    except Exception as e:
        print(f"⚠️ Error estimating P/L for {token.get('name', 'Unknown')}: {e}")
        return 0