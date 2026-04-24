from flask import Flask, request
import requests

app = Flask(__name__)

ACCESS_TOKEN = H/sP3dpwb2xL0hoJBGgTWWYpE3PExAz0JENYd4Rr7o/ux7298iaTGojQnDpGwyDzvsMZIW800PEzNzD1rx/PcLfls2JYSBF1Rn1T9Vga8Y+2qqfrhnb9oMIf7zYjnfGco6n7RWhYjpXaxpqlp16mdgdB04t89/1O/w1cDnyilFU=

@app.route("/callback", methods=["POST"])
def callback():
    events = request.json["events"]

    for event in events:
        if event["type"] == "message":
            reply_token = event["replyToken"]
            text = event["message"]["text"]

            requests.post(
                "https://api.line.me/v2/bot/message/reply",
                headers={
                    "Authorization": f"Bearer {ACCESS_TOKEN}"
                },
                json={
                    "replyToken": reply_token,
                    "messages": [{"type": "text", "text": text}]
                }
            )
    return "OK"
