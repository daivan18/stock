FROM python:3.10-slim

# 讓 Python 的輸出直接印出，不要留在緩衝區
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 核心修正：在跑 pip install 之前，先安裝 Linux 編譯時需要的底層工具（保證 psycopg2 等套件順利安裝）
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# 先複製裝套件需要的清單
COPY requirements.txt .

# 升級 pip 並安裝 Python 套件
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 複製專案所有原始碼到容器內
COPY . .

# 配合 Cloud Run 與絕大多數雲端服務預設的 8080 連接埠
EXPOSE 8080

# 啟動 FastAPI 服務
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]