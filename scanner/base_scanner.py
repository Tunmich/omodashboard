import logging

from utils.logger_config import setup_logger
logger = setup_logger("base_scanner")

def scan_base_tokens(limit=30):
    """
    Simulates scanning Base-based meme tokens.
    Returns a list of token dictionaries.
    """
    return [
        {
            "name": "BaseDOGE",
            "chain": "Base",
            "address": "0xBASEAAA000000000000000000000000000000A1",
            "buzz_score": 83,
            "token_price_usd": 0.0031
        },
        {
            "name": "ChadBase",
            "chain": "Base",
            "address": "0xBASEBBB000000000000000000000000000000B2",
            "buzz_score": 88,
            "token_price_usd": 0.0029
        }
    ]