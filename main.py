import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{BOT_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Hello! I am your Telegram bot.")
        else:
            send_message(chat_id, f"💬 You said: {text}")

    return "ok"
