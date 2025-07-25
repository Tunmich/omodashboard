# utils/network.py

import requests
import logging
import time

def resilient_request(url, retries=3, timeout=10, method="get", **kwargs):
    attempt = 0
    while attempt < retries:
        try:
            response = requests.request(method, url, timeout=timeout, **kwargs)
            if response.status_code == 200:
                return response
            else:
                logging.warning(f"⚠️ Response status {response.status_code} from {url}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"❌ Request failed: {e}")
        attempt += 1
        time.sleep(2)  # cooldown before retry
    logging.error(f"🚫 Failed to fetch {url} after {retries} attempts.")
    return None
