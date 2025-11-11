# Créer un nouveau fichier propre
cat > backend/analyze_and_publish_clean.py << 'EOF'
# backend/analyze_and_publish.py
import os
import json
import requests
from datetime import datetime

def send_telegram_message(message):
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    chat_id = os.getenv('TELEGRAM_CHAT_ID')
    
    if not token or not chat_id:
        print("Telegram not configured (token or chat missing). Skipping send.")
        return False
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {'chat_id': chat_id, 'text': message, 'parse_mode': 'HTML'}
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("✅ Telegram message sent")
            return True
        else:
            print(f"❌ Telegram error: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Telegram send error: {e}")
        return False

def main():
    print("Start SPOREX pipeline...")
    
    # Simulation de données
    signals = 3
    data = {"signals": signals}
    
    with open('matches_today.json', 'w') as f:
        json.dump(data, f)
    
    print(f"Wrote matches_today.json signals: {signals}")
    
    if signals > 0:
        message = f"🚨 {signals} signals detected!"
        send_telegram_message(message)

if __name__ == "__main__":
    main()
EOF

# Tester le nouveau fichier
python backend/analyze_and_publish_clean.py
