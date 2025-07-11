# tools/rpc_monitor.py
import time
import logging
import json

from web3 import Web3

RPCS = {
    "Ethereum": [
        "https://mainnet.infura.io/v3/YOUR_INFURA_PROJECT_ID",
        "https://eth.llamarpc.com",
        "https://rpc.ankr.com/eth"
    ],
    "BNB": [
        "https://bsc-dataseed.binance.org/",
        "https://bsc.publicnode.com",
        "https://rpc.ankr.com/bsc"
    ],
    "Base": [
        "https://mainnet.base.org",
        "https://base.publicnode.com",
        "https://base.llamarpc.com"
    ]
}

HEALTHY_RPCS = {}

def test_rpc(chain, url):
    try:
        web3 = Web3(Web3.HTTPProvider(url))
        return web3.is_connected()
    except Exception as e:
        logging.warning(f"❌ Error testing RPC [{chain}]: {url} → {e}")
        return False

def save_healthy_rpcs():
    with open("healthy_rpcs.json", "w") as f:
        json.dump(HEALTHY_RPCS, f, indent=2)
    logging.info("📁 healthy_rpcs.json updated.")

def monitor_loop():
    while True:
        print("📡 Scanning RPC health...")
        for chain, urls in RPCS.items():
            healthy = [url for url in urls if test_rpc(chain, url)]
            HEALTHY_RPCS[chain] = healthy
            logging.info(f"🟢 {chain} healthy RPCs: {healthy}")
        save_healthy_rpcs()
        time.sleep(300)  # 🔁 Scan every 5 minutes

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    monitor_loop()