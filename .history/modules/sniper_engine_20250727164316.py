# 🎯 Real-time sniper engine
def execute_sniper_loop(roc_threshold=5.0):
    global total_sol_spent, last_trade_time

    now = time.time()

    if now - last_trade_time < MIN_COOLDOWN_SECONDS:
        logger.info("⏳ Cooldown active.")
        return

    if is_sniper_paused():
        logger.info("⏸️ Sniper paused.")
        time.sleep(300)
        return

    sol_price = fetch_sol_usd_price()
    if not sol_price:
        logger.warning("⚠️ SOL price unavailable.")
        return

    wallet_sol = get_sol_balance(wallet.pubkey())
    wallet_eth = 0.0  # ETH logic placeholder

    market_data = {
        "price_change_pct": 4.2,
        "volume_change_pct": 3.8
    }

    trade_decision = execute_trade_logic(
        wallet_sol_balance=wallet_sol,
        wallet_eth_balance=wallet_eth,
        last_trade_time=last_trade_time,
        current_time=now,
        daily_sol_spent=total_sol_spent,
        market_data=market_data
    )

    if trade_decision["action"] == "skip":
        logger.info(f"⏳ Trade skipped: {trade_decision['reason']}")
        return

    amount_sol = trade_decision["sol_allocation"]
    slippage = trade_decision["slippage_tolerance"]
    aggressiveness = trade_decision["aggressiveness"]

    logger.info(f"💡 Trade Aggressiveness: {aggressiveness}")

    if wallet_sol < LOW_BALANCE_ALERT or wallet_sol < amount_sol + 0.01:
        logger.warning(f"🛑 Low SOL balance: {wallet_sol}")
        return

    pairs = fetch_new_pairs()
    passed_count = 0

    for token in pairs:
        try:
            symbol = token["symbol"]
            address = token["address"]
            logger.info(f"🔍 Evaluating {symbol} ({address})")

            token["roc_30s"] = calculate_roc(address)
            logger.info(f"📈 ROC: {token['roc_30s']}%")

            if token["roc_30s"] < roc_threshold:
                logger.info("⛔ ROC too low.")
                continue

            token["age_seconds"] = get_token_age(address, RUGCHECK_API_KEY)
            creator = get_creator_wallet(address, RUGCHECK_API_KEY)
            token["creator_wallet"] = creator
            token["creator_score"] = get_creator_history_score(creator)

            if token["creator_score"] < 30:
                logger.info("⛔ Poor creator score.")
                continue

            if address in SAFE_OVERRIDES:
                token["rug_score"] = 0.0
                logger.info("✅ Safe override applied.")

            token_data = check_token_security(address, api_key=RUGCHECK_API_KEY)
            if token_data:
                if not is_good_contract(token_data):
                    logger.info("⛔ Contract flagged.")
                    continue
                if not is_bundled_supply(token_data):
                    logger.info("⛔ Supply bundle issues.")
                    continue

            if token["liquidity_usd"] < 15000:
                logger.info("⛔ Liquidity too low.")
                continue

            if not should_allow_rug(token) or not should_buy(token):
                logger.info("⛔ Strategy rejected token.")
                continue

            if total_sol_spent + amount_sol > MAX_DAILY_SOL:
                logger.info("🚫 Daily spend limit reached.")
                break

            tx_link = buy_token_solana(address, amount_sol, wallet)
            outcome = "Success" if tx_link else "Failed"

            log_trade(symbol, "solana", amount_sol, creator, tx_link or "-", outcome)
            update_creator_score(creator, outcome)

            if tx_link:
                logger.info(f"✅ Trade successful: {tx_link}")
                send_trade_alert(symbol, "solana", tx_link)
                total_sol_spent += amount_sol
                last_trade_time = time.time()
                passed_count += 1
            else:
                logger.warning(f"🚫 Trade failed for {symbol}")

        except Exception as e:
            logger.error(f"🔥 Scan failed for {symbol}: {e}")
            continue

        time.sleep(2)

    if passed_count == 0:
        send_message("⚠️ No tokens passed sniper filters.")
