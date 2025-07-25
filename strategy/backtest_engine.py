import pandas as pd
import logging

from strategy.trade_decision_engine import should_buy

def run_backtest(log_file="logs/historical_tokens.csv"):
    try:
        df = pd.read_csv(log_file)
        df["Backtest_Result"] = df.apply(lambda row: should_buy(dict(row)), axis=1)
        total = len(df)
        passed = df["Backtest_Result"].sum()
        win_rate = (passed / total) * 100
        print(f"📈 Backtest Complete: {passed}/{total} tokens passed decision logic")
        print(f"✅ Decision Win Rate: {win_rate:.2f}%")
        return df
    except Exception as e:
        print(f"💥 Backtest failed: {str(e)}")
        return None