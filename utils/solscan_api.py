import requests

def fetch_token_price_solscan(token_address):
    """
    Query latest price of a SPL token via Solscan or comparable Solana data provider.
    """
    try:
        url = f"https://public-api.solscan.io/market/token/{token_address}"
        res = requests.get(url)
        data = res.json()
        return float(data.get("priceUsdt", 0))
    except Exception as e:
        print(f"⚠️ Failed to fetch SOL token price: {e}")
        return None