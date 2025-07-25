# utils/trade_logger.py

import csv
import os
import datetime
import logging

LOG_FILE = "logs/trades.csv"
FIELDNAMES = [
    "Timestamp",
    "Token",
    "Chain",
    "Amount_ETH",
    "Estimated_Payout",
    "Tx_Link",
    "Status"
]

def log_trade(token, chain, amount_eth, payout_estimate, tx_link, status="Success"):
    """
    Logs trade info to CSV + console output via logging.
    """
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Timestamp": timestamp,
        "Token": token,
        "Chain": chain,
        "Amount_ETH": amount_eth,
        "Estimated_Payout": payout_estimate,
        "Tx_Link": tx_link,
        "Status": status
    }

    # 🛡 Ensure log folder exists
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # ✍️ Ensure CSV file exists
    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if not file_exists:
            writer.writeheader()
        writer.writerow(entry)

    # 🖥 Optional debug output
    logging.info(
        f"📝 Trade logged — Token: {token} | Chain: {chain} | "
        f"Amount: {amount_eth} | Payout: {payout_estimate} | "
        f"Tx: {tx_link} | Status: {status}"
    )
