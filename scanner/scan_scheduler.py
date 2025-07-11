import logging

from utils.logger_config import setup_logger
setup_logger()
from scanner.eth_scanner import scan_eth_tokens
from scanner.bnb_scanner import scan_bnb_tokens
from scanner.base_scanner import scan_base_tokens
from scanner.solana_scanner import scan_solana_tokens

def get_all_tokens():
    return scan_eth_tokens() + scan_bnb_tokens() + scan_base_tokens() + scan_solana_tokens()