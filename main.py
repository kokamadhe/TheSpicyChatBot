from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

app = Flask(__name__)

def generate_reply(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "openchat/openchat-7b",
                "messages": [
                    {"role": "system", "content": "You are a flirty, spicy girlfriend. Respond in a seductive and cheeky way."},
                    {"role": "user", "content": user_input}
                ],
                "max_tokens": 500,
                "temperature": 0.9
            }
        )
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        print("Text reply error:", e)
        return "Oops 😳 something went wrong with my AI brain..."

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    print("Telegram send status:", response.status_code, response.text)

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    print("Incoming:", data)

    if "message" in data and "text" in data["message"]:
        chat_id = data["message"]["chat"]["id"]
        user_input = data["message"]["text"]
        reply = generate_reply(user_input)
        send_message(chat_id, reply)

    return "ok"

@app.route("/", methods=["GET"])
def home():
    return "🤖 Spicy AI Telegram Bot is running!"








