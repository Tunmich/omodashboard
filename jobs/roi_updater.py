import csv
from utils.roi_evaluator import fetch_token_price_dexscreener, calculate_roi

def update_trade_rois():
    path = "logs/trades.csv"
    updated_rows = []

    with open(path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["Estimated_Payout"] == "Pending" and row["Status"] == "Success":
                ca = row["Tx_Link"].split("/")[-1]  # 🔎 Extract CA if embedded
                chain = row["Chain"].lower()
                buy_amount = float(row["Amount_ETH"]) * 1700  # 🧮 Rough ETH price — can refine

                price = fetch_token_price_dexscreener(ca, chain)
                roi = calculate_roi(buy_amount, price) if price else "?"
                row["Estimated_Payout"] = f"{roi}%"

            updated_rows.append(row)

    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=updated_rows[0].keys())
        writer.writeheader()
        writer.writerows(updated_rows)