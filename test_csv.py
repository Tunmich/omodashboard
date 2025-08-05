import pandas as pd

try:
    df = pd.read_csv("logs/trades.csv")
    print(df.head())
except Exception as e:
    print(f"❌ Error: {e}")
