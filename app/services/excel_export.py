from io import BytesIO
import pandas as pd
from sqlalchemy.orm import Session
from app.models import Document
from app.services.stock_logic import get_stock


def export_document(db: Session, doc_id: int) -> BytesIO:
    doc = db.query(Document).get(doc_id)
    if not doc:
        raise ValueError("Документ не найден")
    rows = [{
        "№ позиции": i.position_no, "Наименование": i.name, "Код": i.code,
        "Артикул": i.article, "Марка": i.brand, "Кол-во": i.quantity,
        "Ед. изм.": i.unit, "Изготовитель": i.manufacturer,
        "Поставщик": i.supplier, "Масса": i.mass, "Примечание": i.note,
    } for i in doc.items]
    df = pd.DataFrame(rows)
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Спецификация")
    bio.seek(0)
    return bio


def export_stock(db: Session) -> BytesIO:
    data = get_stock(db)
    df = pd.DataFrame(data).rename(columns={
        "code": "Код", "name": "Наименование", "article": "Артикул",
        "quantity": "Остаток", "unit": "Ед. изм.",
    })
    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as w:
        df.to_excel(w, index=False, sheet_name="Остаток")
    bio.seek(0)
    return bio