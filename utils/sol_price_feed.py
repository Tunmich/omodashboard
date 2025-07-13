import requests

def fetch_sol_usd_price():
    try:
        res = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=solana&vs_currencies=usd")
        return float(res.json()["solana"]["usd"])
    except Exception as e:
        print(f"⚠️ Failed to fetch SOL price: {e}")
        return None