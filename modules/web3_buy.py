import json
import time
import logging
from web3 import Web3
from dotenv import load_dotenv
import os

# 🔒 Load environment variables
load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")

# ✅ Connect to Ethereum
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# 🧱 Uniswap V2 Router Setup
ROUTER_ADDRESS = Web3.toChecksumAddress("0x7a250d5630B4cF539739df2C5dAcb4c659Ff2488D")  # Uniswap V2
with open("abis/uniswap_v2_router.json", "r") as f:
    router_abi = json.load(f)
router = web3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)

# 🔁 Standard WETH address on Ethereum
weth_address = Web3.toChecksumAddress("0xC02aaa39b223FE8D0A0E5C4F27eAD9083C756Cc2")

# 📊 Price estimation using real DEX data
def get_estimated_min_output(amount_eth, token_out_address, slippage_pct=0.5):
    try:
        amount_in_wei = web3.toWei(amount_eth, 'ether')
        path = [weth_address, Web3.toChecksumAddress(token_out_address)]

        amounts = router.functions.getAmountsOut(amount_in_wei, path).call()
        estimated_out = amounts[-1]
        min_out = int(estimated_out * (1 - slippage_pct / 100))

        logging.info(f"📊 Estimated output: {estimated_out} — Min after slippage: {min_out}")
        return min_out
    except Exception as e:
        logging.warning(f"⚠️ Failed to fetch output estimate: {e}")
        return 0

# 🔒 Sell simulation to avoid honeypots
def simulate_sell(token_address):
    try:
        token_contract = web3.eth.contract(
            address=Web3.toChecksumAddress(token_address),
            abi=json.load(open("abis/erc20_token.json"))
        )
        balance = token_contract.functions.balanceOf(WALLET_ADDRESS).call()
        if balance == 0:
            logging.info(f"🚫 No balance in token {token_address}, skipping sell check")
            return False

        path = [Web3.toChecksumAddress(token_address), weth_address]
        result = router.functions.getAmountsOut(balance, path).call()
        return result[-1] > 0
    except Exception as e:
        logging.warning(f"Sell simulation failed for {token_address}: {e}")
        return False

# 🛒 Execute real trade (ETH → Token)
def buy_token(token_address, amount_eth=0.01, slippage_pct=0.5):
    try:
        token_out = Web3.toChecksumAddress(token_address)
        path = [weth_address, token_out]
        deadline = int(time.time()) + 300

        min_tokens = get_estimated_min_output(amount_eth, token_out, slippage_pct)
        if min_tokens == 0:
            logging.warning(f"⛔ Skipping trade: Could not estimate minTokens for {token_out}")
            return None

        txn = router.functions.swapExactETHForTokens(
            min_tokens, path, WALLET_ADDRESS, deadline
        ).build_transaction({
            'from': WALLET_ADDRESS,
            'value': web3.toWei(amount_eth, 'ether'),
            'gas': 250000,
            'gasPrice': web3.toWei('10', 'gwei'),
            'nonce': web3.eth.getTransactionCount(WALLET_ADDRESS),
        })

        signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)
        tx_hash = web3.eth.send_raw_transaction(signed_txn.rawTransaction)
        tx_url = f"https://etherscan.io/tx/{web3.toHex(tx_hash)}"
        logging.info(f"✅ Trade broadcasted: {tx_url}")
        return tx_url

    except Exception as e:
        logging.error(f"🔥 Trade execution failed: {e}")
        return None