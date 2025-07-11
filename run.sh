#!/bin/bash

echo "🚀 Launching Meme Token Radar Fullstack..."

# Build Docker image if needed
docker image inspect meme-sniper > /dev/null 2>&1 || docker build -t meme-sniper .

# Start Telegram controller
echo "📲 Starting Telegram command listener..."
nohup python alerts/telegram_controller.py > logs/telegram_control.log 2>&1 &
nohup python scheduler/report_loop.py > logs/report.log 2>&1 &

echo "✅ Bot now controllable via Telegram."