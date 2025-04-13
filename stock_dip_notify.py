import redis
import requests
import os
from utils.stock_price import get_realtime_price

# ==== Redis 連線設定 ====
redis_client = redis.StrictRedis(host="localhost", port=6379, db=0, decode_responses=True)

# ==== LINE Messaging API Token ====
LINE_CHANNEL_ACCESS_TOKEN = "65UAgtUyFgoSJ1FrrRqYuyiT5ceBOD3uZnbyUNpCRvD4HlTTqpMFi5k4sQKRQOre+bdUHZ+VvgGV/gHezxfe8GELUhww0NeNLxtkzqMIKg/4qnirC1aD1JdwjHk+opw2c/sUiY6703Ex3gsiZHMB8QdB04t89/1O/w1cDnyilFU="
YOUR_USER_ID = "你的 LINE 使用者 ID"  # ← 請手動填入！

# ==== 使用 LINE Messaging API 傳訊息 ====
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

# ==== 主邏輯：檢查股票是否到價並通知 ====
def check_and_notify():
    notify_message = ""

    keys = redis_client.keys("stock:*")

    for key in keys:
        stock_data = redis_client.hgetall(key)

        try:
            symbol = stock_data.get("symbol")
            add_price = float(stock_data.get("add_price", 0))
            current_price = get_realtime_price(symbol)

            print(f"{symbol} 現價: {current_price} ➜ 加碼價: {add_price}")

            if add_price > 0 and current_price <= add_price:
                notify_message += f"\n📉 {symbol} 跌破 {add_price}（現價 {current_price}）"

        except Exception as e:
            print(f"[錯誤] 處理 {key} 時發生例外：{e}")

    if notify_message:
        send_line_message("⚠️ 到價通知：" + notify_message)
    else:
        print("目前沒有股票跌到加碼價")

if __name__ == "__main__":
    check_and_notify()
