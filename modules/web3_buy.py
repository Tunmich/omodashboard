import json
import time
import logging
from web3 import Web3
from dotenv import load_dotenv
import os
from utils.wallet_mapper import get_safe_evm_wallet

# 🔒 Load environment variables
load_dotenv()
INFURA_URL = os.getenv("INFURA_URL")
WALLET_ADDRESS = os.getenv("WALLET_ADDRESS")
PRIVATE_KEY = os.getenv("PRIVATE_KEY")
import os
from dotenv import load_dotenv
load_dotenv()

# Auto-inject EVM wallet if missing
if not os.getenv("EVM_WALLET_ADDRESS"):
    try:
        # Use Phantom's known derivation logic or fetch from wallet connector
        # For now, simulate with fallback mapping
        sol_address = os.getenv("WALLET_ADDRESS")
        evm_address = get_safe_evm_wallet(sol_address)
        os.environ["EVM_WALLET_ADDRESS"] = evm_address
        print(f"🔐 EVM wallet injected from Phantom: {evm_address}")
    except Exception as e:
        print(f"⚠️ Failed to inject EVM wallet: {e}")

# ✅ Connect to Ethereum
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# 🧱 Uniswap V2 Router Setup
ROUTER_ADDRESS = Web3.to_checksum_address("0x7a250d5630B4cF539739df2C5dAcb4c659Ff2488D")  # Uniswap V2
with open("abis/uniswap_v2_router.json", "r") as f:
    router_abi = json.load(f)
router = web3.eth.contract(address=ROUTER_ADDRESS, abi=router_abi)

# 🔁 Standard WETH address on Ethereum
weth_address = Web3.to_checksum_address("0xC02aaa39b223FE8D0A0E5C4F27eAD9083C756Cc2")

# 📊 Price estimation using real DEX data
def get_estimated_min_output(amount_eth, token_out_address, slippage_pct=0.5):
    try:
        amount_in_wei = web3.toWei(amount_eth, 'ether')
        path = [weth_address, Web3.to_checksum_address(token_out_address)]

        amounts = router.functions.getAmountsOut(amount_in_wei, path).call()
        estimated_out = amounts[-1]
        min_out = int(estimated_out * (1 - slippage_pct / 100))

        logging.info(f"📊 Estimated output: {estimated_out} — Min after slippage: {min_out}")
        return min_out
    except Exception as e:
        logging.warning(f"⚠️ Failed to fetch output estimate: {e}")
        return 0

# 🔒 Sell simulation logic removed

# 🛒 Execute real trade (ETH → Token)
def buy_token(token_address, amount_eth=0.01, slippage_pct=0.5):
    try:
        token_out = Web3.to_checksum_address(token_address)
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