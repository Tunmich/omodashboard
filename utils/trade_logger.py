import csv
from datetime import datetime
import os
import logging

LOG_FILE = "logs/trades.csv"

def log_trade(token):
    os.makedirs("logs", exist_ok=True)
    new_trade = [
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        token["name"],
        token["chain"],
        token["address"],
        token["buzz_score"],
        "Yes" if token["liquidity"] else "No",
        "Yes" if token["rug_check"] else "No",
        "Yes" if token["ownership_renounced"] else "No"
    ]

    file_exists = os.path.isfile(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "Timestamp", "Name", "Chain", "Contract", "Buzz Score",
                "Liquidity", "Rug Check", "Ownership Renounced"
            ])
        writer.writerow(new_trade)