from utils.trade_tracker import update_leaderboard
from utils.web3_factory import get_web3_provider
from utils.trade_predictor import predict_success

import logging
from web3 import Web3

from alerts.telegram_bot import send_message

SIMULATE_TRADES = True  # Set to False for live trading

# 🧠 Router map per chain
ROUTER_ADDRESSES = {
    "Ethereum": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",   # Uniswap V2
    "BNB": "0x10ED43C718714eb63d5aA57B78B54704E256024E",       # PancakeSwap V2
    "Base": "0x327Df1E6de05895d2ab08513aa0d9f61C3aBfD1f",       # BaseSwap V2
    "Solana": None  # Not EVM-compatible
}

USDC = "0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48"
TRADE_BUDGET_USD = 1.0
TRADE_AMOUNT_WEI = Web3.to_wei(TRADE_BUDGET_USD, "ether")
SLIPPAGE_PERCENT = 3

ROUTER_ABI = [{
    "name": "getAmountsOut",
    "type": "function",
    "stateMutability": "view",
    "inputs": [
        {"name": "amountIn", "type": "uint256"},
        {"name": "path", "type": "address[]"}
    ],
    "outputs": [{"name": "amounts", "type": "uint256[]"}]
}]

# 📲 Send trade result to Telegram
def send_trade_summary(token):
    pl = float(token.get("estimated_pl", 0))
    emoji = "💚" if pl > 0 else "🔴"

    summary = (
        f"{emoji} Trade Summary: {token['name']}\n"
        f"🔗 Chain: {token['chain']}\n"
        f"📦 Token: {token['address']}\n"
        f"📊 Return: {token.get('estimated_return')}\n"
        f"💰 Value: ${token.get('estimated_value')}\n"
        f"💸 P/L: ${pl}\n"
        f"⛽ Gas: ${token.get('estimated_gas_usd', 'N/A')}"
    )
    send_message(summary)

# 🔧 Simulate token trade with router + slippage + gas
def simulate_trade(token):
    try:
        update_leaderboard(token)

        provider = get_web3_provider(token["chain"])
        if not provider:
            logging.warning(f"🚫 No RPC provider for {token['chain']}")
            return

        web3 = provider.web3
        router_address = ROUTER_ADDRESSES.get(token["chain"])
        if not router_address:
            logging.warning(f"🚫 No router address configured for {token['chain']}")
            return

        router = web3.eth.contract(address=Web3.to_checksum_address(router_address), abi=ROUTER_ABI)
        path = [Web3.to_checksum_address(token["address"]), USDC]
        raw_amounts = router.functions.getAmountsOut(TRADE_AMOUNT_WEI, path).call()
        estimated_output = raw_amounts[-1] if raw_amounts else 0

        slippage = SLIPPAGE_PERCENT / 100
        final_output = int(estimated_output * (1 - slippage))
        token["estimated_return"] = final_output

        gas_price = provider.get_gas_price()
        estimated_gas = Web3.fromWei(gas_price * 150000, "ether")  # conservative 150k gas
        token["estimated_gas_usd"] = round(float(estimated_gas), 4)

        token_price = float(token.get("token_price_usd", 0.003))
        estimated_value = final_output * token_price
        token["estimated_value"] = round(estimated_value, 4)
        token["estimated_pl"] = round(estimated_value - TRADE_BUDGET_USD - token["estimated_gas_usd"], 4)

        logging.info(f"💸 {token['name']} → Raw: {estimated_output}, Final: {final_output}, P/L: {token['estimated_pl']}")

        if SIMULATE_TRADES:
            print(f"🧪 Simulated trade → Buying {token['symbol']} on {token['chain']} for {TRADE_BUDGET_USD} ETH")
            summary = f"""
📊 Dry Run Summary:
Token: {token['symbol']}
Chain: {token['chain']}
Amount: {TRADE_BUDGET_USD} ETH
Status: SIMULATED
RPC: {provider.web3.provider.endpoint_uri}
"""
            print(summary)
        else:
            send_trade_summary(token)

    except Exception as e:
        logging.warning(f"⚠️ Trade simulation failed for {token.get('name', 'Unknown')}: {e}")

        # 🧠 Main runner entry — used by launcher
def run_trading_bot(simulate=True):
    global SIMULATE_TRADES
    SIMULATE_TRADES = simulate

    print("🔁 MemeBot scanning tokens...")
    tokens_to_evaluate = [
        {
            "name": "TESTINU",
            "symbol": "TINU",
            "address": "0x0000000000000000000000000000000000000000",
            "chain": "Ethereum",
            "token_price_usd": 0.003
        },
        {
            "name": "BASEFLOKI",
            "symbol": "BFLOKI",
            "address": "0x0000000000000000000000000000000000000001",
            "chain": "Base",
            "token_price_usd": 0.004
        }
        # ➕ Add real tokens here later
    ]

    for token in tokens_to_evaluate:
        decision = predict_success(token)
        if decision["should_trade"]:
            logging.info(f"🎯 Triggering trade for {token['name']}")
            simulate_trade(token)
        else:
            logging.info(f"❌ Skipped {token['name']} — ROI: {decision['roi']} | Risk: {decision['risk']}")
