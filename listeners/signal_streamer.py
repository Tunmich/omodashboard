# listeners/signal_streamer.py

from telethon import TelegramClient, events
from dotenv import load_dotenv
import os
import re
from datetime import datetime
from strategy.trade_decision_engine import evaluate_signal  # optional hook
from utils.telegram_alert import send_signal_alert          # optional alert

load_dotenv()

# 🔐 Telegram session
API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
client = TelegramClient("user_session", API_ID, API_HASH)

# 🧠 Keyword triggers
KEYWORDS = ["contract address", "CA", "$SOL", "mint", "deploy", "launch", "live"]

# 📦 Load channel IDs
channel_ids = []
for key, value in os.environ.items():
    if key.startswith("CHANNEL_ID_"):
        channel_ids.append(int(value))

# 🧪 Signal parser
def is_signal(msg):
    msg_lower = msg.lower()
    return any(keyword in msg_lower for keyword in KEYWORDS)

def extract_ca_from_text(text):
    matches = re.findall(r'(?:0x)?[a-fA-F0-9]{35,}', text)
    return matches[0] if matches else None

@client.on(events.NewMessage(chats=channel_ids))
async def handler(event):
    text = event.message.message
    if not text or not is_signal(text):
        return

    ca_address = extract_ca_from_text(text)
    source = await event.get_chat()
    signal = {
        "source": source.title,
        "chat_id": event.chat_id,
        "msg_id": event.id,
        "timestamp": str(datetime.utcnow()),
        "text": text,
        "ca_address": ca_address
    }

    print(f"📡 Signal received → {signal['source']} | CA: {ca_address}")
    
    # Optional alert
    if ca_address:
        await send_signal_alert(signal)

    # Optional evaluation hook
    evaluate_signal(signal)

# 🚀 Start streamer
def start_signal_streamer():
    print("👂 Listening for CA drops...")
    client.run_until_disconnected()

if __name__ == "__main__":
    start_signal_streamer()
