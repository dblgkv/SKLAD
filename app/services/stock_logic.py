from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models import StockTransaction


def get_stock(db: Session):
    """Текущий остаток по каждому коду."""
    rows = (
        db.query(
            StockTransaction.code,
            func.max(StockTransaction.name).label("name"),
            func.sum(StockTransaction.quantity).label("quantity"),
        )
        .group_by(StockTransaction.code)
        .all()
    )
    return [
        {
            "code": r.code,
            "name": r.name,
            "article": "",
            "quantity": round(r.quantity, 3),
            "unit": "",
        }
        for r in rows
        if abs(r.quantity) > 1e-9
    ]