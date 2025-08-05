import pandas as pd
import streamlit as st

@st.cache_data(ttl=300)
def load_trade_logs(file_path="logs/trades.csv") -> pd.DataFrame:
    try:
        df_raw = pd.read_csv(file_path, on_bad_lines="skip", engine="python")
        df_cleaned = df_raw[df_raw["name"] != "name"]

        required = {"Timestamp", "name", "chain", "ROI", "estimated_payout", "estimated_value", "estimated_pl"}
        missing = required - set(df_cleaned.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        df_cleaned["ROI"] = pd.to_numeric(df_cleaned["ROI"], errors="coerce")
        df_cleaned["estimated_payout"] = pd.to_numeric(df_cleaned["estimated_payout"], errors="coerce")
        df_cleaned["estimated_value"] = pd.to_numeric(df_cleaned["estimated_value"], errors="coerce")
        df_cleaned["estimated_pl"] = pd.to_numeric(df_cleaned["estimated_pl"], errors="coerce")

        df_cleaned["Timestamp"] = pd.to_datetime(df_cleaned["Timestamp"], errors="coerce")
        df_cleaned["Date"] = df_cleaned["Timestamp"].dt.date

        return df_cleaned.dropna(subset=["Timestamp"])

    except Exception as e:
        st.warning(f"⚠️ Trade log load failed: {e}")
        return pd.DataFrame(columns=[
            "Timestamp", "name", "chain", "ROI", "estimated_payout", "estimated_value", "estimated_pl", "Date"
        ])

@st.cache_data(ttl=300)
def load_historical_tokens(path="logs/historical_tokens.csv") -> pd.DataFrame:
    try:
        df_raw = pd.read_csv(path, on_bad_lines="skip", engine="python")
        df_cleaned = df_raw[df_raw["name"] != "name"]

        required = {"name", "chain", "buzz_score", "risk_score", "estimated_return", "token_price_usd"}
        missing = required - set(df_cleaned.columns)
        if missing:
            raise ValueError(f"Missing columns: {missing}")

        numeric_fields = ["buzz_score", "risk_score", "estimated_return", "token_price_usd"]
        for col in numeric_fields:
            df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors="coerce")

        df_cleaned = df_cleaned.dropna(subset=["name", "chain", "estimated_return"])
        df_cleaned = df_cleaned.drop_duplicates()

        return df_cleaned

    except Exception as e:
        st.warning(f"⚠️ Token log load failed: {e}")
        return pd.DataFrame(columns=[
            "name", "chain", "buzz_score", "risk_score", "estimated_return", "token_price_usd"
        ])
