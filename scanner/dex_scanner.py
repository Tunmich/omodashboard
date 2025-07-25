import requests
import logging

DEX_SCREENER_API = "https://api.dexscreener.com/latest/dex/pairs"

def scan_trending_tokens(chain="ethereum"):
    """
    Fetches trending tokens for a given chain from DexScreener.
    Supports: ethereum, bsc, base, polygon, etc.
    """
    try:
        url = f"{DEX_SCREENER_API}/{chain}"
        res = requests.get(url, timeout=10)
        data = res.json()

        tokens = []
        for pair in data.get("pairs", [])[:10]:  # top 10 trending pairs
            tokens.append({
                "name": pair.get("baseToken", {}).get("name", "Unknown"),
                "symbol": pair.get("baseToken", {}).get("symbol", ""),
                "address": pair.get("baseToken", {}).get("address", ""),
                "chain": chain.capitalize(),
                "token_price_usd": pair.get("priceUsd"),
                "liquidity_usd": pair.get("liquidity", {}).get("usd", ""),
                "volume_usd": pair.get("volume", {}).get("h24", ""),
                "pair_url": pair.get("url", "")
            })

        return tokens
    except Exception as e:
        logging.warning(f"⚠️ DexScreener API failed: {e}")
        return []
