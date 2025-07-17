from flask import Flask, request
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
BOT_USERNAME = os.getenv("BOT_USERNAME", "SpicyChatBot")  # optional

TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

@app.route("/", methods=["POST"])
def handle_message():
    data = request.get_json()
    print("Incoming:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        user_message = data["message"].get("text", "")

        reply_text = generate_reply(user_message)

        send_message(chat_id, reply_text)

    return "OK"

def generate_reply(user_input):
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": "mistral-7b",  # or try "openchat"
                "messages": [{"role": "user", "content": user_input}],
                "max_tokens": 1000,  # reduced to prevent error
                "temperature": 0.8
            }
        )

        response.raise_for_status()
        result = response.json()
        reply = result["choices"][0]["message"]["content"]
        return reply

    except Exception as e:
        print("Text reply error:", e)
        return "Sorry, something went wrong. Try again later."

def send_message(chat_id, text):
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    response = requests.post(TELEGRAM_API_URL, json=payload)
    print("Telegram send status:", response.status_code)

if __name__ == "__main__":
    app.run(debug=True)





