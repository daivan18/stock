import os
import time
import requests
from collections import defaultdict
from sqlalchemy import create_engine, text
from sqlalchemy.engine.url import make_url
from sqlalchemy.exc import OperationalError
from dotenv import load_dotenv
from utils.stock_price import get_realtime_price

# 載入 .env 環境變數
load_dotenv()

# ==== PostgreSQL 連線設定 ====
DATABASE_URL = os.getenv("DATABASE_URL")
url = make_url(DATABASE_URL)

max_retries = 5
delay = 5
engine = None
for i in range(max_retries):
    try:
        engine = create_engine(url, connect_args={"sslmode": "require"})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ 成功連線到資料庫")
        break
    except OperationalError as e:
        print(f"❌ 第 {i+1} 次連線失敗，{delay} 秒後重試...：{e}")
        time.sleep(delay)
else:
    print("❌ 無法連線到資料庫，請確認 Render 狀態或 IP 白名單")
    exit(1)

# ==== LINE API Token ====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")

def send_line_message(to_user_id, message):
    url = "https://api.line.me/v2/bot/message/push"
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_CHANNEL_ACCESS_TOKEN}"
    }
    payload = {
        "to": to_user_id,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }
    r = requests.post(url, headers=headers, json=payload)
    print(f"➡️ 傳送給 {to_user_id} 的 LINE 回應：{r.status_code} - {r.text}")

def check_and_notify():
    user_notifications = defaultdict(str)  # key: line_id, value: notification msg
    try:
        with engine.connect() as conn:
            
            result = conn.execute(text("""
                SELECT wl.symbol, wl.target_price, users.username, users.line_id
                FROM watchlist wl
                INNER JOIN users
                    ON wl.username = users.username
                WHERE wl.target_price <> 0
                """))

            for row in result:
                user_id = row.line_id
                symbol = row.symbol
                target_price = float(row.target_price)

                try:
                    current_price = get_realtime_price(symbol)
                    print(f"{symbol} 現價: {current_price} ➜ 加碼價: {target_price}")
                    if target_price > 0 and current_price <= target_price:
                        user_notifications[user_id] += f"\n📉 {symbol} 跌破 {target_price}（現價 {current_price}）"
                except Exception as e:
                    print(f"[錯誤] 取得 {symbol} 現價失敗：{e}")
    except Exception as e:
        print(f"[錯誤] 資料庫查詢失敗：{e}")
        return

    # 發送訊息給每位使用者（若有符合條件）
    for user_id, msg in user_notifications.items():
        if msg:
            full_msg = "⚠️ 到價通知：" + msg
            send_line_message(user_id, full_msg)
        else:
            print(f"{user_id} 沒有符合條件的股票")

if __name__ == "__main__":
    check_and_notify()
