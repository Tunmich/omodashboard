#!/bin/bash

echo "🔐 Wallet check in progress..."
python3 start_sniper_bot.py --wallet-check

echo "🚀 Starting dashboard and scheduler..."
python3 start_sniper_bot.py --dashboard --scheduler

echo "📦 Initializing OMO sniper modules..."

mkdir -p logs

echo "🧭 Launching Telegram intelligence listener..."
nohup python3 mint_watcher.py > logs/mint_watcher.log 2>&1 &

echo "🎮 Launching Telegram command bot..."
nohup python3 omo_bot.py > logs/omo_bot.log 2>&1 &

echo "🔫 Launching sniper patrol loop..."
nohup python3 trade_launcher.py > logs/trade_launcher.log 2>&1 &

echo "✅ All components running in background."