# utils/token_security.py

import requests
import time
import os
from dotenv import load_dotenv

load_dotenv()
RUGCHECK_API_KEY = os.getenv("RUGCHECK_API_KEY")

def get_token_age(mint, api_key):
    try:
        url = f"https://api.helius.xyz/v0/token-metadata?mint={mint}&api-key={api_key}"
        res = requests.get(url, timeout=10).json()
        created_at = res.get("created_at")
        if not created_at:
            return 0  # fallback: treat as fresh token
        return time.time() - created_at
    except Exception as e:
        print(f"❌ Token age fetch error: {e}")
        return 0  # safest fallback

def get_creator_wallet(mint, api_key):
    try:
        url = f"https://api.helius.xyz/v0/token-metadata?mint={mint}&api-key={api_key}"
        res = requests.get(url).json()
        return res.get("update_authority", "")
    except Exception as e:
        print(f"❌ Error fetching creator wallet: {e}")
        return ""

def check_token_security(mint, chain_id="solana", api_key=RUGCHECK_API_KEY):
    url = f"https://api.gopluslabs.io/api/v1/token_security/{chain_id}"
    params = {"contract_addresses": mint}
    headers = {"Authorization": api_key} if api_key else {}
    try:
        response = requests.get(url, params=params, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("result", {}).get(mint.lower(), {})
    except Exception as e:
        print(f"❌ Error fetching token security for {mint}: {e}")
        return None

def is_good_contract(data):
    return data.get("is_open_source", False) and not data.get("is_proxy", False)

def is_bundled_supply(data):
    top10 = float(data.get("top10_holders_percentage", 0))
    return top10 < 80.0
