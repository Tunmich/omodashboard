#!/bin/bash

echo "🛑 Initiating OMO shutdown..."

# Kill sniper modules
pkill -f "mint_watcher.py"
pkill -f "trade_launcher.py"
pkill -f "omo_bot.py"

echo "🧹 Sniper modules terminated."
echo "🗃️ Archiving logs..."

# Archive logs
mkdir -p logs/archive
timestamp=$(date +"%Y%m%d_%H%M%S")
mv logs/*.log logs/archive/omo_logs_$timestamp/

# Send Telegram shutdown alert with killfeed
echo "📡 Sending final mission report..."

# Generate killfeed summary
FEED=""
if [ -f sniper_log.txt ]; then
    FEED=$(tail -n 5 sniper_log.txt)
else
    FEED="No killfeed available."
fi

# Python inline alert via solana_executor send_telegram_alert
python3 - <<EOF
import os
from modules.solana_executor import send_telegram_alert
os.environ['TELEGRAM_BOT_TOKEN'] = os.getenv("TELEGRAM_BOT_TOKEN")
os.environ['TELEGRAM_CHAT_ID'] = os.getenv("TELEGRAM_CHAT_ID")

report = f"""🛑 *OMO Shutdown Sequence Initiated*

Mission logs archived.
Killfeed:
