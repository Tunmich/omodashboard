# utils/logger_config.py
import logging
# utils/logger_config.py

import logging
from logging.handlers import RotatingFileHandler

def setup_logger(log_file="terminal_log.txt", max_bytes=5_000_000, backup_count=3):
    logger = logging.getLogger()
    if logger.hasHandlers():
        return

    logger.setLevel(logging.INFO)

    # Main log: rotates when it hits ~5MB
    handler = RotatingFileHandler(log_file, maxBytes=max_bytes, backupCount=backup_count)
    formatter = logging.Formatter("%(asctime)s — %(levelname)s — %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    # Optional: Also log to terminal
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)