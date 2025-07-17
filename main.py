from flask import Flask, request, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
DEFAULT_CHAT_MODEL = "openai/gpt-3.5-turbo"
DEFAULT_IMAGE_MODEL = "modelslab/revAnimated"

# 🧠 TEXT REPLY
def chat_reply(message):
    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEFAULT_CHAT_MODEL,
            "messages": [
                {"role": "system", "content": "You're a flirty, spicy chatbot."},
                {"role": "user", "content": message},
            ],
        },
    )
    data = response.json()
    return data["choices"][0]["message"]["content"]

# 🎨 IMAGE GENERATION
def generate_image(prompt):
    response = requests.post(
        "https://openrouter.ai/api/v1/images/generations",
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": DEFAULT_IMAGE_MODEL,
            "prompt": prompt,
            "size": "512x768",
            "num_images": 1,
        },
    )

    data = response.json()
    return data["data"][0]["url"] if "data" in data else None

# 📥 TELEGRAM WEBHOOK HANDLER
@app.route("/", methods=["POST"])
def handle_message():
    try:
        data = request.get_json()
        message = data["message"]
        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        # 🔍 Check if it's an /image command
        if text.lower().startswith("/image"):
            prompt = text.replace("/image", "").strip()
            if not prompt:
                send_message(chat_id, "Please include a prompt, e.g. `/image a sexy anime girl`")
                return jsonify({"ok": True})

            image_url = generate_image(prompt)
            if image_url:
                send_photo(chat_id, image_url)
            else:
                send_message(chat_id, "❌ Failed to generate image. Try again.")
            return jsonify({"ok": True})

        # ✨ Regular chat reply
        reply = chat_reply(text)
        send_message(chat_id, reply)

    except Exception as e:
        print("Error:", e)
    return jsonify({"ok": True})

# 📨 SEND TEXT MESSAGE
def send_message(chat_id, text):
    requests.post(
        f"{TELEGRAM_API_URL}/sendMessage",
        json={"chat_id": chat_id, "text": text}
    )

# 🖼️ SEND IMAGE
def send_photo(chat_id, photo_url):
    requests.post(
        f"{TELEGRAM_API_URL}/sendPhoto",
        json={"chat_id": chat_id, "photo": photo_url}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


