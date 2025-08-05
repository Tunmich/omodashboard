# tools/generate_csv_from_env.py

import os
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

# Load tokens and chains from .env or use fallbacks
tokens = os.getenv("TOKEN_ADDRESSES", "PEPE,SNEK,DEGEN").split(",")
chains = os.getenv("CHAINS", "SOL,BASE").split(",")

# Trade History CSV (used for 'Estimated_Payout')
trade_history_rows = []
confirmed_rows = []

for i, token in enumerate(tokens):
    for chain in chains:
        trade_history_rows.append({
            "Token": token.strip(),
            "Estimated_Payout": 100 + i * 25,
            "Buy_Tx_Hash": f"0xhash{i}{chain.lower()}",
            "Chain": chain.strip(),
            "Timestamp": pd.Timestamp.now()
        })

        confirmed_rows.append({
            "token": token.strip(),
            "estimated_return": 80 + i * 10,
            "win_rate": 50 + i * 5,
            "Chain": chain.strip(),
            "Timestamp": pd.Timestamp.now()
        })

# Create folders
os.makedirs("data", exist_ok=True)
os.makedirs("logs", exist_ok=True)

# Write the files
pd.DataFrame(trade_history_rows).to_csv("data/trade_history.csv", index=False)
pd.DataFrame(confirmed_rows).to_csv("data/confirmed_trades.csv", index=False)
pd.DataFrame(trade_history_rows).to_csv("logs/trades.csv", index=False)

print("✅ Fixed CSVs with correct column names generated.")
