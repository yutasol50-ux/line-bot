                               s
  6 tasks (1 done, 1 in progress, 4 open)
  GitHubの編集画面で Ctrl+A → Delete → 以下を貼る:

  from flask import Flask,trequestal
  import requsits d   a   s        -review
  import os     t   m   m    t
   …          e  d                                                                                                        app = Flask(__name__)
   ─────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
  6 tasks (1 done, 1 in progress, 4 open)                                                                                 ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
                                                                                                                          @app.route("/callback", methods=["POST"])
  def callback(): n   d   t        l
     body = request.json    c           w
     if not bodyoor "events" not in body:
                 d
  6 tasks returne"OK"in progress, 4 open)
                                                                                                                              for event in body["events"]:
         if event["type"]s==─"message"─and─event["message"]["type"]─==─"text":─────────────────────────────────────────
          t  reply_token = event["replyToken"]                                                                                 e      n   c   d    c           w
  6 tasks (1 dtext = event["message"]["text"]

              requests.post(
          t   s  "https://api.line.me/v2/bot/message/reply",                                                                           hea ers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        e      n json={d    c           w──────────────────────────────────────────────────────────────────────────────
             n  o              n    n                                                                                    6 tasks (1 done, 1 i"replyToken": reply_token,
                      "messages": [{"type": "text", "text": text}]
                  }                                                                                                                 )
     return "OK" n   d   t        l────────────────────────────────────────────────────────────────────────────────────
        e      n   c   d    c           w                                                                                if __aame__ == "__main__":    n    n
                 d
  6 taapp.run()ne, 1 in progress, 4 open)
