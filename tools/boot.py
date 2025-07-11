# tools/boot.py
import subprocess
import sys
import logging

print("🚀 Booting MemeBot Sniper...")

# Step 1: Validate Wallet
print("🔎 Validating wallet configuration...\n")
validation = subprocess.run([sys.executable, "tools/validate_wallet.py"])

# If validation fails, you can choose to halt here
if validation.returncode != 0:
    print("❌ Wallet validation failed. Aborting launch.")
    sys.exit(1)

# Step 2: Start Trading Engine
print("\n✅ Wallet validated. Launching trading engine...\n")
subprocess.run([sys.executable, "main.py"])