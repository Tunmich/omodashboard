# launcher.py

import argparse
import subprocess
import threading
import time
import logging

from utils.logger_config import setup_logger
setup_logger()

from utils.balance_checker import wallet_check
from utils.solana_balance import get_sol_balance

def start_dashboard():
    print("🖥️ Launching dashboard...")
    subprocess.run(["streamlit", "run", "dashboard/app.py"])

def start_scheduler():
    print("⏱️ Launching scanner scheduler...")
    subprocess.run(["python", "scheduler/job_runner.py"])

def start_sniper(mode="test"):
    flag = "--live" if mode == "live" else "--test"
    print(f"🚀 Launching Sniper Bot in {mode.upper()} mode...")
    subprocess.run(["python", "start_sniper_bot.py", flag])

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Unified MemeBot Launcher")
    parser.add_argument(
        "--mode",
        choices=["dashboard", "scan", "trade", "wallet"],
        help="Select operation mode"
    )

    args = parser.parse_args()

    if args.mode == "wallet":
        print("🔍 Checking wallet balances...")
        wallet_check()
        sol_balance = get_sol_balance()
        print(f"Solana: {sol_balance:.4f} SOL")

    elif args.mode == "dashboard":
        dashboard_thread = threading.Thread(target=start_dashboard)
        dashboard_thread.daemon = True
        dashboard_thread.start()
        time.sleep(5)

    elif args.mode == "scan":
        start_scheduler()

    elif args.mode == "trade":
        start_sniper("live")  # Change to "live" if ready for real trading