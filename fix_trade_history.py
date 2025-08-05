import pandas as pd

file_path = "data/trade_history.csv"

# Load and patch
df = pd.read_csv(file_path)

# Rename 'estimated_pl' → 'Estimated_Payout'
if "estimated_pl" in df.columns:
    df.rename(columns={"estimated_pl": "Estimated_Payout"}, inplace=True)

# Save it back
df.to_csv(file_path, index=False)
print("✅ trade_history.csv patched successfully.")
