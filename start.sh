#!/bin/bash
echo "🔐 Wallet check in progress..."
python start_sniper_bot.py --wallet-check

echo "🚀 Starting dashboard and scheduler..."
python start_sniper_bot.py --dashboard --scheduler