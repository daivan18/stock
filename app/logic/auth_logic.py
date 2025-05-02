import bcrypt
import requests
import httpx
import redis
import os
from db import get_connection
from fastapi import Request, HTTPException, status

# 預設為 true（表示本地環境）
IS_LOCAL = os.getenv("IS_LOCAL", "true").lower() == "true"

if IS_LOCAL:
    GET_PASETO_TOKEN_URL = "http://localhost:8080/api/login"
    VERIFY_PASETO_TOKEN_URL = "http://localhost:8080/api/verify"
else:
    GET_PASETO_TOKEN_URL = "https://paseto-auth-service.onrender.com/api/login"
    VERIFY_PASETO_TOKEN_URL = "https://paseto-auth-service.onrender.com/api/verify"

# 連接 Redis，帶入密碼
redis_client = redis.from_url(
    "rediss://red-d07jip49c44c73a1qka0:oP2WtzLH12w93GZxAIaWyeoxgBvAPNyU@singapore-keyvalue.render.com:6379",
    decode_responses=True
)
# redis_client = redis.Redis(
#     host="localhost",
#     port=6379,
#     password="test1234",  # 加入 Redis 密碼
#     decode_responses=True,
# )

# 連接Render PostgreSQL資料庫，並取得資料
def get_user_by_username(username):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT username, password_hash FROM users WHERE username = %s", (username,)
    )
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user


# 登入驗證：比對資料庫登入資訊，並取得 PASETO token
def verify_user_credentials_and_get_token(username, password):

    try:
        user = get_user_by_username(username)

        if not user:
            return False, "使用者不存在"
    except Exception as e:
        return False, f"資料庫查詢錯誤: {str(e)}"

    try:
        # 使用者輸入的密碼用bcrypt 雜湊演算法進行比對
        if not bcrypt.checkpw(password.encode(), user[1].encode()):
            return False, "密碼錯誤"
    except Exception as e:
        return False, f"密碼驗證錯誤: {str(e)}"

    try:
        response = requests.post(
            GET_PASETO_TOKEN_URL, json={"username": username, "password": password}
        )
        response.raise_for_status()
        token = response.json().get("token")
        return True, token
    except Exception as e:
        return False, f"登入服務失敗: {str(e)}"


def get_request(request: Request):
    return request

# async def verify_paseto_token(request: Request = Depends(get_request)): 這段寫法錯誤
# 這一行 Request = Depends(get_request)，就是錯的地方。
# 這行的意思是：「要先執行 get_request，結果當作 request 傳進來」。
# 但 get_request 是 FastAPI 內建用來自動取得 HTTP Header Authorization 的方法，
# 因此如果 Header 裡沒有 Authorization，就會直接自動拋 Missing Authorization header！
# 你原本只是想從 Cookie 抓 token，根本不需要 Depends，直接要 Request 物件就可以。
# async def verify_paseto_token(request: Request):
#     token = request.cookies.get("access_token")

#     print("Cookie access_token:", request.cookies.get("access_token"))

#     if not token:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing Authorization token")

#     async with httpx.AsyncClient() as client:
#         response = await client.post(VERIFY_PASETO_TOKEN_URL, json={"token": token})

#     if response.status_code != 200:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")

#     return response.json()


async def verify_paseto_token(request: Request):
    try:
        # 從 Redis 抓 access_token
        token = redis_client.get("access_token")
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="No token found in Redis or token expired",
            )

        # 確保 token 格式正確（基本防呆）
        token = token.strip()
        if not token.startswith("v2.local."):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token format",
            )

        # 呼叫 Go Server 的 /validate API 驗證 token
        headers = {"Authorization": f"Bearer {token}"}
        async with httpx.AsyncClient() as client:
            response = await client.post(VERIFY_PASETO_TOKEN_URL, headers=headers)

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Token validation failed with status {response.status_code}",
            )

        # 預期 Go Server 驗證成功後會回傳 payload (ex: {"username": "xxx"})
        data = response.json()
        username = data.get("username")
        user_id = data.get("id") 

        if not username:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token valid but payload missing username",
            )

        return {
            "username": username,
            "user_id": user_id,
        }

    except httpx.RequestError as e:
        print(f"HTTP Request Error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Failed to reach authentication server",
        )
    except Exception as e:
        print(f"verify_paseto_token() Exception: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token verification failed",
        )

# async def verify_paseto_token(request: Request):
#     try:
#         # 從 Cookie 抓 access_token
#         access_token = request.cookies.get("access_token")
#         if not access_token:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Missing access_token in cookies"
#             )

#         # 呼叫 Go 的 /verify API
#         async with httpx.AsyncClient() as client:
#             response = await client.post(VERIFY_PASETO_TOKEN_URL, json={"token": access_token})

#         if response.status_code != 200:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid or expired token"
#             )

#         data = response.json()
#         username = data.get("username")

#         if not username:
#             raise HTTPException(
#                 status_code=status.HTTP_401_UNAUTHORIZED,
#                 detail="Invalid token payload"
#             )

#         # 驗證成功，回傳 username 或其他資訊
#         return {"username": username}

#     except Exception as e:
#         print(f"verify_paseto_token() Exception: {str(e)}")
#         raise HTTPException(
#             status_code=status.HTTP_401_UNAUTHORIZED,
#             detail="Token verification failed"
#         )
