# utils/logger_config.py

import logging
import os

def setup_logger(name: str, log_file: str = "app.log", level: int = logging.INFO) -> logging.Logger:
    """Sets up and returns a named logger with both file and console handlers."""

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)
    log_path = os.path.join("logs", log_file)

    # Format config
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s:%(name)s: %(message)s", "%Y-%m-%d %H:%M:%S"
    )

    # File handler
    file_handler = logging.FileHandler(log_path)
    file_handler.setFormatter(formatter)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Create or get the logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
