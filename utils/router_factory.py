# utils/router_factory.py

from web3 import Web3
import json

def get_router_for_chain(chain_name):
    router_map = {
        "ethereum": {
            "rpc": "https://mainnet.infura.io/v3/YOUR_KEY",
            "router": "0x7a250d5630B4cF539739df2C5dAcb4c659F2488D",
            "weth": "0xC02aaa39b223FE8D0A0E5C4F27eAD9083C756Cc2"
        },
        "bnb": {
            "rpc": "https://bsc-dataseed.binance.org/",
            "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
            "weth": "0xBB4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"  # WBNB
        }
    }

    config = router_map.get(chain_name)
    if not config:
        raise ValueError("Chain not supported")

    web3 = Web3(Web3.HTTPProvider(config["rpc"]))
    with open("abis/uniswap_v2_router.json", "r") as f:
        abi = json.load(f)
    router = web3.eth.contract(address=Web3.toChecksumAddress(config["router"]), abi=abi)

    return {
        "web3": web3,
        "router": router,
        "weth": Web3.toChecksumAddress(config["weth"])
    }