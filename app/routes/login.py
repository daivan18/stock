from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.logic.auth_logic import verify_user_credentials_and_get_token
import redis
import os
import requests

router = APIRouter()
templates = Jinja2Templates(directory="templates")

# 連接本地 Redis（開發用），正式上線改連Render
# redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# 根據環境判斷 Redis URL
if os.getenv("RENDER") == "true":
    # Render 上線環境：使用 Internal URL（不需 Allowlist）
    redis_url = "redis://red-d07jip49c44c73a1qka0:6379"
else:
    # 本地測試環境：使用 External URL（需允許本機 IP）
    redis_url = "rediss://red-d07jip49c44c73a1qka0:oP2WtzLH12w93GZxAIaWyeoxgBvAPNyU@singapore-keyvalue.render.com:6379"

redis_client = redis.from_url(redis_url, decode_responses=True)

# redis_client = redis.StrictRedis(
#     host="singapore-keyvalue.render.com",
#     username="red-d07jip49c44c73a1qka0",
#     port=6379,
#     password="oP2WtzLH12w93GZxAIaWyeoxgBvAPNyU",
#     decode_responses=True
# )

# 啟動FastAPI服務後，直接訪問http://127.0.0.1:8000會自動轉址到/login
@router.get("/", response_class=HTMLResponse)

@router.get("/login", response_class=HTMLResponse)
def login_form(request: Request):
    # 預熱 Paseto Auth 微服務，避免 Render 進入 idle 導致 503
    try:
        requests.get("https://paseto-auth-service.onrender.com/healthz", timeout=1)
    except requests.exceptions.RequestException:
        # 忽略錯誤，只是為了喚醒
        pass

    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login", response_class=HTMLResponse)
def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        success, result = verify_user_credentials_and_get_token(username, password)
        if not success:
            return templates.TemplateResponse("login.html", {"request": request, "error": result})

        token = result
        
        # 存到 Redis，Key = token，Value = username
        redis_client.setex("access_token", 3600, token)  # 存 3600秒 (1小時)

        resp = RedirectResponse("/dashboard", status_code=302)
        # resp.set_cookie(
        #     key="access_token",
        #     value=token,
        #     httponly=True,
        #     secure=False,  # 本機用 False，上線要 True
        #     samesite="Lax",
        #     max_age=3600
        # )
        return resp
    except Exception as e:
        return templates.TemplateResponse("login.html", {"request": request, "error": f"登入失敗：{str(e)}"})
    
@router.get("/logout")
def logout():
    resp = RedirectResponse(url="/login", status_code=302)
    resp.delete_cookie("access_token")
    return resp