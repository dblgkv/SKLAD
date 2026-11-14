import os
import configparser
import shutil
import time
import threading
from datetime import date, datetime
from typing import List

from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.database import get_db, CONFIG_PATH, init_db
from app.models import Document, DocumentItem, StockTransaction
from app.services.excel_import import parse_excel_preview
from app.services.stock_logic import get_stock
from app.services.excel_export import export_document, export_stock

router = APIRouter(prefix="/api")

@router.post("/parse-files")
async def api_parse_files(files: List[UploadFile] = File(...)):
    results, all_rows = [], []
    for file in files:
        content = await file.read()
        res = parse_excel_preview(content, file.filename)
        results.append(res)
        if res["status"] in ("success", "warning"):
            all_rows.extend(res["rows"])
    return {"status": "success", "files": results, "all_rows": all_rows}


@router.post("/confirm-upload")
def api_confirm_upload(data: dict, db: Session = Depends(get_db)):
    doc_type = data.get("doc_type")
    files_data = data.get("files", [])
    
    if not files_data:
        raise HTTPException(400, "Нет данных для сохранения")

    # --- ЗАЩИТА ОТ ОТРИЦАТЕЛЬНЫХ ОСТАТКОВ ---
    if doc_type == "shipment":
        # Получаем текущие остатки
        current_stock_list = get_stock(db)
        current_stock = {item["code"]: item["quantity"] for item in current_stock_list}
        
        # Считаем, сколько мы хотим отгрузить в этом запросе
        requested = {}
        for file_info in files_data:
            for r in file_info.get("rows", []):
                code = r["code"]
                requested[code] = requested.get(code, 0) + r["quantity"]
        
        # Проверяем, хватает ли товара
        errors = []
        for code, qty in requested.items():
            available = current_stock.get(code, 0)
            if qty > available:
                # Найдем название для понятной ошибки
                name = next((r["name"] for f in files_data for r in f.get("rows", []) if r["code"] == code), code)
                errors.append(f"{name} (код {code}): нужно {qty}, а на складе {available}")
        
        if errors:
            raise HTTPException(400, "Недостаточно товара на складе:\n" + "\n".join(errors))
    # ----------------------------------------

    docs_created = 0

    for file_info in files_data:
        fname = file_info.get("filename", "Неизвестный файл")
        rows = file_info.get("rows", [])
        if not rows: continue

        try:
            doc_date_obj = datetime.strptime(file_info.get("doc_date", str(date.today())), "%Y-%m-%d").date()
        except ValueError:
            doc_date_obj = date.today()

        doc_number = f"{doc_type.upper()}-{int(time.time())}-{docs_created+1}"
        
        doc = Document(
            doc_type=doc_type, doc_number=doc_number, purpose="Импорт из файла",
            author="Система", doc_date=doc_date_obj, source_file=fname,
        )
        db.add(doc)
        db.flush()

        for i, r in enumerate(rows):
            db.add(DocumentItem(
                document_id=doc.id, position_no=i + 1,
                name=r["name"], code=r["code"], article=r["article"],
                quantity=r["quantity"], unit=r.get("unit", ""), note=r.get("note", ""),
            ))
            db.add(StockTransaction(
                code=r["code"], name=r["name"],
                quantity=r["quantity"] if doc_type == "order" else -r["quantity"],
                document_id=doc.id, document_date=doc_date_obj,
            ))
        docs_created += 1

    db.commit()
    return {"status": "ok", "docs_created": docs_created}


@router.get("/stock")
def api_stock(db: Session = Depends(get_db)):
    return get_stock(db)

@router.get("/logs")
def api_logs(db: Session = Depends(get_db)):
    docs = db.query(Document).order_by(Document.created_at.desc()).all()
    return [{
        "id": d.id,
        "datetime": d.created_at.strftime("%Y-%m-%d %H:%M:%S") if d.created_at else "—",
        "doc_type": d.doc_type, "source_file": d.source_file or "Ручной ввод",
        "items": len(d.items), "author": d.author,
    } for d in docs]

@router.get("/export/document/{doc_id}")
def api_export_document(doc_id: int, db: Session = Depends(get_db)):
    bio = export_document(db, doc_id)
    return StreamingResponse(
        bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f"attachment; filename=spec_{doc_id}.xlsx"},
    )

@router.get("/export/stock")
def api_export_stock(db: Session = Depends(get_db)):
    bio = export_stock(db)
    return StreamingResponse(
        bio, media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=stock.xlsx"},
    )

@router.post("/reload")
def reload_db_connection():
    try:
        init_db()
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(500, f"Ошибка перезагрузки БД: {e}")

@router.post("/shutdown")
def shutdown():
    def kill():
        time.sleep(0.5)
        os._exit(0)
    threading.Thread(target=kill).start()
    return {"status": "shutting down"}