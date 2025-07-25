from web3 import Web3
import json
import logging

from utils.config_loader import load_chain_config

def estimate_swap_output(chain_name, token_address, amount_in_eth):
    config = load_chain_config(chain_name)
    web3 = Web3(Web3.HTTPProvider(config["rpc"]))

    router_abi = json.load(open(f"config/{chain_name.lower()}_router_abi.json"))
    router = web3.eth.contract(address=Web3.to_checksum_address(config["router_address"]), abi=router_abi)

    amount_in_wei = web3.toWei(amount_in_eth, "ether")
    path = [Web3.to_checksum_address(config["router_address"]), Web3.to_checksum_address(token_address)]

    try:
        amounts = router.functions.getAmountsOut(amount_in_wei, path).call()
        return web3.fromWei(amounts[1], "ether")
    except:
        return 0  # No output estimate or routing issue