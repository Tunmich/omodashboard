# utils/creator_tracker.py

import logging
import threading
from typing import Dict

# 🧠 Thread-safe score tracker
creator_scores: Dict[str, Dict[str, int]] = {}
scores_lock = threading.Lock()  # prevents race conditions

def update_creator_score(creator: str, outcome: str) -> None:
    """
    Updates the internal stats for a creator wallet.
    Outcome must be 'Success' or 'Failed'.
    """
    if not isinstance(creator, str):
        logging.warning(f"⚠️ Invalid creator type: {type(creator)} — must be str")
        return

    if outcome not in ("Success", "Failed"):
        logging.warning(f"⚠️ Invalid outcome: {outcome}")
        return

    with scores_lock:
        if creator not in creator_scores:
            creator_scores[creator] = {"successes": 0, "fails": 0}

        creator_scores[creator]["successes"] += (outcome == "Success")
        creator_scores[creator]["fails"] += (outcome == "Failed")

        logging.info(f"📊 Score updated for {creator}: {creator_scores[creator]}")

def get_creator_score(creator: str) -> int:
    """
    Returns raw score (successes - failures).
    """
    if not isinstance(creator, str):
        logging.warning(f"⚠️ Invalid creator type: {type(creator)}")
        return 0

    with scores_lock:
        stats = creator_scores.get(creator, {"successes": 0, "fails": 0})
        return stats["successes"] - stats["fails"]

def get_creator_history_score(creator: str) -> int:
    """
    Returns normalized reputation score (0 to 100).
    Based on success/failure ratio.
    """
    if not isinstance(creator, str):
        logging.warning(f"⚠️ Invalid creator type: {type(creator)}")
        return 0

    with scores_lock:
        stats = creator_scores.get(creator, {"successes": 0, "fails": 0})
        total = stats["successes"] + stats["fails"]

        if total == 0:
            logging.info(f"⚠️ No trade history for creator {creator} — default score applied")
            return 50  # neutral trust

        ratio = stats["successes"] / total
        score = int(ratio * 100)
        logging.info(f"📈 Reputation score for {creator}: {score} ({stats['successes']} success / {stats['fails']} fail)")
        return score
