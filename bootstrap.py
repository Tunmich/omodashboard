import os
import subprocess
import threading
import time
from dotenv import load_dotenv

# ✅ Load environment
load_dotenv()

# ✅ Track launched threads
thread_pool = []

def resolve_group_ids():
    print("\n🧠 Resolving Telegram Signal Channels with keywords...")
    try:
        subprocess.run(["python", "utils/id_resolver.py"])
    except Exception as e:
        print(f"❌ Failed to resolve IDs: {e}")

def run_preflight():
    print("\n🔍 Running Preflight Check...")
    subprocess.run(["python", "utils/preflight_checker.py"])

def launch_engine():
    print("\n🚀 Starting OMO Engine...")
    try:
        def engine_thread():
            subprocess.run(["python", "main.py"])

        t = threading.Thread(target=engine_thread)
        t.start()
        thread_pool.append(t)

        print("✅ OMO Engine thread started.\n")
    except Exception as e:
        print(f"❌ Failed to start engine: {e}")

def launch_signal_streamer():
    subprocess.run(["python", "listeners/signal_streamer.py"])

def show_env():
    print("\n📦 Environment Snapshot:")
    keys = ["OMO_CHAIN_MODE", "EVM_WALLET_ADDRESS", "TELEGRAM_TOKEN", "TELEGRAM_CHAT_ID"]
    for key in keys:
        print(f"- {key}: {os.getenv(key, '❌ Not Set')}")

def menu():
    while True:
        print("\n🧠 OMO Bootstrap Menu")
        print("0. Resolve Telegram Signal Channels by Keyword")
        print("1. Run Preflight Checker")
        print("2. Launch Engine (main.py)")
        print("3. Show .env Status")
        print("4. Launch Signal Streamer (CA Scanner)")
        print("5. Exit")

        choice = input("Select an option: ").strip()
        if choice == "0":
            resolve_group_ids()
        elif choice == "1":
            run_preflight()
        elif choice == "2":
            launch_engine()
        elif choice == "3":
            show_env()
        elif choice == "4":
            launch_signal_streamer()
        elif choice == "5":
            print("👋 Goodbye.")
            break
        else:
            print("❌ Invalid option. Try again.")


    # 🔒 Ensure launched threads finish before shutdown
    if thread_pool:
        print("\n🧵 Waiting for engine threads to complete...")
        try:
            for t in thread_pool:
                t.join()
        except KeyboardInterrupt:
            print("🛑 Interrupted. Threads may exit abruptly.")

# 🚀 Entrypoint
if __name__ == "__main__":
    menu()
