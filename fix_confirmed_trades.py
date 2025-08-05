import pandas as pd

file_path = "data/confirmed_trades.csv"

# Load and patch
df = pd.read_csv(file_path)

# Rename 'Token' → 'token'
if "Token" in df.columns:
    df.rename(columns={"Token": "token"}, inplace=True)

# Add dummy win_rate if missing
if "win_rate" not in df.columns:
    df["win_rate"] = [100] * len(df)  # You can adjust this logic if needed

# Save it back
df.to_csv(file_path, index=False)
print("✅ confirmed_trades.csv patched successfully.")
