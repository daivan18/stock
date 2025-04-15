from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from utils.stock_price import get_realtime_price
from db import get_connection
from datetime import datetime
import requests
import os

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# ==== LINE Messaging API Token ====
LINE_CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_TOKEN")
YOUR_USER_ID = os.getenv("LINE_USER_ID")

class Stock:
    def __init__(self, symbol, price, add_price, change_percent=None, gap_percent=0):  # 設定預設值為 0
        self.symbol = symbol
        self.price = float(price)
        self.add_price = float(add_price)
        self.change_percent = change_percent
        self.gap_percent = gap_percent if gap_percent is not None else 0  # 確保 gap_percent 不為 None


    def calculate_change_percent(self):
        # 模擬 2% 漲幅，實際情況可以從API獲取
        self.change_percent = round((self.price - self.price * 0.98) / self.price * 100, 2)  # 假設漲了2%

    def calculate_gap_percent(self):
        if self.add_price > 0:
            self.gap_percent = round((self.add_price - self.price) / self.price * 100, 2)
        else:
            self.gap_percent = None

@app.get("/", response_class=HTMLResponse)
async def read_stocks(request: Request):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT symbol, target_price FROM watchlist")
    rows = cursor.fetchall()

    stocks = []
    for row in rows:
        symbol, add_price = row
        price = get_realtime_price(symbol) 
        stock = Stock(symbol, price, add_price)
        stock.calculate_change_percent()
        stock.calculate_gap_percent()
        stocks.append(stock)

    conn.close()
    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": stocks})

@app.post("/add_stock")
async def add_stock(request: Request, symbol: str = Form(...)):
    symbol = symbol.strip().upper()

    try:
        price = get_realtime_price(symbol)
        if price == -1:
            print(f"[錯誤] 無法取得 {symbol} 的股價，新增失敗")
            return RedirectResponse("/", status_code=302)

        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO watchlist (symbol, target_price, updated_by, updated_at)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (symbol) DO NOTHING;
        """, (symbol, 0, "system", datetime.now()))

        conn.commit()
        conn.close()

        print(f"[成功] 已新增 {symbol}，現價為 {price}")
        return RedirectResponse("/", status_code=302)

    except Exception as e:
        print(f"[例外錯誤] 新增 {symbol} 時發生錯誤：{e}")
        return RedirectResponse("/", status_code=302)

@app.post("/delete_stock", response_class=HTMLResponse)
async def delete_stock(request: Request, symbol: str = Form(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM watchlist WHERE symbol = %s", (symbol,))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=302)

@app.post("/set_add_price")
async def set_add_price(symbol: str = Form(...), add_price: float = Form(...)):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE watchlist
        SET target_price = %s, updated_by = %s, updated_at = %s
        WHERE symbol = %s
    """, (add_price, "system", datetime.now(), symbol))
    conn.commit()
    conn.close()
    return RedirectResponse("/", status_code=302)

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

@app.post("/notify") 
async def notify_test(symbol: str = Form(...)):
    send_line_message(f"[測試] 股票 {symbol} 推播成功！")
    return RedirectResponse("/", status_code=302)
