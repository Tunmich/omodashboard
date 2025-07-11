import pandas as pd
import logging

TIERS = {
    "Tier 1": {"max_trade": 1.0, "unlock_threshold": 0},
    "Tier 2": {"max_trade": 2.0, "unlock_threshold": 5},
    "Tier 3": {"max_trade": 5.0, "unlock_threshold": 10},
    "Tier 4": {"max_trade": 10.0, "unlock_threshold": 25}
}

def get_current_tier():
    try:
        df = pd.read_csv("logs/trades.csv")
        confirmed_trades = df[df["Status"] == "Confirmed"]
        count = len(confirmed_trades)

        for tier, data in reversed(TIERS.items()):
            if count >= data["unlock_threshold"]:
                return tier, data["max_trade"]
        return "Tier 1", TIERS["Tier 1"]["max_trade"]
    except:
        return "Tier 1", TIERS["Tier 1"]["max_trade"]