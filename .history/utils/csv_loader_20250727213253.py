import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_trade_logs(file_path="logs/trades.csv") -> pd.DataFrame:
    try:
        # Load CSV with safeguards
        df_raw = pd.read_csv(file_path, on_bad_lines='skip', engine="python")

        # Drop repeated headers inside the file (row where column names repeat)
        df_cleaned = df_raw[df_raw["name"] != "name"]

        # Ensure required columns are present
        required = {"Timestamp", "name", "chain", "ROI", "estimated_payout", "estimated_value", "estimated_pl"}
        missing = required - set(df_cleaned.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        # Convert key metrics to numeric
        df_cleaned["ROI"] = pd.to_numeric(df_cleaned["ROI"], errors="coerce")
        df_cleaned["estimated_payout"] = pd.to_numeric(df_cleaned["estimated_payout"], errors="coerce")
        df_cleaned["estimated_value"] = pd.to_numeric(df_cleaned["estimated_value"], errors="coerce")
        df_cleaned["estimated_pl"] = pd.to_numeric(df_cleaned["estimated_pl"], errors="coerce")

        # Timestamp parsing
        df_cleaned["Timestamp"] = pd.to_datetime(df_cleaned["Timestamp"], errors="coerce")
        df_cleaned["Date"] = df_cleaned["Timestamp"].dt.date

        return df_cleaned.dropna(subset=["Timestamp"])

    except Exception as e:
        st.warning(f"⚠️ Trade log load failed: {e}")
        return pd.DataFrame(columns=["Timestamp", "name", "chain", "ROI", "estimated_payout", "estimated_value", "estimated_pl", "Date"])
