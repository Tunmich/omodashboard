
import json
import random
import sys
import os
import logging

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from utils.pl_tracker import estimate_trade_pl

# 📂 Input & output file paths
INPUT_FILE = "simulated_tokens.json"
OUTPUT_FILE = "pl_simulated_results.json"

# 🔄 Load mock tokens
try:
    with open(INPUT_FILE, "r") as file:
        tokens = json.load(file)

    if not isinstance(tokens, list):
        raise ValueError("Input file must contain a list of token dictionaries.")

except Exception as e:
    print(f"❌ Failed to load {INPUT_FILE}: {e}")
    tokens = []

# 🧪 Inject simulation metrics & estimate P/L
enriched = []
for token in tokens:
    try:
        # Inject trade budget
        token["trade_amount_usd"] = 1.0

        # Use token’s price or fallback
        token["token_price_usd"] = token.get("token_price_usd", 0.0034)

        # Generate a pseudo-random swap output
        token["estimated_return"] = round(random.uniform(10, 500), 4)

        # Estimate profit/loss
        pl = estimate_trade_pl(token)
        token["estimated_pl"] = round(pl, 4)

        print(f"📊 {token.get('name', 'Unnamed')} | Output: {token['estimated_return']} | P/L: ${token['estimated_pl']}")
        enriched.append(token)

    except Exception as err:
        print(f"⚠️ Error processing token {token.get('name', 'Unknown')}: {err}")

# 💾 Save simulation results
try:
    with open(OUTPUT_FILE, "w") as outfile:
        json.dump(enriched, outfile, indent=2)
    print(f"✅ Results saved to {OUTPUT_FILE}")

except Exception as e:
    print(f"❌ Failed to save output: {e}")