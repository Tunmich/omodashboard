# utils/web3_factory.py

import os
import time
import logging
import json
from utils.safe_web3 import SafeWeb3

# 🔗 Load static RPCs from .env and fallback defaults
STATIC_RPCS = {
    "Ethereum": [
        os.getenv("RPC_ETH"),
        os.getenv("RPC_ETH_FALLBACK"),
        "https://eth.llamarpc.com",
        "https://rpc.ankr.com/eth"
    ],
    "BNB": [
        os.getenv("RPC_BNB"),
        os.getenv("RPC_BNB_FALLBACK"),
        "https://rpc.ankr.com/bsc",
        "https://bsc-dataseed1.ninicoin.io"
    ],
    "Base": [
        os.getenv("RPC_BASE"),
        os.getenv("RPC_BASE_FALLBACK"),
        "https://base.publicnode.com",
        "https://mainnet.base.org"
    ]
}

def get_web3_provider(chain: str):
    """
    Returns a connected SafeWeb3 instance for the specified chain, using either dynamic
    healthy RPCs or static fallback options.

    Args:
        chain (str): Blockchain name (Ethereum, BNB, Base)

    Returns:
        SafeWeb3 or None: A working RPC provider or None if all fail
    """
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    rpc_list = []

    # 🔁 Load healthy RPCs from local cache
    try:
        with open("healthy_rpcs.json", "r") as f:
            rpc_data = json.load(f)
        rpc_list = rpc_data.get(chain, [])
        logging.info(f"[{timestamp}] 📁 Loaded healthy RPCs for {chain} from JSON")
    except Exception as e:
        logging.warning(f"[{timestamp}] ⚠️ Could not load healthy_rpcs.json: {e}")

    # ➕ Use static fallback if none are available
    if not rpc_list:
        rpc_list = STATIC_RPCS.get(chain, [])
        logging.info(f"[{timestamp}] 🔁 Using static RPCs for {chain}")

    # ✅ Try each RPC until one succeeds
    for url in rpc_list:
        if url:
            try:
                provider = SafeWeb3(url)
                if provider.is_connected():  # Updated to match SafeWeb3
                    return provider
                    logging.info(f"[{timestamp}] 🟢 Connected to {chain} via {url}")
                else:
                    logging.warning(f"[{timestamp}] ⚠️ RPC not responsive: {url}")
            except Exception as e:
                logging.warning(f"[{timestamp}] ❌ RPC failure for {chain}: {url} → {e}")
                continue
def is_connected(self) -> bool:
    try:
        return self.web3.is_connected()
    except Exception as e:
        logging.warning(f"⚠️ RPC connect check failed: {e}")
        return False

    # 🚫 All attempts failed
    logging.error(f"[{timestamp}] ❌ No healthy RPCs found for {chain}")
    return None
