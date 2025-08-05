# backup_project.sh

#!/bin/bash
echo "📦 Creating backup zip of Meme_bot..."
zip -r Meme_bot_backup_$(date +%Y%m%d_%H%M).zip Meme_bot
echo "✅ Backup complete."
