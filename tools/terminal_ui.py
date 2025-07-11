import os
import time
import logging

def menu():
    os.system("clear")
    print("\n🛠️  Meme Token Radar CLI")
    print("----------------------------")
    print("1. View Bot Logs")
    print("2. Refresh Mock Tokens")
    print("3. Run Backtest")
    print("4. Open Dashboard")
    print("5. Stop Bot")
    print("0. Exit")
    print("6. Run Telegram Controller")

def loop():
    while True:
        menu()
        choice = input("\n👉 Choose an option: ")
        if choice == "1":
            os.system("tail -n 20 logs/token_scan.log")
        elif choice == "2":
            os.system("python tools/token_mock_cli.py -n 20")
        elif choice == "3":
            os.system("python strategy/backtest_engine.py")
        elif choice == "4":
            os.system("streamlit run dashboard/app.py")
        elif choice == "5":
            os.system("docker stop sniperbot")
        elif choice == "6":
         os.system("python alerts/telegram_controller.py")
        elif choice == "0":
            print("👋 Goodbye!")
            break
        else:
            print("⚠️ Invalid choice!")
        input("\nPress Enter to continue...")


if __name__ == "__main__":
    loop()