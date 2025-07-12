# modules/sniper_sniff.py

import requests
import time
import logging
from strategy.decision_engine import should_buy
from modules.web3_buy import buy_token

# Configure logging
logging.basicConfig(level=logging.INFO)

DEX_API_URL = "https://api.dexscreener.com/latest/dex/pairs"

def fetch_new_pairs(chain="ethereum", limit=20):
    """Fetches recently listed token pairs from DexScreener"""
    try:
        response = requests.get(f"{DEX_API_URL}/{chain}")
        data = response.json().get("pairs", [])
        return data[:limit]
    except Exception as e:
        logging.error(f"Failed to fetch new pairs: {e}")
        return []

def extract_token_info(pair):
    return {
        "name": pair.get("baseToken", {}).get("name"),
        "symbol": pair.get("baseToken", {}).get("symbol"),
        "address": pair.get("baseToken", {}).get("address"),
        "chain": pair.get("chainId"),
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "price": float(pair.get("priceUsd", 0)),
        "social_score_x": pair.get("twitter", {}).get("followers", 0),
        "owner_renounced": False,  # can be updated with rug checks
        "rug_check": False
    }

def scan_and_evaluate():
    pairs = fetch_new_pairs(chain="ethereum")  # Can loop through multiple chains
    for pair in pairs:
        token = extract_token_info(pair)
        if should_buy(token):
            # Trigger buy function
            tx_link = buy_token(token["address"], amount_eth=0.01)
            if tx_link:
                logging.info(f"✅ Token sniped: {tx_link}")
            else:
                logging.info(f"✅ Token sniped: {token['symbol']} ({token['address']})")
        else:
            logging.info(f"⛔ SKIPPED: {token['symbol']} did not pass screening.")
        time.sleep(2)  # gentle pacing to avoid rate limits