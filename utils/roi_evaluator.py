import requests

def fetch_token_price_dexscreener(contract_address, chain):
    try:
        api_url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}/{contract_address}"
        response = requests.get(api_url)
        data = response.json()
        return float(data["pair"]["priceUsd"])
    except Exception as e:
        print(f"⚠️ Failed to fetch price for {contract_address} on {chain}: {e}")
        return None

def calculate_roi(buy_price, current_price):
    try:
        roi = ((current_price - buy_price) / buy_price) * 100
        return round(roi, 2)
    except Exception as e:
        print(f"⚠️ ROI calculation failed: {e}")
        return None