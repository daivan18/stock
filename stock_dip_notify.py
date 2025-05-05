import os
import requests
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from utils.stock_price import get_realtime_price
from sqlalchemy.engine.url import make_url

# 載入 .env 檔案中的環境變數
load_dotenv()

# ==== PostgreSQL 連線設定 ====
DATABASE_URL = os.getenv("DATABASE_URL")

url = make_url(DATABASE_URL)
engine = create_engine(url, connect_args={"sslmode": "require"})
# engine = create_engine(DATABASE_URL)

# ==== LINE Messaging API Token ====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
YOUR_USER_ID = os.getenv("LINE_USER_ID")

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

    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT symbol, target_price FROM watchlist"))

            for row in result:
                symbol = row.symbol
                target_price = float(row.target_price)

                try:
                    current_price = get_realtime_price(symbol)
                    print(f"{symbol} 現價: {current_price} ➜ 加碼價: {target_price}")

                    if target_price > 0 and current_price <= target_price:
                        notify_message += f"\n📉 {symbol} 跌破 {target_price}（現價 {current_price}）"

                except Exception as e:
                    print(f"[錯誤] 取得 {symbol} 現價失敗：{e}")

    except Exception as e:
        print(f"[錯誤] 資料庫連線或查詢失敗：{e}")
        send_line_message(f"❌ 無法連接資料庫：{e}")
        return

    if notify_message:
        send_line_message("⚠️ 到價通知：" + notify_message)
    else:
        print("目前沒有股票跌到加碼價")


if __name__ == "__main__":
    check_and_notify()
