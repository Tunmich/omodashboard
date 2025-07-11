from web3 import Web3
from utils.retry_rpc import retry_rpc_call
import logging

class SafeWeb3:
    def __init__(self, rpc_url):
        self.web3 = Web3(Web3.HTTPProvider(rpc_url))

    def get_block_number(self):
        return retry_rpc_call(self.web3.eth.get_block_number)

    def get_gas_price(self):
        return retry_rpc_call(self.web3.eth.gas_price)

    def get_token_info(self, address):
        try:
            name_call = self.web3.eth.contract(address=address, abi=[]).functions.name()
            symbol_call = self.web3.eth.contract(address=address, abi=[]).functions.symbol()
            decimals_call = self.web3.eth.contract(address=address, abi=[]).functions.decimals()

            name = retry_rpc_call(name_call.call)
            symbol = retry_rpc_call(symbol_call.call)
            decimals = retry_rpc_call(decimals_call.call)
            return {"name": name, "symbol": symbol, "decimals": decimals}
        except Exception as e:
            logging.warning(f"⚠️ Failed to fetch token info: {e}")
            return {}

    def get_swap_output(self, router, input_token, output_token, amount_in_wei):
        try:
            path = [input_token, output_token]
            estimate_call = router.functions.getAmountsOut(amount_in_wei, path)
            amounts = retry_rpc_call(estimate_call.call)
            return amounts[-1] if amounts else 0
        except Exception as e:
            logging.warning(f"⚠️ Failed to get swap output: {e}")
            return 0