from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from app.routes import stock_tracker, login, dashboard
from starlette.middleware.sessions import SessionMiddleware

app = FastAPI(debug=True)

app.add_middleware(SessionMiddleware, secret_key="super-secret")

app.include_router(login.router)
app.include_router(dashboard.router)
app.include_router(stock_tracker.router)

templates = Jinja2Templates(directory="templates")

@app.middleware("http")
async def log_request_debug(request: Request, call_next):
    print("➡️ 收到請求：", request.method, request.url)
    print("➡️ Cookie:", request.cookies)
    response = await call_next(request)
    return response