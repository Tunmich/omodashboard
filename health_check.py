import importlib
import logging
from utils.telegram_alert import send_heartbeat

logging.basicConfig(level=logging.INFO)
import csv
from datetime import datetime

LOG_FILE = "logs/health_checks.csv"
FIELDNAMES = ["Timestamp", "First_Attempt", "Retry_Attempt", "Status"]

def log_health_status(first_result, retry_result):
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    final_status = (
        "Pass" if first_result
        else "Retry Success" if retry_result
        else "Fail"
    )

    entry = {
        "Timestamp": timestamp,
        "First_Attempt": "OK" if first_result else "Fail",
        "Retry_Attempt": "OK" if retry_result else "Fail",
        "Status": final_status
    }

    # Ensure log file exists with headers
    log_dir = os.path.dirname(LOG_FILE)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(entry)

# ✅ Modules to verify
MODULES = {
    "strategy.decision_engine": "should_buy",
    "utils.sol_price_feed": "fetch_sol_usd_price",
    "utils.telegram_alert": "send_trade_alert",
    "modules.solana_executor": "buy_token_solana",
    "modules.sniper_engine": "scan_and_snipe"
}

def test_module(module_path, test_func=None):
    try:
        mod = importlib.import_module(module_path)
        if test_func:
            func = getattr(mod, test_func, None)
            assert callable(func)
        logging.info(f"✅ {module_path} passed")
        return True
    except Exception as e:
        logging.error(f"🔥 {module_path} failed: {e}")
        return False

def run_health_check():
    print("🔎 Running OMO pre-flight diagnostics...\n")
    all_good = True

    for module, func in MODULES.items():
        if not test_module(module, func):
            all_good = False

    if all_good:
        print("\n✅ All systems passed. Sending heartbeat ping...")
        send_heartbeat()
    else:
        print("\n⚠️ One or more modules failed. Bot will NOT launch.")
import time

if __name__ == "__main__":
   if __name__ == "__main__":
    first_pass = run_health_check()

    if first_pass:
        send_heartbeat()
        log_health_status(True, None)
    else:
        import time
        time.sleep(60)  # Short pause before retry
        print("\n🔁 Rechecking after 30 minutes...")
        time.sleep(1800)  # Wait 30 minutes
        second_pass = run_health_check()

        if second_pass:
            send_heartbeat()
        log_health_status(False, second_pass)

if __name__ == "__main__":
    run_health_check()