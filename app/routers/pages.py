from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os

# Нам нужен доступ к шаблонам
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "app", "templates"))

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse(request=request, name="base.html")

@router.get("/upload-order", response_class=HTMLResponse)
def upload_order(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html", context={"doc_type": "order"})

@router.get("/upload-shipment", response_class=HTMLResponse)
def upload_shipment(request: Request):
    return templates.TemplateResponse(request=request, name="upload.html", context={"doc_type": "shipment"})

@router.get("/stock", response_class=HTMLResponse)
def stock_page(request: Request):
    return templates.TemplateResponse(request=request, name="stock.html")

@router.get("/logs", response_class=HTMLResponse)
def logs_page(request: Request):
    return templates.TemplateResponse(request=request, name="logs.html")

@router.get("/settings", response_class=HTMLResponse)
def settings_page(request: Request, msg: str = None, error: str = None):
    from app.database import get_db_folder
    current = get_db_folder()
    return templates.TemplateResponse(
        request=request, 
        name="settings.html", 
        context={"current_folder": current, "msg": msg, "error": error}
    )