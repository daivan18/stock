import psycopg2
from dotenv import load_dotenv
import os

# 載入 .env 中的環境變數
load_dotenv()

def get_connection():
    database_url = os.getenv("DATABASE_URL")
    
    if database_url:
        # Render 上用 DATABASE_URL
        return psycopg2.connect(database_url)
    else:
        # 取得本機.env連線資訊
        return psycopg2.connect(
            host=os.getenv("DB_HOST"),
            database=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            port=os.getenv("DB_PORT", 5432)  # 預設 port 5432
        )