# main.py

from fastapi import FastAPI
from redis_client import set_cache, get_cache

app = FastAPI()

@app.get("/")
def root():
    return {"message": "Hello, stock project!"}

@app.get("/cache/{symbol}")
def cache_stock(symbol: str):
    # 模擬存入股價
    price = "123.45"
    set_cache(symbol, price)
    return {"cached": True, "symbol": symbol, "price": price}

@app.get("/price/{symbol}")
def get_price(symbol: str):
    price = get_cache(symbol)
    if price:
        return {"symbol": symbol, "cached_price": price}
    else:
        return {"symbol": symbol, "cached_price": None, "message": "No cache found"}
