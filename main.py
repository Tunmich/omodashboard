import os
import sys
import time
import threading
from datetime import datetime
from dotenv import load_dotenv

# 🔧 Make sibling modules discoverable
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

# 🧬 Load environment
load_dotenv()

# ✅ Mode setup
MODE = os.getenv("OMO_CHAIN_MODE", "multi").lower()
INTEL_TELEGRAM_ENABLED = os.getenv("INTEL_TELEGRAM_ENABLED", "False") == "True"

# 🧠 Required imports (delayed to allow safe import when needed)
from intel_engine import start_intel_engine
from alerts.telegram_bot import send_startup_ping
from utils.wallet_mapper import get_safe_evm_wallet
from health_check import health_monitor_loop

# ✅ Thread tracking pool
thread_pool = []

def inject_evm_wallet():
    if not os.getenv("EVM_WALLET_ADDRESS"):
        try:
            sol_address = os.getenv("WALLET_ADDRESS")
            evm_address = get_safe_evm_wallet(sol_address)
            os.environ["EVM_WALLET_ADDRESS"] = evm_address
            print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
        except Exception as e:
            print(f"⚠️ Failed to inject EVM wallet: {e}")

def launch_chain_bot():
    if MODE == "solana":
        from start_sniper_bot import launch_sol_bot
        print("🚀 Launching Solana Sniper Engine via Jupiter...")
        send_startup_ping("solana")
        t = threading.Thread(target=launch_sol_bot, name="SolBot")
    else:
        from scheduler.job_runner import run_scheduler
        print("🚀 Launching Multi-Chain Scanner Engine...")
        send_startup_ping("multi")
        t = threading.Thread(target=run_scheduler, name="ScannerBot")
    
    t.start()
    thread_pool.append(t)

def start_main():
    print("🧠 OMO Engine Booting...\n")

    inject_evm_wallet()
    start_intel_engine()

    # Launch health monitor
    health_thread = threading.Thread(target=health_monitor_loop, name="HeartbeatMonitor")
    health_thread.start()
    thread_pool.append(health_thread)

    launch_chain_bot()

    # Optional: block main thread to prevent shutdown
    try:
        while True:
            time.sleep(5)
    except KeyboardInterrupt:
        print("🛑 OMO Engine interrupted. Exiting cleanly...")

# 🔒 Only run engine if this is a direct script call
if __name__ == "__main__":
    start_main()
