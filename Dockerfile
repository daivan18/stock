FROM python:3.10-slim

# 💡 優化 1：讓 Python 的輸出直接印出，不要留在緩衝區
# 這樣你才能在終端機利用 `docker compose logs` 即時看到 print 或 logger 的訊息
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 先複製裝套件需要的清單，利用快取加速之後的打包
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有原始碼到容器內
COPY . .

# 暴露你的 Python Web 服務 Port
EXPOSE 5000

# 啟動指令
CMD ["python", "main.py"]