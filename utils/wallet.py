from dotenv import load_dotenv
import os
import logging

from utils.logger_config import setup_logger
setup_logger()

load_dotenv()

wallet_address = os.getenv("WALLET_ADDRESS")
private_key = os.getenv("PRIVATE_KEY")