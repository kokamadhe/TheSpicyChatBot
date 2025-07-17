import os
import requests
from flask import Flask, request
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
BOT_URL = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}"

# Your OpenRouter API key here
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_IMAGE_URL = "https://openrouter.ai/api/v1/chat/completions"

app = Flask(__name__)

def send_message(chat_id, text):
    requests.post(f"{BOT_URL}/sendMessage", json={
        "chat_id": chat_id,
        "text": text
    })

def send_photo(chat_id, photo_url):
    requests.post(f"{BOT_URL}/sendPhoto", json={
        "chat_id": chat_id,
        "photo": photo_url
    })

def generate_image(prompt):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    json_data = {
        "model": "openai/dall-e-2",  # or another supported model
        "messages": [
            {"role": "user", "content": f"Generate an image: {prompt}"}
        ],
        "stream": False
    }

    try:
        response = requests.post(OPENROUTER_IMAGE_URL, headers=headers, json=json_data)
        response.raise_for_status()
        data = response.json()
        # The response will have image URL inside choices -> message -> content or output
        # Adjust this part according to OpenRouter image API docs or response format:
        image_url = None
        if "choices" in data and len(data["choices"]) > 0:
            content = data["choices"][0]["message"]["content"]
            # The content should be the image URL or JSON containing URL
            # If just URL:
            image_url = content.strip()
        return image_url
    except Exception as e:
        print("Image generation error:", e)
        return None

@app.route("/", methods=["POST"])
def webhook():
    data = request.get_json()
    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")

        if text == "/start":
            send_message(chat_id, "Hello! Use /image <prompt> to generate an AI image.")
        elif text.startswith("/image"):
            prompt = text.replace("/image", "").strip()
            if not prompt:
                send_message(chat_id, "Please provide an image prompt.\nExample:\n/image a beautiful sunset")
            else:
                send_message(chat_id, "Generating your image, please wait...")
                image_url = generate_image(prompt)
                if image_url:
                    send_photo(chat_id, image_url)
                else:
                    send_message(chat_id, "Sorry, failed to generate image. Please try again later.")
        else:
            send_message(chat_id, f"💬 You said: {text}")
    return "ok"

