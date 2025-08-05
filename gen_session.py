from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError
import os
from dotenv import load_dotenv

load_dotenv()

API_ID = int(os.getenv("TELEGRAM_API_ID"))
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("LOGIN_PHONE")

client = TelegramClient("user_session", API_ID, API_HASH)

async def main():
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(PHONE)
        code = input("📩 Enter the code sent to your Telegram: ")

        try:
            await client.sign_in(PHONE, code)
        except SessionPasswordNeededError:
            password = input("🔐 Enter your Telegram login password: ")
            await client.sign_in(password=password)

    print("✅ Session file generated successfully!")

if __name__ == "__main__":
    client.loop.run_until_complete(main())
