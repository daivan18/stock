from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()

@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(request: Request):
    # 💡 改用 request.app.state.templates，徹底解決循環匯入與重複初始化問題
    return request.app.state.templates.TemplateResponse("dashboard.html", {"request": request})