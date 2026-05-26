FROM python:3.10-slim

# 讓 Python 的輸出直接印出，不要留在緩衝區
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 終極修正：補全所有可能需要的編譯工具與環境
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    g++ \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 先複製裝套件需要的清單
COPY requirements.txt .

# 關鍵點：先把 pip 升級到最新版，再裝 dependencies
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有原始碼到容器內
COPY . .

# 配合 Cloud Run 預設的 8080 連接埠
EXPOSE 8080

# 啟動 FastAPI 服務
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]