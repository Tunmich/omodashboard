import csv, os, datetime

LOG_FILE = "logs/trades.csv"
FIELDNAMES = ["Timestamp", "Token", "Chain", "Amount_ETH", "Estimated_Payout", "Tx_Link", "Status"]

def log_trade(token, chain, amount_eth, payout_estimate, tx_link, status="Success"):
    timestamp = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    entry = {
        "Timestamp": timestamp,
        "Token": token,
        "Chain": chain,
        "Amount_ETH": amount_eth,
        "Estimated_Payout": payout_estimate,"pending"

        "Tx_Link": tx_link,
        "Status": "Success"
    }

    # 🛡️ Ensure log file exists
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
            writer.writeheader()

    log_trade(symbol, chain, 0.01, "-", "-", status="Failed")

    # ✍️ Append log entry
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=FIELDNAMES)
        writer.writerow(entry)

try:
    config = get_router_for_chain(chain)  # Ethereum or BNB
except ValueError:
    logging.warning(f"⚠️ Skipping unknown chain: {chain.upper()}")
    continue

web3 = config["web3"]
router = config["router"]
weth_address = config["weth"]

if not simulate_sell(ca):
    logging.info(f"🔒 {symbol} on {chain.upper()} failed sell check. Skipping.")
    continue

tx_link = buy_token(
    token_address=ca,
    amount_eth=0.01,
    slippage_pct=0.5,
    web3=web3,
    router=router,
    weth_address=weth_address
)

if not tx_link:
    logging.warning(f"🚫 Trade for {symbol} on {chain.upper()} failed. Skipping.")
    continue