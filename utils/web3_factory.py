import os
import time
import logging
import json
from utils.safe_web3 import SafeWeb3

# 🔗 Load static RPCs from .env and hardcoded defaults
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

def get_web3_provider(chain):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

    # 🔁 Try live healthy_rpcs.json first (if available)
    try:
        with open("healthy_rpcs.json", "r") as f:
            rpc_data = json.load(f)
        rpc_list = rpc_data.get(chain, [])
        logging.info(f"📁 Loaded healthy RPCs for {chain} from JSON")
    except Exception as e:
        logging.warning(f"⚠️ [{timestamp}] Could not load healthy_rpcs.json: {e}")
        rpc_list = []

    # ➕ Fallback to static RPCs if JSON is missing or empty
    if not rpc_list:
        rpc_list = STATIC_RPCS.get(chain, [])
        logging.info(f"🔁 Using static RPCs for {chain}")

    # ✅ Connect to first working RPC
    for url in rpc_list:
        if url:
            try:
                provider = SafeWeb3(url)
                if provider.web3.isConnected():
                    logging.info(f"🟢 [{timestamp}] Connected to {chain} via {url}")
                    return provider
            except Exception as e:
                logging.warning(f"❌ [{timestamp}] RPC failure for {chain}: {url} → {e}")
                continue

    # 🚫 All failed
    logging.error(f"❌ [{timestamp}] No healthy RPCs found for {chain}")
    return None