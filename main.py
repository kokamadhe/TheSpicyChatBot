import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

app = Flask(__name__)

# Image generation models on OpenRouter (add/remove as you wish)
SUPPORTED_MODELS = [
    "revAnimated",
    "dreamshaper",
    "realisticVision",
    "deliberate",
    "juggernaut",
    "meinamix"
]

def send_message(chat_id, text):
    requests.post(TELEGRAM_API_URL, json={"chat_id": chat_id, "text": text})

def generate_image(model_name, prompt):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o",  # required by OpenRouter even for prompt injection
        "messages": [
            {
                "role": "user",
                "content": f"<|imagegen|><|model:{model_name}|>{prompt}"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        data = response.json()
        # image URL is returned inside the 'content' field of the assistant's reply
        image_url = data['choices'][0]['message']['content'].strip()
        return image_url
    else:
        print("Image generation error:", response.text)
        return None

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()

    if "message" in data and "text" in data["message"]:
        text = data["message"]["text"]
        chat_id = data["message"]["chat"]["id"]

        if text.startswith("/image"):
            parts = text.split(" ", 2)
            if len(parts) < 3:
                send_message(chat_id, "Usage: /image <model> <prompt>")
                return "ok"

            model_name = parts[1]
            prompt = parts[2]

            if model_name not in SUPPORTED_MODELS:
                send_message(chat_id, f"❌ Model not supported. Use one of: {', '.join(SUPPORTED_MODELS)}")
                return "ok"

            send_message(chat_id, "🧠 Generating your image, please wait...")

            image_url = generate_image(model_name, prompt)
            if image_url:
                send_message(chat_id, image_url)
            else:
                send_message(chat_id, "❌ Failed to generate image. Try again later.")
        else:
            # Simple AI chat reply using OpenRouter
            reply = generate_text_reply(text)
            send_message(chat_id, reply)

    return "ok"

def generate_text_reply(user_input):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": "openai/gpt-4o",
        "messages": [
            {"role": "system", "content": "You are a flirty and spicy AI chatbot."},
            {"role": "user", "content": user_input}
        ]
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        print("Text reply error:", response.text)
        return "😓 Sorry, I couldn't respond right now."

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)




