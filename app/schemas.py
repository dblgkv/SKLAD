from pydantic import BaseModel
from datetime import date


class UploadMeta(BaseModel):
    doc_type: str
    doc_number: str
    purpose: str = ""
    author: str = ""
    doc_date: date


class ParsedRow(BaseModel):
    source_file: str = ""
    code: str
    name: str
    article: str = ""
    quantity: float
    unit: str = ""
    note: str = ""


class ConfirmUploadRequest(BaseModel):
    doc_type: str
    rows: list[ParsedRow]