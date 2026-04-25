from flask import Flask, request
import requests
import os
from google import genai

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
client = genai.Client(api_key=os.environ.get("GEMMA_API_KEY"))

@app.route("/", methods=["GET"])
def index():
    return "OK", 200

@app.route("/callback", methods=["GET", "POST"])
def callback():
    if request.method == "GET":
        return "OK", 200

    body = request.get_json(force=True, silent=True)
    if not body or "events" not in body:
        return "OK", 200

    for event in body["events"]:
        if event["type"] == "message" and event["message"]["type"] == "text":
            reply_token = event["replyToken"]
            user_text = event["message"]["text"]

            try:
                response = client.models.generate_content(
                    model="gemini-1.5-flash",
                    contents=user_text
                )
                reply_text = response.text
            except Exception as e:
                reply_text = "エラーが発生しました。"
                print(f"Gemini error: {e}")

            requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                json={
                    "replyToken": reply_token,
                    "messages": [{"type": "text", "text": reply_text}]
                }
            )
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
