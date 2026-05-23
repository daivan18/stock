import os
import redis
import requests
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from app.logic.auth_logic import verify_user_credentials_and_get_token

router = APIRouter()

# 💡 最佳實踐：完全不管是什麼雲端，程式碼只認 "REDIS_URL" 這個環境變數
# 如果環境變數沒設定（例如本機開發），就預設連線到本機的 redis://localhost:6379
REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# 修正 1：修復原本掛空的路由，讓輸入首頁 "/" 的人自動導向到 "/login"
@router.get("/", response_class=HTMLResponse)
def index_redirect():
    return RedirectResponse(url="/login", status_code=302)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    # 預熱 Auth 微服務的網址也改用環境變數，方便未來遷移
    AUTH_SERVICE_URL = os.getenv("AUTH_SERVICE_URL", "https://paseto-auth-service.onrender.com")
    try:
        requests.get(f"{AUTH_SERVICE_URL}/healthz", timeout=1)
    except requests.exceptions.RequestException:
        pass

    # 💡 修正 2：改用 request.app.state.templates，刪除原本路由內的 Jinja2Templates 初始化
    return request.app.state.templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        success, result = verify_user_credentials_and_get_token(username, password)
        if not success:
            return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": result})

        token = result
        
        # 💡 修正 3：修復 Key 覆蓋 Bug！將個別使用者的 token 辨識碼作為 Redis 的 Key
        redis_client.setex(f"session:{token}", 3600, username) 

        resp = RedirectResponse("/dashboard", status_code=302)
        
        # 💡 修正 4：既然登出有 delete_cookie，登入成功時記得把 Cookie 寫進去瀏覽器
        # Secure 屬性也改由環境變數控制（本機開發為 False，線上生產環境為 True）
        IS_COOKIE_SECURE = os.getenv("COOKIE_SECURE", "False").lower() == "true"
        resp.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            secure=IS_COOKIE_SECURE,  
            samesite="Lax",
            max_age=3600
        )
        return resp
    except Exception as e:
        return request.app.state.templates.TemplateResponse("login.html", {"request": request, "error": f"登入失敗：{str(e)}"})
    
@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("access_token")
    return resp