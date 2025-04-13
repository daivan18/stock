from fastapi import FastAPI, Request
import uvicorn
from dotenv import load_dotenv
import os
import json
import requests  # 加入 requests 模組

# 載入 .env 檔案
load_dotenv()

# 讀取 LINE Channel Access Token
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

app = FastAPI()

def reply_message(reply_token: str, text: str):
    url = "https://api.line.me/v2/bot/message/reply"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "replyToken": reply_token,
        "messages": [{"type": "text", "text": text}]
    }
    response = requests.post(url, headers=headers, json=payload)  # 使用 requests 發送請求
    print(f"[LINE] 回覆狀態：{response.status_code} - {response.text}")

@app.post("/webhook")
async def line_webhook(req: Request):
    body = await req.body()
    data = json.loads(body)
    print(f"[LINE] 收到訊息：{json.dumps(data, indent=2)}")

    events = data.get("events", [])
    for event in events:
        if event["type"] == "message":
            user_message = event["message"]["text"]
            reply_token = event["replyToken"]
            reply_message(reply_token, f"你說的是：{user_message}")
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run("webhook:app", host="0.0.0.0", port=8000, reload=True)



# uvicorn webhook:app --reload
