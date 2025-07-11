# alerts/telegram.py

def send_message(msg):
    print(f"📲 Sending message to Telegram: {msg}")
    # 🔧 Replace with actual telegram bot logic later

def send_roi_alert(token):
    msg = f"""
📈 ROI Potential Alert
Token: {token['name']}
Chain: {token['chain']}
Risk: {token['risk_score']}/100
Buzz: {token['buzz_score']}
Estimated Output for $1: {token['estimated_return']}
📊 ROI Score: {token['roi_score']}/90
"""
    bot.send_message(chat_id=CHAT_ID, text=msg)