import logging

leaderboard = []  # Can later persist this to a file or database

def update_leaderboard(token):
    entry = {
        "name": token["name"],
        "pl": token.get("estimated_pl", 0),
        "chain": token["chain"]
    }
    leaderboard.append(entry)
    leaderboard.sort(key=lambda x: x["pl"], reverse=True)
    leaderboard[:] = leaderboard[:5]  # Top 5 only

    message = "🏆 Top Trades Leaderboard:\n"
    for idx, t in enumerate(leaderboard, 1):
        icon = "💹" if float(t["pl"]) > 0 else "❌"
        message += f"{idx}. {icon} {t['name']} ({t['chain']}) → P/L: ${t['pl']}\n"

    send_message(message.strip())