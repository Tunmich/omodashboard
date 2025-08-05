import os
import datetime
import shutil
import zipfile

# ❌ Purge targets
PURGE_TARGETS = [
    "abis", "alerts", "config", "dashboard", "data", "jobs", "predictor",
    "scanner", "scheduler", "strategy", "tools", "trading", "triggers", "utils",
    "__pycache__", "auto_trade.py", "main.py", "trade_test.py", "health_check.py",
    "healthy_rpcs.json", "Dockerfile", "terminal_log.txt", "meme bot file list.txt",
    "Memebot usage instructions.txt", "Memebot usage instructions 2.txt",
    "pl_simulated_results.json", "pyproject.toml", "run.sh", "set_up.py",
    "launch_env.sh", "simulated_tokens.json", "convert_keypair.py"
]

LOG_FILE = "purge_log.txt"
BACKUP_FOLDER = "backups"

def confirm(prompt):
    response = input(f"{prompt} [y/N]: ").strip().lower()
    return response == 'y'

def add_to_zip(zipf, target):
    if os.path.isdir(target):
        for root, dirs, files in os.walk(target):
            for file in files:
                full_path = os.path.join(root, file)
                arcname = os.path.relpath(full_path, start=os.getcwd())
                zipf.write(full_path, arcname)
    elif os.path.isfile(target):
        zipf.write(target)

def delete_target(target):
    try:
        if os.path.isdir(target):
            shutil.rmtree(target)
        elif os.path.isfile(target):
            os.remove(target)
        else:
            return False
        return True
    except Exception as e:
        return f"Error: {e}"

def main():
    print("🧼 OMO Cleanup Utility with Backup Enabled")
    print("🔍 Scanning for purge candidates...\n")

    os.makedirs(BACKUP_FOLDER, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_zip_path = os.path.join(BACKUP_FOLDER, f"purged_backup_{timestamp}.zip")
    deleted = []

    with zipfile.ZipFile(backup_zip_path, 'w') as zipf:
        for item in PURGE_TARGETS:
            if os.path.exists(item):
                if confirm(f"❌ Backup and delete '{item}'?"):
                    try:
                        add_to_zip(zipf, item)
                        result = delete_target(item)
                        if result == True:
                            print(f"✅ Backed up and deleted '{item}'")
                            deleted.append(item)
                        else:
                            print(f"⚠️ Failed to delete '{item}': {result}")
                    except Exception as e:
                        print(f"🚫 Error backing up '{item}': {e}")
                else:
                    print(f"🛑 Skipped '{item}' by user choice")
            else:
                print(f"➖ Not found: '{item}'")

    if deleted:
        with open(LOG_FILE, "a") as log:
            log.write(f"\n--- Purge at {timestamp} ---\n")
            for d in deleted:
                log.write(f"Deleted: {d}\n")
            log.write(f"🔐 Backup archive: {backup_zip_path}\n")

        print(f"\n🗃️ Purge complete. Items backed up in ZIP: {backup_zip_path}")
        print(f"📄 Actions logged in: {LOG_FILE}")
    else:
        print("\n📦 No files were removed or backed up.")

if __name__ == "__main__":
    main()
