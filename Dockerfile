# 使用官方 Python 基礎映像檔
FROM python:3.13-slim

# 設定工作目錄
WORKDIR /app

# 複製當前目錄內容到容器內
COPY . .

# 安裝依賴套件
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 設定環境變數（可加強安全性）
ENV PYTHONUNBUFFERED=1

# 啟動容器時執行 stock_dip_notify.py
CMD ["python", "stock_dip_notify.py"]
