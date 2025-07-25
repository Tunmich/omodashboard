# utils/preflight_checker.py

import sys
import os
import importlib
from dotenv import load_dotenv

# 🧠 Set up relative import path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# ✅ Load environment variables
load_dotenv()

# ✅ Try importing wallet conversion tool
try:
    from utils.wallet_mapper import phantom_to_evm
    print("✅ phantom_to_evm imported successfully")
except Exception as e:
    phantom_to_evm = None
    print(f"⚠️ Failed to import phantom_to_evm: {e}")

def scan_imports():
    """
    Scans and verifies all critical modules for import errors.
    """
    print("\n🚦 OMO Preflight Import Check\n")
    errors = []

    modules_to_check = [
        "main",
        "intel_engine",
        "intel_patrol",
        "intel_listener",
        "modules.solana_executor",
        "modules.sniper_engine",
        "scanner.twitter_tracker",
        "scheduler.job_runner",
        "strategy.trade_decision_engine",
        "utils.wallet_mapper",
        "utils.telegram_alert",
        "alerts.telegram_bot",
    ]

    for mod in modules_to_check:
        try:
            importlib.import_module(mod)
            print(f"✅ {mod}")
        except Exception as e:
            print(f"❌ {mod} failed")
            print(f"   🔥 {e.__class__.__name__}: {e}")
            errors.append(mod)

    if errors:
        print("\n🚨 Import Failures:")
        for mod in errors:
            print(f" - {mod}")
        print("\n🧪 Suggest running: grep 'phantom_to_evm' -r ./ to track unimported usage.")
    else:
        print("\n✅ All imports verified. Engine is green.")

if __name__ == "__main__":
    # 🔐 Inject EVM wallet if available
    sol_address = os.getenv("SOLANA_WALLET")

    if not sol_address:
        print("⚠️ SOLANA_WALLET not found in .env")
    elif not phantom_to_evm:
        print("⚠️ phantom_to_evm is not available — check wallet_mapper.py")
    else:
        try:
            evm_wallet = phantom_to_evm(sol_address)
            print(f"🔐 EVM wallet injected from Phantom: {evm_wallet}")
        except Exception as e:
            print(f"⚠️ Failed to convert SOL to EVM: {e}")

    scan_imports()
