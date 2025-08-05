import os
import shutil
import zipfile
import datetime

PURGE_CANDIDATES = [
    "abis", "alerts", "config", "dashboard", "data", "jobs", "predictor",
    "scanner", "scheduler", "strategy", "tools", "trading", "triggers", "utils",
    "__pycache__", "auto_trade.py", "main.py", "trade_test.py", "health_check.py",
    "healthy_rpcs.json", "Dockerfile", "terminal_log.txt", "meme bot file list.txt",
    "Memebot usage instructions.txt", "Memebot usage instructions 2.txt",
    "pl_simulated_results.json", "pyproject.toml", "run.sh", "set_up.py",
    "launch_env.sh", "simulated_tokens.json", "convert_keypair.py"
]

BACKUP_DIR = "backups"
LOG_FILE = "purge_log.txt"

def list_files():
    print("\n📂 Purge Candidates:\n")
    for i, item in enumerate(PURGE_CANDIDATES):
        status = "🗑️" if os.path.exists(item) else "❌ Not Found"
        print(f" {i+1:02d}. {item:<30} {status}")
    print()

def backup_items():
    os.makedirs(BACKUP_DIR, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_name = f"purged_backup_{timestamp}.zip"
    zip_path = os.path.join(BACKUP_DIR, zip_name)

    print(f"\n🔐 Creating backup archive: {zip_name}...")
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        for item in PURGE_CANDIDATES:
            if os.path.exists(item):
                if os.path.isdir(item):
                    for root, _, files in os.walk(item):
                        for file in files:
                            full = os.path.join(root, file)
                            arc = os.path.relpath(full, start=os.getcwd())
                            zipf.write(full, arc)
                else:
                    zipf.write(item)

    print(f"✅ Backup complete: {zip_path}\n")
    return zip_path

def purge_items():
    deleted = []
    for item in PURGE_CANDIDATES:
        if os.path.exists(item):
            try:
                if os.path.isdir(item):
                    shutil.rmtree(item)
                else:
                    os.remove(item)
                deleted.append(item)
                print(f"🗑️ Removed: {item}")
            except Exception as e:
                print(f"❌ Error deleting {item}: {e}")
        else:
            print(f"➖ Skipped {item} (not found)")
    return deleted

def log_purge(deleted, backup_path):
    time_now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a") as log:
        log.write(f"\n--- Purge at {time_now} ---\n")
        for item in deleted:
            log.write(f"Deleted: {item}\n")
        log.write(f"Backup: {backup_path}\n")

def cli():
    print("🧼 OMO Purge CLI Interface")
    while True:
        print("""
🧭 Select an option:
  [1] View purge candidates
  [2] Run purge with backup
  [3] Exit
        """)
        choice = input("Enter your choice: ").strip()

        if choice == "1":
            list_files()
        elif choice == "2":
            confirm = input("⚠️ Are you sure you want to backup and purge? [y/N]: ").lower()
            if confirm == "y":
                backup_path = backup_items()
                deleted = purge_items()
                log_purge(deleted, backup_path)
                print(f"\n🧾 Log saved to {LOG_FILE}")
            else:
                print("❌ Purge cancelled.")
        elif choice == "3":
            print("👋 Exiting purge CLI.")
            break
        else:
            print("❓ Invalid option. Try again.")

if __name__ == "__main__":
    cli()
