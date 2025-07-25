import logging

from utils.logger_config import setup_logger
logger = setup_logger("eth_scanner")

def scan_eth_tokens(limit=30):
    """
    Simulates scanning Ethereum-based meme tokens.
    Returns a list of token dictionaries.
    """
    return [
        {
            "name": "ETHMeme",
            "chain": "Ethereum",
            "address": "0xABC1230000000000000000000000000000000001",
            "buzz_score": 91,
            "token_price_usd": 0.0045
        },
        {
            "name": "TurboShiba",
            "chain": "Ethereum",
            "address": "0xDEF4560000000000000000000000000000000002",
            "buzz_score": 87,
            "token_price_usd": 0.0023
        }
    ]