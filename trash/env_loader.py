# utils/env_loader.py

import os
import logging
from dotenv import load_dotenv

load_dotenv()  # Load from .env file once

def get_env(key: str, required: bool = False, fallback=None):
    value = os.getenv(key, fallback)
    if required and value is None:
        logging.warning(f"⚠️ Required env variable '{key}' is missing.")
    return value

def get_float(key: str, required: bool = False, fallback=None):
    val = get_env(key, required, fallback)
    try:
        return float(val)
    except (TypeError, ValueError):
        logging.warning(f"⚠️ Could not convert '{key}' to float. Using fallback: {fallback}")
        return fallback

def get_bool(key: str, fallback=False):
    val = get_env(key, fallback=fallback)
    return str(val).lower() in ["true", "1", "yes"]

def get_list(key: str, delimiter=",", fallback=None):
    val = get_env(key, fallback="")
    return val.split(delimiter) if val else fallback or []

def show_env_summary(keys: list):
    print("📦 Environment Summary:")
    for key in keys:
        print(f"• {key} = {os.getenv(key)}")
