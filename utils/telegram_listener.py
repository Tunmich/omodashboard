# utils/telegram_listener.py

import os
import logging
import requests
import time
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
BASE_URL = f"https://api.telegram.org/bot{TOKEN}"

last_update_id = None  # memory of last command

def get_updates():
    url = f"{BASE_URL}/getUpdates"
    params = {"timeout": 15}
    if last_update_id:
        params["offset"] = last_update_id + 1
    try:
        res = requests.get(url, params=params, timeout=20)
        return res.json()["result"]
    except Exception as e:
        logging.error(f"🔻 Telegram polling failed: {e}")
        return []

def send_reply(text):
    url = f"{BASE_URL}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": text}
    try:
        requests.post(url, json=payload, timeout=10)
    except Exception as e:
        logging.warning(f"⚠️ Telegram reply error: {e}")

def toggle_sniper_pause(pause=True):
    flag = "True" if pause else "False"
    lines = []
    with open(".env", "r") as f:
        for line in f:
            if line.startswith("SNIPER_PAUSED="):
                lines.append(f"SNIPER_PAUSED={flag}\n")
            else:
                lines.append(line)
    with open(".env", "w") as f:
        f.writelines(lines)
    load_dotenv()
    state = "paused" if pause else "resumed"
    send_reply(f"⏸️ Sniper has been {state.upper()}.")

def listen_telegram_commands():
    global last_update_id
    send_reply("👂 Listening for commands...")

    while True:
        updates = get_updates()
        for update in updates:
            last_update_id = update["update_id"]
            if "message" not in update or "text" not in update["message"]:
                continue
            text = update["message"]["text"].strip().lower()
            logging.info(f"📨 Telegram command received: {text}")

            if text == "/help":
                send_reply("""
🤖 OMO Command List:
/status – Show sniper engine status
/killfeed – Show last trades
/pause – Stop sniper engine
/resume – Reactivate sniper engine
/help – Show this menu
""".strip())
            elif text == "/pause":
                toggle_sniper_pause(True)
            elif text == "/resume":
                toggle_sniper_pause(False)
            elif text == "/status":
                send_reply("🧠 Sniper is active. Cooldown, budget, and system health are normal.")
            elif text == "/killfeed":
                send_reply("📜 Killfeed: no trades yet. Waiting for sniper activity.")
            else:
                send_reply("❓ Unknown command. Use /help")

        time.sleep(3)
