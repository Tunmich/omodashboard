import importlib
import logging
import csv
import time
import os
import sys
import psutil
from datetime import datetime
from utils.telegram_alert import send_heartbeat, send_failure_alert
from utils.thread_launcher import THREAD_STATUS

# Logging setup
logging.basicConfig(filename="logs/health_monitor.log", level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")

LOG_FILE = "logs/health_checks.csv"
FIELDNAMES = ["Timestamp", "First_Attempt", "Retry_Attempt", "Status"]

MODULES = {
    "strategy.trade_decision_engine": "should_buy",
    "utils.sol_price_feed": "fetch_sol_usd_price",
    "utils.telegram_alert": "send_trade_alert",
    "modules.solana_executor": "buy_token_solana",
    "modules.sniper_engine": "scan_and_snipe",
    "scanner.twitter_tracker": "track_keywords",
    "intel_listener": "TelegramListener",
    "intel_patrol": "PatrolManager",
    "intel_engine": "HeartbeatMonitor"
}

def test_module(name, attr):
    try:
        mod = importlib.import_module(name)
        if hasattr(mod, attr):
            logging.info(f"✅ {name}.{attr} exists")
            return {"status": "ok", "module": f"{name}.{attr}", "message": "Found"}
        else:
            logging.error(f"❌ {name}.{attr} missing")
            return {"status": "fail", "module": f"{name}.{attr}", "reason": "Attribute not found"}
    except Exception as e:
        logging.error(f"❌ Import failed for {name}: {e}")
        return {"status": "fail", "module": f"{name}.{attr}", "reason": str(e)}

def run_health_check():
    print("🔧 OMO /ping report\n")
    results = []
    for name, attr in MODULES.items():
        result = test_module(name, attr)
        symbol = "✅" if result["status"] == "ok" else "❌"
        msg = result.get("message", result.get("reason"))
        print(f"{symbol} {result['module']} | {msg}")
        results.append(result)
    return [r for r in results if r["status"] == "fail"]

def monitor_threads():
    for thread, status in THREAD_STATUS.items():
        if not status or not status.get("active"):
            error = status.get("last_error", "unknown")
            print(f"❌ Thread {thread} inactive | Error: {error}")
            send_failure_alert([f"Thread down: {thread}"])
        else:
            print(f"✅ {thread}: uptime {status.get('uptime', 0)}s, retries {status.get('retries', 0)}")

def log_csv(first, retry):
    row = {
        "Timestamp": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"),
        "First_Attempt": "OK" if first else "Fail",
        "Retry_Attempt": "OK" if retry else "Fail",
        "Status": "Pass" if first else "Retry Success" if retry else "Fail"
    }
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    write_header = not os.path.exists(LOG_FILE)
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

def log_system_resources():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    logging.info(f"🧠 CPU: {cpu}%, Memory: {mem}%")

def health_monitor_loop():
    while True:
        failed = run_health_check()
        monitor_threads()
        log_system_resources()

        if not failed:
            send_heartbeat()
            log_csv(True, None)
        else:
            send_failure_alert([f["module"] for f in failed])
            time.sleep(1800)
            retry = run_health_check()
            monitor_threads()
            if not retry:
                send_heartbeat()
            log_csv(False, not retry)
        time.sleep(1800)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--ping":
        failed = run_health_check()
        monitor_threads()
        log_system_resources()
        print("\n🔍 Ping complete.")
        if failed:
            print(f"\n⚠️ {len(failed)} modules failed.")
        else:
            print("✅ All modules passed.")
    else:
        health_monitor_loop()
