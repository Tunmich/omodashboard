import time
import logging
from strategy.trade_decision_engine import should_buy
from modules.solana_executor import execute_sol_trade
from modules.evm_executor import execute_evm_trade  # optional if defined
from scanner.token_feed import fetch_live_tokens

logging.basicConfig(
    filename="logs/scheduler.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

def scan_and_score(token):
    try:
        logging.info(f"🔍 Scanning token → {token.get('symbol')} | {token.get('address')}")
        if should_buy(token):
            logging.info(f"✅ Approved → {token.get('symbol')} | {token.get('address')}")
            chain = token.get("chain")
            if chain == "Solana":
                execute_sol_trade(token.get("address"), token.get("buy_amount"), token.get("wallet"))
            elif chain == "Ethereum":
                execute_evm_trade(token)
        else:
            reasons = []
            buzz = token.get("buzz_score", 0)
            roi = token.get("roi_score", 0)
            risk = token.get("risk_score", 100)
            fusion_boost = token.get("fusion_boost", 0)
            total_score = buzz + roi - risk + fusion_boost

            if buzz < 70:
                reasons.append(f"buzz {buzz} < 70")
            if roi < 65:
                reasons.append(f"ROI {roi} < 65")
            if risk > 35:
                reasons.append(f"risk {risk} > 35")
            if total_score < 120:
                reasons.append(f"total {total_score} < 120")

            reason_text = ", ".join(reasons) if reasons else "Did not meet dynamic strategy rules"
            logging.info(f"❌ Rejected → {token.get('symbol')} | {reason_text}")
    except Exception as e:
        logging.error(f"⚠️ Scoring error for token → {token.get('symbol')}: {e}")

def run_scheduler():
    logging.info("🧠 Scheduler engine starting...")
    while True:
        try:
            candidates = fetch_live_tokens()
            for token in candidates:
                scan_and_score(token)
        except Exception as e:
            logging.error(f"🚨 Scheduler failure: {e}")
        time.sleep(20)
