import yfinance as yf

def get_realtime_price(symbol: str) -> float:
    try:
        ticker = yf.Ticker(symbol)
        price = ticker.fast_info["lastPrice"]
        return round(price, 2)
    except Exception as e:
        print(f"[get_realtime_price 錯誤] {symbol} 查詢失敗：{e}")
        return -1
