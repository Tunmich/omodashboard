# utils/mirror_daemon.py

import requests
import json
import time
import logging
from datetime import datetime

JUPITER_URL = "https://token.jup.ag/all"
MIRROR_PATH = "mirror/jupiter_tokens.json"

def update_mirror():
    try:
        res = requests.get(JUPITER_URL, timeout=15)
        if res.status_code != 200:
            logging.warning(f"⚠️ Mirror update failed: Jupiter returned {res.status_code}")
            return

        tokens = res.json()
        metadata = {
            "source": "jupiter",
            "synced_at": datetime.utcnow().isoformat(),
            "count": len(tokens),
            "tokens": tokens
        }

        with open(MIRROR_PATH, "w", encoding="utf-8") as f:
            json.dump(metadata, f, indent=2)
        logging.info(f"✅ Mirror updated: {len(tokens)} tokens cached.")
    except Exception as e:
        logging.error(f"❌ Mirror update failed: {e}")

if __name__ == "__main__":
    while True:
        update_mirror()
        time.sleep(600)  # Sync every 10 minutes
