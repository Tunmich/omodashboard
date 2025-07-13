import requests
import time
import logging
from strategy.decision_engine import should_buy
from modules.solana_executor import buy_token_solana
from utils.sol_price_feed import fetch_sol_usd_price
from utils.solana_balance import get_sol_balance
from utils.solscan_api import fetch_token_price_solscan

from utils.solscan_api import fetch_token_price_solscan

def evaluate_roi(buy_price_usd, token_address, amount_sold):
    current_price = fetch_token_price_solscan(token_address)
    if not current_price:
        return "?"

    value_now = current_price * amount_sold
    roi = ((value_now - buy_price_usd) / buy_price_usd) * 100
    return round(roi, 2)


logging.basicConfig(level=logging.INFO)
DEX_API_URL = "https://api.dexscreener.com/latest/dex/pairs"
USD_PER_TRADE = 1.00
MAX_DAILY_SOL = 0.35
total_sol_spent = 0

def fetch_new_pairs(limit=20):
    try:
        response = requests.get(f"{DEX_API_URL}/solana")
        data = response.json().get("pairs", [])
        return data[:limit]
    except Exception as e:
        logging.error(f"❌ Failed to fetch Solana pairs: {e}")
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
        "owner_renounced": False,
        "rug_check": False
    }

def scan_and_evaluate():
    sol_price = fetch_sol_usd_price()
    if not sol_price:
        logging.warning("⚠️ Cannot fetch SOL price, skipping scan.")
        return

    sol_amount = round(USD_PER_TRADE / sol_price, 4)
    wallet_sol = get_sol_balance()

    if wallet_sol < sol_amount + 0.01:
        logging.warning(f"🛑 Insufficient balance. Available: {wallet_sol:.4f} SOL")
        return

    pairs = fetch_new_pairs()

    for pair in pairs:
        try:
            token = extract_token_info(pair)
            name = token.get("name", "Unknown")
            symbol = token.get("symbol", "N/A")
            address = token.get("address", "0x0")
            logging.info(f"🔍 Evaluating: {symbol} ({address})")

            if should_buy(token):
                if total_sol_spent + sol_amount > MAX_DAILY_SOL:
                    logging.info("🚫 Daily SOL cap reached. Standing down.")
                    break

                tx_link = buy_token_solana(token["address"], amount_sol=sol_amount)

                if tx_link:
                    logging.info(f"✅ SPL token sniped: {tx_link}")
                    total_sol_spent += sol_amount
                else:
                    logging.warning(f"⚠️ Trade failed for {symbol} ({address})")
            else:
                logging.info(f"⛔ SKIPPED: {symbol} didn’t pass screening")

        except Exception as e:
            logging.error(f"🔥 Error during scan for {symbol}: {e}")

        time.sleep(2)