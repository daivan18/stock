# Dockerfile

FROM python:3.10-slim

# 建立工作目錄
WORKDIR /app

# 複製專案檔案
COPY . .

# 安裝依賴
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# 執行 Uvicorn 伺服器
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
