
from utils.thread_launcher import THREAD_STATUS

def print_thread_report():
    print("🧵 Thread Launch Status\n")

    for name, data in THREAD_STATUS.items():
        uptime = int(data.get("uptime", 0))
        retries = data.get("retries", 0)
        active = "✅" if data.get("active") else "❌"
        crash = data.get("last_error", "")
        line = f"{active} {name} | {uptime}s up, {retries} retries"
        if not data.get("active") and crash:
            line += f"\n   🔥 Crash reason: {crash}"
        print(line)

    print("\n📊 Threads scanned. Dashboard complete.")
