# scanner/twitter_tracker.py

import snscrape.modules.twitter as sntwitter
import logging

# Keywords to track
SEARCH_TERMS = [
    "just launched", "new token", "now live",
    "DEXtools trending", "pair deployed", "#ERC20", "#memecoin"
]

def scan_twitter_buzz(limit=50):
    """
    Scrapes recent crypto tweets for hype signals.
    Returns list of rough token candidates (parsed from tweet text).
    """
    tokens = []
    try:
        for term in SEARCH_TERMS:
            query = f"{term} lang:en since:2025-07-20"
            for tweet in sntwitter.TwitterSearchScraper(query).get_items():
                if len(tokens) >= limit:
                    break
                content = tweet.content

                # 🧪 Basic address extraction (advanced version can use regex or NLP)
                if "0x" in content:
                    addr = content.split("0x")[1].split()[0][:40]
                    tokens.append({
                        "address": f"0x{addr}",
                        "source": "Twitter",
                        "tweet_text": content,
                        "user": tweet.user.username,
                        "name": "TweetToken",
                        "chain": "Ethereum"  # default — can infer later
                    })
    except Exception as e:
        logging.warning(f"⚠️ Twitter scrape failed: {e}")

    return tokens
