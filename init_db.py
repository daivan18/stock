import os
import psycopg2
from urllib.parse import urlparse
from dotenv import load_dotenv

load_dotenv()  # 確保在這裡也調用一次，以防萬一

# 確認環境變數
print("DB URL:", os.getenv("DATABASE_URL"))

def get_connection():
    # 解析 DATABASE_URL
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL is not set in the environment variables.")
    
    parsed_url = urlparse(database_url)

    # 透過解析 URL 取得必要的資訊
    conn = psycopg2.connect(
        host=parsed_url.hostname,
        port=parsed_url.port,
        dbname=parsed_url.path[1:],  # 移除開頭的 '/'
        user=parsed_url.username,
        password=parsed_url.password
    )
    
    return conn

def create_tables():
    conn = get_connection()
    cur = conn.cursor()

    # 建立 users 資料表
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            password_hash VARCHAR(100) NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # 建立 watchlist 資料表（已存在則不重建）
    cur.execute("""
        CREATE TABLE IF NOT EXISTS watchlist (
            id SERIAL PRIMARY KEY,
            symbol VARCHAR(10) NOT NULL,
            target_price NUMERIC(10, 2) NOT NULL,
            updated_by VARCHAR(50),
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id INTEGER REFERENCES users(id),
            CONSTRAINT unique_user_symbol UNIQUE (user_id, symbol)
        )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ users 和 watchlist 資料表建立完成")

if __name__ == "__main__":
    create_tables()
