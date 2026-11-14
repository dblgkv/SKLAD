import re
import io
import pandas as pd
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import HTTPException
from app.models import Document, DocumentItem, StockTransaction


def _find_header_row(df: pd.DataFrame) -> int:
    """Ищет строку, где есть 'Наименование' и 'Кол-во' (или 'Количество')."""
    for idx, row in df.iterrows():
        row_str = " ".join([str(x).lower() for x in row.values if pd.notna(x)])
        if "наименование" in row_str and ("кол-во" in row_str or "количество" in row_str):
            return idx
    raise ValueError("Не найдена строка с заголовками (ожидаются 'Наименование' и 'Кол-во')")


def _extract_qty(val):
    """Извлекает число из строки типа '178', '178 шт.', '178,5'."""
    if pd.isna(val):
        return None
    s = str(val).replace(",", ".")
    s = re.sub(r"[^\d.]", "", s)
    try:
        return float(s)
    except ValueError:
        return None


def _map_columns(df: pd.DataFrame) -> dict:
    df.columns = [str(c).strip().lower() for c in df.columns]
    return {
        "code": next((c for c in df.columns if "код" in c), None),
        "article": next((c for c in df.columns if "артикул" in c), None),
        "name": next((c for c in df.columns if "наименование" in c), None),
        "qty": next((c for c in df.columns if "кол-во" in c or "количество" in c), None),
        "unit": next((c for c in df.columns if "ед. изм" in c or "ед.изм" in c), None),
        "note": next((c for c in df.columns if "примечание" in c), None),
    }


def parse_excel_preview(file_bytes: bytes, filename: str) -> dict:
    """
    Парсит Excel, но НЕ сохраняет в БД. Возвращает статус и строки.
    """
    result = {"filename": filename, "status": "success", "rows": [], "error": None, "doc_date": str(date.today())}

    # Проверка формата имени файла
    if filename.count("_") < 2 or not filename.lower().endswith(".xlsx"):
        result["status"] = "warning"
        result["error"] = "Имя файла не соответствует формату 'Объект_Заявка_ГГГГ.ММ.ДД.xlsx'"

    # Извлекаем дату из имени файла (ищем паттерн ГГГГ.ММ.ДД)
    date_match = re.search(r'(\d{4})\.(\d{2})\.(\d{2})', filename)
    if date_match:
        try:
            doc_date = datetime.strptime(date_match.group(0), "%Y.%m.%d").date()
            result["doc_date"] = str(doc_date)
        except ValueError:
            pass # Оставляем сегодняшнюю дату, если формат неверный

    try:
        file_stream = io.BytesIO(file_bytes)
        df_raw = pd.read_excel(file_stream, engine="openpyxl", header=None)
        
        file_stream = io.BytesIO(file_bytes)
        header_row_idx = _find_header_row(df_raw)
        df = pd.read_excel(file_stream, engine="openpyxl", header=header_row_idx)
    except Exception as e:
        result["status"] = "error"
        result["error"] = f"Ошибка чтения Excel: {e}"
        return result

    cols = _map_columns(df)
    if not cols["name"] or not cols["qty"]:
        result["status"] = "error"
        result["error"] = "Не найдены обязательные колонки 'Наименование' или 'Кол-во'"
        return result

    for _, row in df.iterrows():
        name = str(row.get(cols["name"], "")).strip() if pd.notna(row.get(cols["name"])) else ""
        qty = _extract_qty(row.get(cols["qty"]))
        if not name or qty is None or qty <= 0:
            continue

        code = ""
        if cols["code"] and pd.notna(row.get(cols["code"])):
            code = str(row.get(cols["code"])).strip()
        elif cols["article"] and pd.notna(row.get(cols["article"])):
            code = str(row.get(cols["article"])).strip()

        if not code or code.lower() == "nan" or code.strip() == "":
            code = name

        article = str(row.get(cols["article"], "")).strip() if cols["article"] and pd.notna(row.get(cols["article"])) else ""
        unit = str(row.get(cols["unit"], "")).strip() if cols["unit"] and pd.notna(row.get(cols["unit"])) else ""
        note = str(row.get(cols["note"], "")).strip() if cols["note"] and pd.notna(row.get(cols["note"])) else ""

        result["rows"].append({
            "source_file": filename,
            "code": code,
            "name": name,
            "article": article,
            "quantity": qty,
            "unit": unit,
            "note": note,
            "doc_date": result["doc_date"] # Передаем дату в каждую строку для JS
        })

    if not result["rows"]:
        result["status"] = "error"
        result["error"] = "Не найдено ни одной строки с данными"

    return result