from sqlalchemy import Column, Integer, String, Float, Date, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    doc_type = Column(String(20), nullable=False)   # "order" | "shipment"
    doc_number = Column(String(50), unique=True, nullable=False)
    purpose = Column(String(255))
    author = Column(String(100))
    doc_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)  # <--- ИСПРАВЛЕНО
    source_file = Column(String(255))

    items = relationship("DocumentItem", back_populates="document", cascade="all, delete-orphan")
    transactions = relationship("StockTransaction", back_populates="document")


class DocumentItem(Base):
    __tablename__ = "document_items"

    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    position_no = Column(Integer)
    name = Column(String(255))
    code = Column(String(100), index=True)
    article = Column(String(100))
    brand = Column(String(100))
    quantity = Column(Float, nullable=False)
    unit = Column(String(20))          # шт, м.п., хл.
    manufacturer = Column(String(150))
    supplier = Column(String(150))
    mass = Column(Float)
    note = Column(Text)

    document = relationship("Document", back_populates="items")


class StockTransaction(Base):
    __tablename__ = "stock_transactions"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), index=True, nullable=False)
    name = Column(String(255))
    quantity = Column(Float, nullable=False)   # + приход, - расход
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)
    document_date = Column(Date, nullable=False)
    created_at = Column(DateTime, default=datetime.now)  # <--- ИСПРАВЛЕНО

    document = relationship("Document", back_populates="transactions")