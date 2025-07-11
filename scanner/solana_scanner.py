import logging

from utils.logger_config import setup_logger
setup_logger()

def scan_solana_tokens():
    """
    Simulates scanning Solana-based meme tokens.
    Returns a list of token dictionaries.
    """
    return [
        {
            "name": "SolMeme",
            "chain": "Solana",
            "address": "SoLAA1xyzVb7YZZy9pGWQkDfA2t1Z2ZxMeme88",
            "buzz_score": 69,
            "token_price_usd": 0.0011
        },
        {
            "name": "SolTroll",
            "chain": "Solana",
            "address": "SoLBB2abcVb7YZZy9pGWQkDfA2t1Z2ZxTroll99",
            "buzz_score": 65,
            "token_price_usd": 0.0009
        }
    ]