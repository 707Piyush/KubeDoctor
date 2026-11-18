
import os
import requests
from dotenv import load_dotenv

# Load the secret token from .env
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if not TOKEN:
    print("Error: Telegram token not found in .env")
    raise SystemExit

# Get messages sent to the bot
url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(url, timeout=15)
response.raise_for_status()

updates = response.json()["result"]

if not updates:
    print("No messages found.")
    print("Open your Telegram bot and send /start.")
    raise SystemExit

# Find the latest chat ID
chat_id = updates[-1]["message"]["chat"]["id"]
print("Your Telegram Chat ID:", chat_id)
# Send a test alert
message = "KubeDoctor is connected successfully! Telegram alerts are working."

send_url = f"https://api.telegram.org/bot{TOKEN}/sendMessage"

result = requests.post(
    send_url,
    data={
        "chat_id": chat_id,
        "text": message
    },
    timeout=15
)

result.raise_for_status()

print("Success! Telegram test message sent.")
