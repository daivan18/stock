# 建立Render 資料庫的 watchlist 資料表
import os
from db import get_connection
from dotenv import load_dotenv

load_dotenv()  # 確保在這裡也調用一次，以防萬一

print("DB_HOST:", os.getenv("DB_HOST"))
print("DB_PORT:", os.getenv("DB_PORT"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("DB_USER:", os.getenv("DB_USER"))
print("DB_PASSWORD:", os.getenv("DB_PASSWORD"))

def create_table():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            target_price NUMERIC(10, 2) NOT NULL,
            updated_by VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    cur.close()
    conn.close()
    print("✅ 資料表建立完成")

if __name__ == "__main__":
    create_table()
