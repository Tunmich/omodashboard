import logging
from scanner.solana_scanner import scan_solana_tokens
from scanner.eth_scanner import scan_eth_tokens
from scanner.bnb_scanner import scan_bnb_tokens
from scanner.base_scanner import scan_base_tokens
from scanner.dex_screener import get_dex_candidates
from utils.token_enricher import enrich_token_data

logging.basicConfig(level=logging.INFO)

def fetch_live_tokens(limit_per_chain=10):
    """
    Aggregates token candidates across Solana, EVM, BNB, Base, and Dex.
    Returns unified list of token dicts compatible with strategy engine.
    """
    tokens = []

    try:
        solana_tokens = scan_solana_tokens(limit=limit_per_chain)
        logging.info(f"✅ Solana tokens: {len(solana_tokens)}")
        tokens.extend([enrich_token_data(t) for t in solana_tokens])
    except Exception as e:
        logging.warning(f"⚠️ Solana scanner failed: {e}")

    try:
        eth_tokens = scan_eth_tokens(limit=limit_per_chain)
        logging.info(f"✅ Ethereum tokens: {len(eth_tokens)}")
        tokens.extend([enrich_token_data(t) for t in eth_tokens])
    except Exception as e:
        logging.warning(f"⚠️ Ethereum scanner failed: {e}")

    try:
        bnb_tokens = scan_bnb_tokens(limit=limit_per_chain)
        logging.info(f"✅ BNB tokens: {len(bnb_tokens)}")
        tokens.extend([enrich_token_data(t) for t in bnb_tokens])
    except Exception as e:
        logging.warning(f"⚠️ BNB scanner failed: {e}")

    try:
        base_tokens = scan_base_tokens(limit=limit_per_chain)
        logging.info(f"✅ Base tokens: {len(base_tokens)}")
        tokens.extend([enrich_token_data(t) for t in base_tokens])
    except Exception as e:
        logging.warning(f"⚠️ Base scanner failed: {e}")

    try:
        dex_tokens = get_dex_candidates(limit=limit_per_chain)
        logging.info(f"✅ Dex tokens: {len(dex_tokens)}")
        tokens.extend([enrich_token_data(t) for t in dex_tokens])
    except Exception as e:
        logging.warning(f"⚠️ Dex scanner failed: {e}")

    return tokens
