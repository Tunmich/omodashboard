import streamlit as st
import pandas as pd
import os

def render_roi_tables_and_charts():
    st.header("🏆 Trade ROI Leaderboard")

    # Load trade history or scoring output
    file_path = "data/trade_history.csv"

    if os.path.exists(file_path):
        try:
            df = pd.read_csv(file_path)

            if "Estimated_Payout" not in df.columns:
                st.warning("⚠️ 'Estimated_Payout' column not found.")
            else:
                df_sorted = df.sort_values(by="Estimated_Payout", ascending=False)
                st.subheader("📈 ROI Estimate Leaderboard")
                st.dataframe(df_sorted[["Token", "Estimated_Payout", "Buy_Tx_Hash"]], use_container_width=True)

        except Exception as e:
            st.error(f"⚠️ Could not load ROI leaderboard: {e}")
    else:
        st.info("ℹ️ No trade history found. Using sample fallback data.")

        # Fallback dummy leaderboard
        dummy_data = {
            "Token": ["MemeCoinX", "PepeNext", "SolJoke", "DegenDrop"],
            "Estimated_Payout": [182.4, 149.2, 97.5, 55.8],
            "Buy_Tx_Hash": ["0xabc...", "0xdef...", "0xghi...", "0xjkl..."]
        }

        df_dummy = pd.DataFrame(dummy_data)
        st.dataframe(df_dummy, use_container_width=True)
        st.bar_chart(df_dummy.set_index("Token")["Estimated_Payout"])

    # --- Confirmed Trades Leaderboard ---
    st.header("✅ Confirmed Trades ROI Leaderboard")
    confirmed_file = "data/confirmed_trades.csv"

    if os.path.exists(confirmed_file):
        try:
            confirmed_df = pd.read_csv(confirmed_file)

            if "estimated_return" not in confirmed_df.columns:
                st.warning("⚠️ 'estimated_return' column missing.")
            else:
                st.dataframe(confirmed_df[["token", "estimated_return", "win_rate"]], use_container_width=True)
                st.bar_chart(confirmed_df.set_index("token")["estimated_return"])
        except Exception as e:
            st.error(f"⚠️ Error loading charts: {e}")
    else:
        st.info("ℹ️ No confirmed trades file found.")

    # --- Optional: trades.csv charting block (safe load) ---
    st.header("📦 Raw Trade Logs Chart")
    trades_path = "logs/trades.csv"

    if os.path.exists(trades_path):
        try:
            if os.path.getsize(trades_path) == 0:
                st.warning("📦 No trade logs found yet. Start trading to populate data.")
            else:
                roi_df = pd.read_csv(trades_path)
                if roi_df.empty:
                    st.warning("⚠️ trades.csv is empty.")
                else:
                    st.subheader("📊 Trade ROI from logs/trades.csv")
                    st.dataframe(roi_df, use_container_width=True)
                    if "ROI" in roi_df.columns:
                        st.bar_chart(roi_df["ROI"])
        except Exception as e:
            st.warning(f"⚠️ Could not load or chart trades.csv: {e}")
    else:
        st.info("📁 logs/trades.csv not found.")
