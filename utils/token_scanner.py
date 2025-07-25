import requests
import logging
import json
import os
import time
from dotenv import load_dotenv
from datetime import datetime
from utils.network import resilient_request
load_dotenv()

JUPITER_URL = "https://token.jup.ag/all"
MIRROR_PATH = "mirror/jupiter_tokens.json"
MIRROR_URL = "https://your-mirror.com/jupiter_tokens.json"  # optional

# ⏱ Max age allowed for local mirror in seconds
MAX_MIRROR_AGE = 600  # 10 minutes

def is_mirror_stale(path):
    try:
        last_modified = os.path.getmtime(path)
        return time.time() - last_modified > MAX_MIRROR_AGE
    except Exception:
        return True  # Consider stale if missing or inaccessible

def scan_solana_tokens(limit=20):
    tokens = []

    # 🔍 Try Jupiter first
    try:
        res = resilient_request(JUPITER_URL)
        if res:
            tokens = res.json()
            logging.info(f"✅ Fetched {len(tokens)} tokens from Jupiter")
        else:
            raise Exception(f"Jupiter returned status {res.status_code}")
    except Exception as e:
        logging.warning(f"⚠️ Jupiter failed: {e}")

        # 🔁 Try local mirror fallback
        if not os.path.exists(MIRROR_PATH) or is_mirror_stale(MIRROR_PATH):
            logging.info("🔄 Mirror is missing or stale — refreshing now...")
            try:
                res = requests.get(JUPITER_URL, timeout=10)
                if res.status_code == 200:
                    metadata = {
                        "source": "jupiter",
                        "synced_at": datetime.utcnow().isoformat(),
                        "count": len(tokens),
                        "tokens": res.json()
                    }
                    os.makedirs(os.path.dirname(MIRROR_PATH), exist_ok=True)
                    with open(MIRROR_PATH, "w", encoding="utf-8") as f:
                        json.dump(metadata, f, indent=2)
                    tokens = metadata["tokens"]
                    logging.info("✅ Local mirror refreshed from Jupiter")
            except Exception as e2:
                logging.error(f"❌ Mirror refresh failed: {e2}")

        if not tokens:
            try:
                with open(MIRROR_PATH, "r", encoding="utf-8") as f:
                    mirror = json.load(f)
                    tokens = mirror.get("tokens", [])
                logging.info(f"📁 Loaded cached mirror: {len(tokens)} tokens")
            except Exception as e3:
                logging.error(f"❌ Failed to load local mirror: {e3}")
                return []

    # 🎯 Filter fresh unlisted mints
    fresh = [t for t in tokens if not t.get("listed") or t.get("tags") == []]
    mints = [t.get("address") for t in fresh[:limit]]
    logging.info(f"✅ Discovered {len(mints)} fresh tokens.")
    return mints
