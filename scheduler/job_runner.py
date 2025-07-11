import os
import time
import logging
from datetime import datetime
import pytz
import sys

from utils.logger_config import setup_logger
setup_logger()

# 🧠 Enable clean imports from project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# 🚀 Core Modules
from scanner.eth_scanner import scan_eth_tokens
from scanner.bnb_scanner import scan_bnb_tokens
from scanner.base_scanner import scan_base_tokens
from scanner.solana_scanner import scan_solana_tokens

from trading.auto_trade import simulate_trade
from alerts.telegram import send_token_alert
from utils.token_logger import log_token_snapshot
from utils.web3_factory import get_web3_provider
from strategy.decision_engine import should_buy

# ✅ Ensure logs folder exists
os.makedirs("logs", exist_ok=True)

# 📝 Trade Logger
def log_trade(token, filename="logs/trades.csv"):
    tz = pytz.timezone("Africa/Lagos")
    timestamp = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

    token_data = {
        "Timestamp": timestamp,
        "name": token.get("name"),
        "chain": token.get("chain"),
        "address": token.get("address"),
        "buzz_score": token.get("buzz_score"),
        "risk_score": token.get("risk_score"),
        "roi_score": token.get("roi_score"),
        "estimated_return": token.get("estimated_return"),
        "estimated_value": token.get("estimated_value", ""),
        "estimated_pl": token.get("estimated_pl", ""),
        "token_price_usd": token.get("token_price_usd", ""),
        "block_number": token.get("block_number", ""),
        "gas_price": token.get("gas_price", ""),
        "name_on_chain": token.get("name_on_chain", ""),
        "symbol": token.get("symbol", ""),
        "Status": "Confirmed"
    }

    write_header = not os.path.exists(filename)
    with open(filename, mode="a", newline="") as file:
        import csv
        writer = csv.DictWriter(file, fieldnames=token_data.keys())
        if write_header:
            writer.writeheader()
        writer.writerow(token_data)

# 📋 Log Setup
logging.basicConfig(
    filename="logs/token_scan.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

# 🔍 Aggregate Token Sources
def get_all_tokens():
    try:
        tokens = []
        tokens += scan_eth_tokens() or []
        tokens += scan_bnb_tokens() or []
        tokens += scan_base_tokens() or []
        tokens += scan_solana_tokens() or []
        return tokens
    except Exception as e:
        logging.error(f"Error fetching tokens: {str(e)}")
        return []

# 🚦 Main Loop With Chain-aware Enrichment
def process_tokens():
    logging.info("🚀 Starting scan for new meme tokens")
    tokens = get_all_tokens()

    for token in tokens:
        try:
            log_token_snapshot(token)

            # 🧠 Attach blockchain metadata
            provider = get_web3_provider(token["chain"])
            if provider:
                try:
                    token["block_number"] = provider.get_block_number()
                    token["gas_price"] = provider.get_gas_price()

                    metadata = provider.get_token_info(token["address"])
                    token["name_on_chain"] = metadata.get("name", "")
                    token["symbol"] = metadata.get("symbol", "")
                    token["decimals"] = metadata.get("decimals", "")
                except Exception as rpc_err:
                    logging.warning(f"⚠️ RPC enrichment failed for {token['name']} ({token['chain']}): {rpc_err}")
            else:
                logging.warning(f"🚫 No RPC provider for {token['chain']} → skipping enrichment.")

            # 🧪 Decision Engine
            if should_buy(token):
                send_token_alert(token)
                simulate_trade(token)
                log_trade(token)
                logging.info(f"✅ TRADED: {token['name']} - {token['chain']} ({token['address']})")
            else:
                logging.info(f"❌ Skipped: {token['name']} - {token['chain']}")

        except Exception as err:
            logging.warning(f"💥 Error processing {token.get('name', 'Unknown Token')}: {str(err)}")

# 🕒 Auto-trigger every 10 mins
def run_scheduler():
    while True:
        process_tokens()
        logging.info("🕒 Waiting 10 minutes...\n")
        time.sleep(600)

# 🚀 Entry
if __name__ == "__main__":
    run_scheduler()