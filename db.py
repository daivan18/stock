import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# 載入 .env 中的環境變數
load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        raise ValueError("環境變數 DATABASE_URL 未設定，無法建立資料庫連線")

    # ❗ 只傳一個參數進來，讓 psycopg2 自己處理 URL 裡的 sslmode
    return psycopg2.connect(database_url)
