import os
import time
import sys
import signal
import argparse
import threading
import logging
import asyncio
from dotenv import load_dotenv
from solders.keypair import Keypair
from scheduler.job_runner import run_scheduler
from scanner.twitter_tracker import track_keywords as scan_twitter_buzz
from strategy.trade_decision_engine import should_buy
from modules.solana_executor import execute_sol_trade
from intel_patrol import start_telegram_listener
from utils.alloc import get_trade_allocation
from health_check import run_health_check
from utils.wallet_mapper import get_safe_evm_wallet
from utils.telegram_alert import send_failure_alert
from listeners.signal_streamer import start_signal_streamer

# Setup logger
logging.basicConfig(
    filename="logs/intel_engine.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Ensure new asyncio loop
asyncio.set_event_loop(asyncio.new_event_loop())

# Load environment variables
load_dotenv()
wallet = Keypair.from_base58_string(os.getenv("WALLET_PRIVATE_KEY"))
sol_amount = float(os.getenv("USD_PER_TRADE", "0.05"))
INTEL_ENABLED = os.getenv("INTEL_TELEGRAM_ENABLED", "False") == "True"

# Track running threads and status
THREAD_STATUS = {}
ACTIVE_THREADS = []

# PID file for tracking
PID_FILE = "bot.pid"

# -------------------- Thread Logic --------------------

class ThreadMaster:
    def __init__(self, thread_config):
        self.thread_config = thread_config

    def launch_all(self):
        for name, func in self.thread_config.items():
            self._start_thread(name, func)

    def _start_thread(self, name, target_func):
        def wrapped():
            retries = 0
            start_time = time.time()
            while True:
                try:
                    THREAD_STATUS[name] = {
                        "retries": retries,
                        "uptime": time.time() - start_time,
                        "active": True
                    }
                    logging.info(f"🧵 Thread started: {name}")
                    print(f">>> Thread started: {name}")
                    target_func()
                except Exception as e:
                    retries += 1
                    THREAD_STATUS[name] = {
                        "retries": retries,
                        "uptime": time.time() - start_time,
                        "active": False,
                        "last_error": str(e)
                    }
                    logging.error(f"🔥 {name} crashed: {e}")
                    try:
                        send_failure_alert([f"Thread crashed → {name}: {e}"])
                    except:
                        pass
                    time.sleep(10)

        t = threading.Thread(target=wrapped, name=name)
        t.start()
        ACTIVE_THREADS.append(t)

# -------------------- Thread Targets --------------------

def twitter_intel_loop():
    print(">>> Starting Twitter intel loop...")
    while True:
        try:
            candidates = scan_twitter_buzz(limit=30)
            for token in candidates:
                logging.info(f"Twitter: scanned → {token['address']}")
                if should_buy(token):
                    logging.info(f"✅ Twitter: approved → {token['address']}")
                else:
                    logging.info(f"❌ Twitter: rejected → {token['address']}")
            time.sleep(60)
        except Exception as e:
            logging.error(f"Twitter loop error: {e}")
            time.sleep(10)

def heartbeat_loop():
    print(">>> Starting heartbeat loop...")
    while True:
        try:
            logging.info("💓 OMO heartbeat — engine running")
            time.sleep(300)
        except Exception as e:
            logging.error(f"Heartbeat error: {e}")
            time.sleep(10)

def launch_signal_thread():
    def wrapped():
        try:
            start_signal_streamer()
        except Exception as e:
            logging.error(f"Signal streamer error: {e}")
            time.sleep(10)
    t = threading.Thread(target=wrapped, name="SignalStreamer")
    t.start()
    ACTIVE_THREADS.append(t)

# -------------------- Thread Config --------------------

THREAD_CONFIG = {
    "TwitterIntel": twitter_intel_loop,
    "SniperScheduler": run_scheduler,
    "HealthMonitor": run_health_check,
    "HeartbeatMonitor": heartbeat_loop,
    "TelegramListener": start_telegram_listener,
    "SignalStreamer": launch_signal_thread
}

# -------------------- Engine Logic --------------------

def start_intel_engine():
    if INTEL_ENABLED:
        print("🧠 Launching Intel Engine...")
        manager = ThreadMaster(THREAD_CONFIG)
        manager.launch_all()
    else:
        print("⏸ Intel engine disabled via .env")

def shutdown_handler(signum=None, frame=None):
    print("\n🛑 Shutdown signal received. Cleaning up...\n")
    logging.info("Shutdown signal received. Exiting all threads...")

    print("📊 Final thread status report:")
    for name, status in THREAD_STATUS.items():
        print(f"• {name}: {'🟢' if status.get('active') else '🔴'} | "
              f"retries={status.get('retries', 0)}, "
              f"uptime={round(status.get('uptime', 0), 1)}s, "
              f"last_error={status.get('last_error', '—')}")

    try:
        send_failure_alert(["🛑 Bot stopped manually via CTRL+C or system signal"])
    except Exception as e:
        print(f"⚠️ Telegram alert failed: {e}")

    remove_pid()
    print("✅ Shutdown complete. Goodbye.")
    sys.exit(0)

# -------------------- PID Utilities --------------------

def write_pid():
    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))

def read_pid():
    if os.path.exists(PID_FILE):
        with open(PID_FILE, "r") as f:
            return int(f.read().strip())
    return None

def remove_pid():
    if os.path.exists(PID_FILE):
        os.remove(PID_FILE)

# -------------------- CLI Functions --------------------

def show_status():
    print("📊 Intel Engine Thread Status:\n")
    if not THREAD_STATUS:
        print("⚠️  Engine not running or no threads started.")
    for name, status in THREAD_STATUS.items():
        print(f"• {name}: {'🟢' if status.get('active') else '🔴'} | "
              f"retries={status.get('retries', 0)}, "
              f"uptime={round(status.get('uptime', 0), 1)}s, "
              f"last_error={status.get('last_error', '—')}")

def cli_entry():
    parser = argparse.ArgumentParser(description="Intel Engine CLI")
    parser.add_argument("command", choices=["start", "stop", "status"], help="Command to run")
    args = parser.parse_args()

    if args.command == "start":
        signal.signal(signal.SIGINT, shutdown_handler)
        signal.signal(signal.SIGTERM, shutdown_handler)

        write_pid()
        start_intel_engine()

        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            shutdown_handler()

    elif args.command == "status":
        show_status()

    elif args.command == "stop":
        pid = read_pid()
        if pid:
            print(f"🛑 Sending termination to PID {pid}...")
            try:
                os.kill(pid, signal.SIGTERM)
                print("✅ Stop signal sent.")
            except Exception as e:
                print(f"❌ Failed to stop process: {e}")
        else:
            print("⚠️ No running process found.")

# -------------------- Run CLI if main --------------------
# 🔗 External module aliases (for backward compatibility)
PatrolManager = start_telegram_listener
HeartbeatMonitor = heartbeat_loop

# -------------------- Run CLI if main --------------------
if __name__ == "__main__":
    cli_entry()

