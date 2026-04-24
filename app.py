 from flask import Flask, request                                                                                        import requests                                                                                                         import os                                                                                                             
  app = Flask(__name__)                                                                                                 
  ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")

  @app.route("/callback", methods=["POST"])                                                                               def callback():
      body = request.json                                                                                                     if not body or "events" not in body:
          return "OK"
                                                                                                                              for event in body["events"]:
          if event["type"] == "message" and event["message"]["type"] == "text":                                                       reply_token = event["replyToken"]                                                                                       text = event["message"]["text"]
                                                                                                                                      requests.post(
                  "https://api.line.me/v2/bot/message/reply",
                  headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},                                                                    json={
                      "replyToken": reply_token,                                                                                              "messages": [{"type": "text", "text": text}]
                  }                                                                                                                   )
      return "OK"

  if __name__ == "__main__":                                                                                                  app.run()
