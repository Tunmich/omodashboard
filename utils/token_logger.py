import csv
import os
import logging

def log_token_snapshot(token, filename="logs/historical_tokens.csv"):
    fields = ["name", "chain", "buzz_score", "risk_score", "estimated_return", "token_price_usd"]
    token_data = {
        "name": token.get("name"),
        "chain": token.get("chain"),
        "buzz_score": token.get("buzz_score", 0),
        "risk_score": token.get("risk_score", 0),
        "estimated_return": token.get("estimated_return", 0),
        "token_price_usd": token.get("token_price_usd", 0)
    }

    # Create file with header if it doesn’t exist
    write_header = not os.path.exists(filename)

    with open(filename, mode="a", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(token_data)