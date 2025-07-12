import argparse
import subprocess
import threading
import time
import logging
import sys
from utils.router_factory import get_router_for_chain

config = get_router_for_chain("bnb")  # or "ethereum"
web3 = config["web3"]
router = config["router"]
weth_address = config["weth"]
sys.stdout.reconfigure(encoding='utf-8')
from auto_trade import run_trading_bot

from utils.logger_config import setup_logger
setup_logger()

from utils.balance_checker import wallet_check
from utils.solana_balance import get_sol_balance

# ✅ Dashboard thread
def start_dashboard():
    print("🖥️ Launching dashboard...")
    subprocess.run(["streamlit", "run", "dashboard/app.py"])

# 🔁 Scheduler process
def start_scheduler():
    print("⏱️ Launching scheduler...")
    subprocess.run(["python", "scheduler/job_runner.py"])

def main():
    parser = argparse.ArgumentParser(description="Sniper Bot Launcher")
    parser.add_argument("--live", action="store_true", help="Enable live trading")
    parser.add_argument("--test", action="store_true", help="Run in simulation (dry-run) mode")
    parser.add_argument("--dashboard", action="store_true", help="Start the dashboard UI")
    parser.add_argument("--scheduler", action="store_true", help="Start the scanning scheduler")
    parser.add_argument("--wallet-check", action="store_true", help="Print wallet balances")

    args = parser.parse_args()

    # ⚙️ Mode selection
    if args.live:
        print("🚨 Launching in LIVE trading mode")
        simulate = False
    else:
        print("🧪 Launching in TEST (simulation) mode")
        simulate = True

    # 🧠 Wallet check
    if args.wallet_check:
        wallet_check()
        sol_balance = get_sol_balance()
        print(f"Solana: {sol_balance:.4f} SOL")

    # 📈 Dashboard
    if args.dashboard:
        dashboard_thread = threading.Thread(target=start_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        time.sleep(5)

    # 🔁 Scheduler
    if args.scheduler:
        start_scheduler()

    # 🚀 Launch trade bot
    run_trading_bot(simulate)

if __name__ == "__main__":
    main()