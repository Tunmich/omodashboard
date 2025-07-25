# utils/chat_id_resolver.py

import os
import re
from dotenv import load_dotenv
from telethon import TelegramClient

# 📥 Load existing environment variables
load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID", "0"))
API_HASH = os.getenv("TELEGRAM_API_HASH", "")
SESSION_NAME = "user_session"
KEYWORDS = ["meme", "alpha", "ca"]  # 🔍 Filter terms

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

def sanitize_label(label):
    """Sanitize group/channel name to create a clean key suffix"""
    return re.sub(r'\W+', '_', label.lower()).strip("_")

def load_existing_ids():
    """Load existing CHANNEL_ID_X values from .env"""
    existing = set()
    if not os.path.exists(".env"):
        return existing

    # 💡 This line tells Python to read using UTF-8, avoiding weird character decoding errors
    with open(".env", "r", encoding="utf-8") as env_file:
        for line in env_file:
            if line.startswith("CHANNEL_ID_"):
                value = line.strip().split("=")[-1]
                existing.add(value)
    return existing

def generate_env_key(label, existing_keys):
    """Generate unique key based on label (e.g., CHANNEL_MEME_2)"""
    base = f"CHANNEL_{sanitize_label(label)}"
    count = 1
    while f"{base}_{count}" in existing_keys:
        count += 1
    return f"{base}_{count}"

async def resolve_and_write_group_ids():
    matches = []
    async for dialog in client.iter_dialogs():
        name = dialog.name or ""
        name_lower = name.lower()
        if any(keyword in name_lower for keyword in KEYWORDS):
            matches.append((str(dialog.id), name))

    if not matches:
        print("😢 No matching channels or groups found.")
        return

    print("\n📦 Matched Channels/Groups:")
    for i, (chat_id, name) in enumerate(matches, start=1):
        print(f"[{i}] {name} → ID: {chat_id}")

    choice = input("\n💬 Enter numbers of groups to save (comma-separated): ").split(",")
    selected = [matches[int(idx.strip()) - 1] for idx in choice if idx.strip().isdigit() and 0 < int(idx.strip()) <= len(matches)]

    existing_ids = load_existing_ids()
    existing_keys = set()
    if os.path.exists(".env"):
        with open(".env", "r") as env:
            for line in env:
                key = line.strip().split("=")[0]
                existing_keys.add(key)

    new_entries = []
    with open(".env", "a") as env_file:
        for chat_id, name in selected:
            if chat_id in existing_ids:
                print(f"⏭️ Skipped (already saved): {name} → ID: {chat_id}")
                continue

            env_key = generate_env_key(name, existing_keys)
            env_file.write(f"{env_key}={chat_id}\n")
            new_entries.append((env_key, name, chat_id))
            existing_keys.add(env_key)

    if new_entries:
        print("\n✅ New Entries Added:")
        for key, name, cid in new_entries:
            print(f"- {key}: {name} → {cid}")
    else:
        print("🔁 Nothing new was added.")

if __name__ == "__main__":
    with client:
        client.loop.run_until_complete(resolve_and_write_group_ids())
