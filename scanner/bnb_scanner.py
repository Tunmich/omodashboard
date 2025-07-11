import logging

from utils.logger_config import setup_logger
setup_logger()

def scan_bnb_tokens():
    """
    Simulates scanning BNB-based meme tokens.
    Returns a list of token dictionaries.
    """
    return [
        {
            "name": "BNBPepe",
            "chain": "BNB",
            "address": "0xBNB1110000000000000000000000000000000011",
            "buzz_score": 78,
            "token_price_usd": 0.0018
        },
        {
            "name": "ZoomBNB",
            "chain": "BNB",
            "address": "0xBNB2220000000000000000000000000000000022",
            "buzz_score": 74,
            "token_price_usd": 0.0014
        }
    ]