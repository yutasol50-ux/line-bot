from flask import Flask, request
import requests
import os
import json
import base64
import cohere

app = Flask(__name__)

ACCESS_TOKEN = os.environ.get("CHANNEL_ACCESS_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO  = "yutasol50-ux/line-news-bot"
SCORES_PATH  = "scores.json"

co = cohere.ClientV2(api_key=os.environ.get("COHERE_API_KEY"))


# ====== GitHub経由でscores.jsonを読み書き ======

def github_get_scores() -> tuple[dict | None, str | None]:
    resp = requests.get(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SCORES_PATH}",
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
        timeout=10,
    )
    if resp.status_code != 200:
        return None, None
    data = resp.json()
    content = json.loads(base64.b64decode(data["content"]).decode("utf-8"))
    return content, data["sha"]


def github_put_scores(scores: dict, sha: str) -> bool:
    content_b64 = base64.b64encode(
        json.dumps(scores, ensure_ascii=False, indent=2).encode("utf-8")
    ).decode("utf-8")
    resp = requests.put(
        f"https://api.github.com/repos/{GITHUB_REPO}/contents/{SCORES_PATH}",
        headers={"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"},
        json={"message": "Update scores via LINE feedback", "content": content_b64, "sha": sha},
        timeout=10,
    )
    return resp.status_code in (200, 201)


def update_score(label: str, delta: float) -> str:
    scores, sha = github_get_scores()
    if scores is None:
        return "スコア取得に失敗しました"

    current = scores["labels"].get(label)
    if current is None:
        # 新しいラベルは初期値5で追加
        scores["labels"][label] = 5.0
        current = 5.0

    new_score = round(min(10.0, max(0.0, current + delta)), 2)
    scores["labels"][label] = new_score

    if github_put_scores(scores, sha):
        direction = "↑" if delta > 0 else "↓"
        return f"{label} {direction} {current:.1f} → {new_score:.1f}"
    return "スコア保存に失敗しました"


# ====== LINE返信 ======

def reply_line(reply_token: str, text: str) -> None:
    requests.post(
        "https://api.line.me/v2/bot/message/reply",
        headers={"Authorization": f"Bearer {ACCESS_TOKEN}"},
        json={"replyToken": reply_token, "messages": [{"type": "text", "text": text}]},
        timeout=10,
    )


# ====== ルーティング ======

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
        if event["type"] != "message" or event["message"]["type"] != "text":
            continue

        reply_token = event["replyToken"]
        user_text = event["message"]["text"].strip()

        print(f"USER_ID: {event['source']['userId']} | MSG: {user_text}")

        # 👍/👎 フィードバック処理（LIKE:AI / BAD:AI）
        if user_text.startswith("LIKE:"):
            label = user_text[5:].strip()
            delta = 1.0
            result = update_score(label, delta)
            reply_line(reply_token, f"👍 {result}")
            continue

        if user_text.startswith("BAD:"):
            label = user_text[4:].strip()
            delta = -1.0
            result = update_score(label, delta)
            reply_line(reply_token, f"👎 {result}")
            continue

        # 通常チャット → Cohereで返答
        try:
            response = co.chat(
                model="command-r-plus-08-2024",
                messages=[{"role": "user", "content": user_text}],
            )
            reply_text = response.message.content[0].text
        except Exception as e:
            reply_text = "エラーが発生しました。"
            print(f"Cohere error: {e}")

        reply_line(reply_token, reply_text)

    return "OK", 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
