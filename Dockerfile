FROM python:3.10-slim

# 💡 優化 1：讓 Python 的輸出直接印出，不要留在緩衝區
ENV PYTHONUNBUFFERED=1

# 設定工作目錄
WORKDIR /app

# 先複製裝套件需要的清單，利用快取加速之後的打包
COPY requirements.txt .

# 安裝 Python 套件
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案所有原始碼到容器內
COPY . .

# 💡 修正 1：Cloud Run 不需要（也會無視）EXPOSE 指令，它可以拿掉，
# 或者改成配合 Cloud Run 預設的 8080
EXPOSE 8080

# 💡 修正 2：啟動指令。
# 如果你的專案是 FastAPI，建議這樣寫：
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

# 如果你的專案是 Flask，且你一定要執行 main.py，請確保 main.py 結尾要改成讀取環境變數的 Port（請看下方說明）
# CMD ["python", "main.py"]