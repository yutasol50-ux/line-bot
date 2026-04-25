from flask import Flask, request
import requests
import os
from huggingface_hub import InferenceClient

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
hf_client = InferenceClient(api_key=os.environ.get("HF_TOKEN"))

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
                result = hf_client.chat.completions.create(
                    model="HuggingFaceH4/zephyr-7b-beta",
                    messages=[{"role": "user", "content": user_text}],
                    max_tokens=500
                )
                reply_text = result.choices[0].message.content
            except Exception as e:
                reply_text = "エラーが発生しました。"
                print(f"HF error: {e}")

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
