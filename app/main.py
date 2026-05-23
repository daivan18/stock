import os
import uvicorn
from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles  # 📥 引入靜態檔案支援
from starlette.middleware.sessions import SessionMiddleware
from app.routes import stock_tracker, login, dashboard

# 1. 🔍 從環境變數讀取設定（安全、靈活）
# 本地端預設開啟 Debug，部署到雲端時可在環境變數設定 DEBUG=False
IS_DEBUG = os.getenv("DEBUG", "True").lower() == "true"
# Session 金鑰，部署時務必在雲端設定一串隨機亂碼
SESSION_SECRET = os.getenv("SESSION_SECRET_KEY", "local-dev-secret-key-123")

app = FastAPI(debug=IS_DEBUG)

# 2. 🛡️ 啟用 Session Middleware
app.add_middleware(SessionMiddleware, secret_key=SESSION_SECRET)

# 3. 🌐 設定網頁模板與靜態檔案
templates = Jinja2Templates(directory="templates")
app.state.templates = templates  # 💡 關鍵：存入 app.state，防止各路由間循環匯入

# 如果你有存放 CSS/JS/圖片的 "static" 資料夾，請把下面這行的註解（#）拿掉：
# app.mount("/static", StaticFiles(directory="static"), name="static")

# 4. 🔀 註冊所有路由
app.include_router(login.router)
app.include_router(dashboard.router)
app.include_router(stock_tracker.router)

# 5. 📝 請求監控 Middleware
@app.middleware("http")
async def log_request_debug(request: Request, call_next):
    # 只在本地開發（Debug 模式）時列印詳細資訊，避免線上環境 Log 爆炸或洩漏隱私
    if IS_DEBUG:
        print(f"➡️ 收到請求：{request.method} {request.url}")
        print(f"➡️ Cookie: {request.cookies}")
        
    response = await call_next(request)
    return response

# 6. 🚀 本地端快捷啟動入口
if __name__ == "__main__":
    # 將 reload 設定為 IS_DEBUG
    # 本地開發（Debug=True）時會自動重載，包成 Docker 上線（Debug=False）時會自動關閉重載，兼顧開發便利與線上效能！
    uvicorn.run("main:app", host="0.0.0.0", port=5000, reload=IS_DEBUG)