# stock_logic.py
from db import get_connection
from utils.stock_price import get_realtime_price
from datetime import datetime
from fastapi.responses import RedirectResponse

class Stock:
    def __init__(self, symbol, price, add_price, change_percent=None, gap_percent=0):
        self.symbol = symbol
        self.price = float(price)
        self.add_price = float(add_price)
        self.change_percent = change_percent
        self.gap_percent = gap_percent if gap_percent is not None else 0

    def calculate_change_percent(self):
        self.change_percent = round((self.price - self.price * 0.98) / self.price * 100, 2)

    def calculate_gap_percent(self):
        if self.add_price > 0:
            self.gap_percent = round((self.add_price - self.price) / self.price * 100, 2)
        else:
            self.gap_percent = None

def get_stocks_from_db(username):
    print("🔍 進入 get_stocks_from_db()")
    stocks = []

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT symbol, target_price FROM watchlist WHERE username = %s", (username,))
        rows = cursor.fetchall()
        conn.close()
        print(f"✅ 資料庫讀取成功，資料筆數：{len(rows)}")

        for row in rows:
            symbol, add_price = row
            try:
                price = get_realtime_price(symbol)
                if price == -1:
                    print(f"⚠️ 無法取得 {symbol} 的即時股價，略過")
                    continue

                stock = Stock(symbol, price, add_price)
                stock.calculate_change_percent()
                stock.calculate_gap_percent()
                stocks.append(stock)
            except Exception as e:
                print(f"❌ 處理股票 {symbol} 發生錯誤：{e}")

    except Exception as e:
        print(f"❌ 資料庫連線或查詢錯誤：{e}")

    return stocks

def add_stock_to_db(request, symbol, username):
    symbol = symbol.strip().upper()

    try:
        conn = get_connection()
        cursor = conn.cursor()

        # 檢查是否已存在
        cursor.execute("""
            SELECT 1 FROM watchlist WHERE username = %s AND symbol = %s
        """, (username, symbol))
        exists = cursor.fetchone()

        if exists:
            conn.close()
            print(f"[提示] 股票 {symbol} 已存在使用者 {username} 的清單中")
            return RedirectResponse(f"/stocks?msg=exists&symbol={symbol}", status_code=302)

        # 若不存在，新增
        cursor.execute("""
            INSERT INTO watchlist (symbol, target_price, username, updated_by, updated_at)
            VALUES (%s, %s, %s, %s, %s)
        """, (symbol, 0, username, "system", datetime.now()))

        conn.commit()
        conn.close()
        print(f"[成功] 已新增 {symbol} 到 {username} 的清單中")
        return RedirectResponse(f"/stocks?msg=added&symbol={symbol}", status_code=302)

    except Exception as e:
        print(f"[例外錯誤] 新增 {symbol} 時發生錯誤：{e}")
        return RedirectResponse(f"/stocks?msg=error&symbol={symbol}&error={str(e)}", status_code=302)

def delete_stock_from_db(symbol, username):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM watchlist WHERE symbol = %s AND username = %s", (symbol, username))
        conn.commit()
        conn.close()
        print(f"[成功] 已刪除 {symbol} (使用者：{username})")

        return RedirectResponse(f"/stocks?msg=deleted&symbol={symbol}", status_code=302)

    except Exception as e:
        print(f"[例外錯誤] 刪除 {symbol} 時發生錯誤：{e}")
        return RedirectResponse(f"/stocks?msg=error&symbol={symbol}&error={str(e)}", status_code=302)

def update_add_price(symbol, add_price, username):
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE watchlist
            SET target_price = %s, updated_by = %s, updated_at = %s
            WHERE symbol = %s AND username = %s
        """, (add_price, "system", datetime.now(), symbol, username))
        conn.commit()
        conn.close()
        print(f"[成功] 已更新 {symbol} 的加碼價為 {add_price} (使用者：{username})")

        return RedirectResponse(f"/stocks?msg=price_set&symbol={symbol}&price={add_price}", status_code=302)

    except Exception as e:
        print(f"[例外錯誤] 更新 {symbol} 的加碼價時發生錯誤：{e}")
        return RedirectResponse(f"/stocks?msg=error&symbol={symbol}&error={str(e)}", status_code=302)