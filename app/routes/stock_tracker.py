# stock_tracker.py
from fastapi import APIRouter, Form, Request, HTTPException, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.logic.line_notify import send_line_message
from app.logic.stock_logic import (
    get_stocks_from_db,
    add_stock_to_db,
    delete_stock_from_db,
    update_add_price,
)
from app.logic.auth_logic import verify_paseto_token

templates = Jinja2Templates(directory="templates")
router = APIRouter()

@router.get("/stocks", response_class=HTMLResponse)
async def read_stocks(request: Request):
    try:
        user_info = await verify_paseto_token(request)
        stocks = get_stocks_from_db(user_info["username"])
        msg = request.query_params.get("msg")
        symbol = request.query_params.get("symbol")
        error = request.query_params.get("error")
        return templates.TemplateResponse("stocks.html", {
            "request": request,
            "stocks": stocks,
            "user": user_info,
            "msg": msg,
            "symbol": symbol,
            "error": error
        })
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/add_stock")
async def add_stock(request: Request, symbol: str = Form(...)):
    try:
        user_info = await verify_paseto_token(request)
        return add_stock_to_db(request, symbol, user_info["username"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/delete_stock", response_class=HTMLResponse)
async def delete_stock(request: Request, symbol: str = Form(...)):
    try:
        user_info = await verify_paseto_token(request)
        return delete_stock_from_db(symbol, user_info["username"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/set_add_price")
async def set_add_price(request: Request, symbol: str = Form(...), add_price: float = Form(...)):
    try:
        user_info = await verify_paseto_token(request)
        return update_add_price(symbol, add_price, user_info["username"])
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/notify")
async def notify_test(symbol: str = Form(...)):
    send_line_message(f"[測試] 股票 {symbol} 推播成功！")
    return RedirectResponse("/", status_code=302)
