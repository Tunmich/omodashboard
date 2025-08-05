from web3 import Web3
import os
import json
import logging
from dotenv import load_dotenv

load_dotenv()

INFURA_URL = os.getenv("INFURA_RPC")
PRIVATE_KEY = os.getenv("EVM_PRIVATE_KEY")
WALLET_ADDRESS = Web3.to_checksum_address(os.getenv("EVM_WALLET"))
BUY_AMOUNT_ETH = float(os.getenv("ETH_PER_TRADE", "0.01"))
SLIPPAGE_TOLERANCE = float(os.getenv("SLIPPAGE_TOLERANCE", "0.05"))  # 5%

# 🛠 Contract Addresses (Uniswap v2 on Ethereum mainnet)
ROUTER_ADDRESS = Web3.to_checksum_address("0x7a250d5630B4cF539739df2C5dAcb4c659F2488D")
WETH_ADDRESS = Web3.to_checksum_address("0xC02aaA39b223FE8D0a0e5C4F27eAD9083C756Cc2")

# 🧠 ABI loading
with open("modules/abi/uniswap_router.json", "r") as f:
    UNISWAP_ABI = json.load(f)
with open("modules/abi/erc20.json", "r") as f:
    ERC20_ABI = json.load(f)

web3 = Web3(Web3.HTTPProvider(INFURA_URL))
router = web3.eth.contract(address=ROUTER_ADDRESS, abi=UNISWAP_ABI)

def execute_evm_trade(token):
    try:
        token_address = Web3.to_checksum_address(token["address"])
        token_symbol = token.get("symbol", "UNK")
        buy_eth = token.get("buy_amount", BUY_AMOUNT_ETH)

        # ✅ Construct path: ETH → Token
        path = [WETH_ADDRESS, token_address]

        # 🧠 Estimate amountOutMin with slippage
        amounts = router.functions.getAmountsOut(web3.to_wei(buy_eth, "ether"), path).call()
        amount_out_min = int(amounts[1] * (1 - SLIPPAGE_TOLERANCE))

        # 🛡 Build transaction
        txn = router.functions.swapExactETHForTokens(
            amount_out_min,
            path,
            WALLET_ADDRESS,
            int(web3.eth.get_block("latest")["timestamp"]) + 60
        ).build_transaction({
            "from": WALLET_ADDRESS,
            "value": web3.to_wei(buy_eth, "ether"),
            "gas": 250000,
            "gasPrice": web3.to_wei("5", "gwei"),
            "nonce": web3.eth.get_transaction_count(WALLET_ADDRESS)
        })

        # 🔐 Sign & send
        signed = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed.rawTransaction)
        tx_url = f"https://etherscan.io/tx/{tx_hash.hex()}"

        logging.info(f"✅ EVM Trade Executed: {token_symbol} | TX → {tx_url}")
        print(f"🟢 Bought {token_symbol} on Ethereum. TX: {tx_url}")

    except Exception as e:
        logging.error(f"🔥 EVM trade failed for {token.get('symbol')}: {e}")
        print(f"❌ Trade failed for {token.get('symbol')}: {e}")
