"""
line_notify.py

此模組提供測試Line官方帳號發送訊息。
主要功能：
- 使用 LINE Bot 的 Push Message API 發送訊息。
- 從環境變數中讀取 LINE 的存取權杖與使用者 ID。

環境變數：
- LINE_CHANNEL_TOKEN: LINE Bot 的存取權杖。
- LINE_USER_ID: 接收訊息的使用者 ID。

函式：
- send_line_message(message): 發送文字訊息給指定的 LINE 使用者。
"""
import os
import requests

LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
YOUR_USER_ID = os.getenv("LINE_USER_ID")

def send_line_message(message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": YOUR_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"LINE 回應：{r.status_code} - {r.text}")