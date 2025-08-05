import os
import zipfile
import datetime

BACKUP_DIR = "backups"

def get_latest_backup():
    files = [f for f in os.listdir(BACKUP_DIR) if f.startswith("purged_backup_") and f.endswith(".zip")]
    if not files:
        print("❌ No backup ZIP found.")
        return None
    files.sort(reverse=True)
    return os.path.join(BACKUP_DIR, files[0])

def restore_backup(zip_path):
    try:
        with zipfile.ZipFile(zip_path, 'r') as zipf:
            zipf.extractall(os.getcwd())
        print(f"✅ Restored backup: {zip_path}")
        return True
    except Exception as e:
        print(f"❌ Error during restore: {e}")
        return False

def main():
    print("🔄 OMO Restore Utility")
    zip_path = get_latest_backup()
    if not zip_path:
        return

    confirm = input(f"⚠️ Restore contents of {os.path.basename(zip_path)} to current project folder? [y/N]: ").strip().lower()
    if confirm == "y":
        success = restore_backup(zip_path)
        if success:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open("restore_log.txt", "a") as log:
                log.write(f"✔ Restored from {zip_path} at {timestamp}\n")
            print("📄 Restore logged in restore_log.txt")
        else:
            print("🚫 Restore failed.")
    else:
        print("🛑 Restore cancelled.")

if __name__ == "__main__":
    main()
