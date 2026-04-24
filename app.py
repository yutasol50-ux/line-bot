from flask import Flask, request
import requests
import os

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

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
            text = event["message"]["text"]

            res = requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
                json={
                    "replyToken": reply_token,
                    "messages": [{"type": "text", "text": text}]
                }
            )
            print(f"LINE API response: {res.status_code} {res.text}")
    return "OK", 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
