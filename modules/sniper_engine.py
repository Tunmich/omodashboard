import requests
import time
import logging
from strategy.decision_engine import should_buy
from modules.solana_executor import buy_token_solana
from utils.sol_price_feed import fetch_sol_usd_price
from utils.solana_balance import get_sol_balance
from utils.telegram_alert import send_trade_alert, send_roi_alert
from utils.logger import log_trade

logging.basicConfig(level=logging.INFO)

USD_PER_TRADE = 1.00
MAX_DAILY_SOL = 0.05
total_sol_spent = 0
DEX_API_URL = "https://api.dexscreener.com/latest/dex/pairs"

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
        "name": pair.get("baseToken", {}).get("name", "Unknown"),
        "symbol": pair.get("baseToken", {}).get("symbol", "N/A"),
        "address": pair.get("baseToken", {}).get("address", "0x0"),
        "chain": pair.get("chainId", "solana"),
        "liquidity_usd": float(pair.get("liquidity", {}).get("usd", 0)),
        "price": float(pair.get("priceUsd", 0)),
        "social_score_x": pair.get("twitter", {}).get("followers", 0),
        "owner_renounced": False,
        "rug_check": False
    }

def scan_and_snipe():
    global total_sol_spent

    sol_price = fetch_sol_usd_price()
    if not sol_price:
        logging.warning("⚠️ Cannot fetch SOL price, skipping scan.")
        return

    amount_sol = round(USD_PER_TRADE / sol_price, 4)
    wallet_sol = get_sol_balance()

    if wallet_sol < amount_sol + 0.01:
        logging.warning(f"🛑 Not enough SOL to trade. Available: {wallet_sol:.4f}")
        return

    pairs = fetch_new_pairs()

    for pair in pairs:
        try:
            token = extract_token_info(pair)
            symbol = token["symbol"]
            address = token["address"]

            logging.info(f"🔍 Evaluating: {symbol} ({address})")

            if should_buy(token):
                if total_sol_spent + amount_sol > MAX_DAILY_SOL:
                    logging.info("🚫 Daily SOL cap reached.")
                    break

                tx_link = buy_token_solana(address, amount_sol=amount_sol)

                if tx_link:
                    logging.info(f"✅ Bought {symbol}: {tx_link}")
                    send_trade_alert(symbol, "solana", tx_link)
                    log_trade(symbol, "solana", amount_sol, "-", tx_link, "Success")
                    total_sol_spent += amount_sol

                    # Optional: Real sell and ROI logic here
                    # roi = evaluate_roi(...)
                    # send_roi_alert(symbol, roi, sell_tx_link)

                else:
                    logging.warning(f"🚫 Trade failed for {symbol}")
                    log_trade(symbol, "solana", amount_sol, "-", "-", "Failed")

            else:
                logging.info(f"⛔ SKIPPED: {symbol} did not pass screening")

        except Exception as e:
            logging.error(f"🔥 Error during scan: {e}")

        time.sleep(2)