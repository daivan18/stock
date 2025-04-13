from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import redis
from utils.stock_price import get_realtime_price
from fastapi.responses import RedirectResponse

app = FastAPI()

templates = Jinja2Templates(directory="templates")

r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)

class Stock:
    def __init__(self, symbol, price, add_price):
        self.symbol = symbol
        self.price = price
        self.add_price = add_price

@app.get("/", response_class=HTMLResponse)
async def read_stocks(request: Request):
    stocks = []
    for key in r.keys("stock:*"):
        data = r.hgetall(key)
        stock = Stock(data['symbol'], data['price'], data['add_price'])
        stocks.append(stock)
    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": stocks})

@app.post("/add_stock")
async def add_stock(request: Request, symbol: str = Form(...)):
    # 去除空白並轉大寫
    symbol = symbol.strip().upper()

    try:
        # 取得即時股價
        price = get_realtime_price(symbol)

        if price == -1:
            print(f"[錯誤] 無法取得 {symbol} 的股價，新增失敗")
            return RedirectResponse("/", status_code=302)

        # 儲存到 Redis，預設加碼價為 0
        r.hmset(f"stock:{symbol}", {
            "symbol": symbol,
            "price": price,
            "add_price": 0
        })

        print(f"[成功] 已新增 {symbol}，現價為 {price}")
        return RedirectResponse("/", status_code=302)

    except Exception as e:
        print(f"[例外錯誤] 新增 {symbol} 時發生錯誤：{e}")
        return RedirectResponse("/", status_code=302)

@app.post("/delete_stock", response_class=HTMLResponse)
async def delete_stock(request: Request, symbol: str = Form(...)):
    r.delete(f"stock:{symbol}")
    return templates.TemplateResponse("stocks.html", {"request": request, "stocks": get_stocks()})

def get_stocks():
    stocks = []
    for key in r.keys("stock:*"):
        data = r.hgetall(key)
        symbol = data['symbol']
        add_price = data.get('add_price', '0')
        
        # 用 Yahoo 抓即時價格
        realtime_price = get_realtime_price(symbol)

        # 寫回 Redis 更新價格（可選）
        r.hset(key, "price", realtime_price)

        stock = Stock(symbol, realtime_price, add_price)
        stocks.append(stock)
    return stocks

# 設定加碼價位
@app.post("/set_add_price")
async def set_add_price(symbol: str = Form(...), add_price: float = Form(...)):
    key = f"stock:{symbol}"
    if r.exists(key):
        r.hset(key, "add_price", add_price)
    return RedirectResponse("/", status_code=302)