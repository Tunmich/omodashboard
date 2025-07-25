# utils/safe_web3.py

from web3 import Web3
import logging

class SafeWeb3:
    def __init__(self, rpc_url: str):
        self.rpc_url = rpc_url
        self.web3 = Web3(Web3.HTTPProvider(self.rpc_url))

    def is_connected(self) -> bool:
        try:
            return self.web3.is_connected()
        except Exception as e:
            logging.warning(f"RPC connect check failed for {self.rpc_url}: {e}")
            return False

    def get_block_number(self) -> int:
        try:
            return self.web3.eth.block_number
        except Exception as e:
            logging.warning(f"Failed to fetch block number: {e}")
            return -1

    def get_gas_price(self) -> int:
        try:
            return self.web3.eth.gas_price
        except Exception as e:
            logging.warning(f"Failed to fetch gas price: {e}")
            return -1

    def get_token_info(self, token_address: str) -> dict:
        if not self.web3.is_address(token_address):
            logging.warning(f"Invalid token address format: {token_address}")
            return {"name": "", "symbol": "", "decimals": ""}

        try:
            abi = [
                {"constant": True, "inputs": [], "name": "name", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "symbol", "outputs": [{"name": "", "type": "string"}], "type": "function"},
                {"constant": True, "inputs": [], "name": "decimals", "outputs": [{"name": "", "type": "uint8"}], "type": "function"}
            ]
            contract = self.web3.eth.contract(
                address=self.web3.to_checksum_address(token_address),
                abi=abi
            )

            try:
                name = contract.functions.name().call()
            except Exception:
                name = ""

            try:
                symbol = contract.functions.symbol().call()
            except Exception:
                symbol = ""

            try:
                decimals = contract.functions.decimals().call()
            except Exception:
                decimals = ""

            return {"name": name, "symbol": symbol, "decimals": decimals}
        except Exception as e:
            logging.warning(f"Token metadata fetch failed for {token_address}: {e}")
            return {"name": "", "symbol": "", "decimals": ""}
