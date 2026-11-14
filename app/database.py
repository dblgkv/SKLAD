import os
import configparser
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(BASE_DIR, "settings.ini")
DEFAULT_FOLDER = os.path.join(os.path.expanduser("~"), "Documents", "SKLAD_Data")

Base = declarative_base()

def get_db_folder():
    if not os.path.exists(CONFIG_PATH):
        config = configparser.ConfigParser()
        config["DATABASE"] = {"db_folder": DEFAULT_FOLDER}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            config.write(f)
        return DEFAULT_FOLDER
    
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH, encoding="utf-8")
    return config.get("DATABASE", "db_folder", fallback=DEFAULT_FOLDER)

def get_engine_and_session():
    DB_FOLDER = get_db_folder()
    os.makedirs(DB_FOLDER, exist_ok=True)

    existing_dbs = [f for f in os.listdir(DB_FOLDER) if f.startswith("sklad_database_") and f.endswith(".db")]

    if existing_dbs:
        existing_dbs.sort(reverse=True)
        db_filename = existing_dbs[0]
    else:
        today_str = datetime.now().strftime("%Y-%m-%d")
        db_filename = f"sklad_database_{today_str}.db"

    DB_PATH = os.path.join(DB_FOLDER, db_filename)
    SQLALCHEMY_DATABASE_URL = f"sqlite:///{DB_PATH}"

    print(f"📂 База данных: {DB_PATH}")

    engine = create_engine(
        SQLALCHEMY_DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal

# Инициализация при импорте
engine, SessionLocal = get_engine_and_session()

def init_db():
    global engine, SessionLocal
    engine, SessionLocal = get_engine_and_session()
    from app import models
    Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Создаем таблицы при первом запуске (импорт внутри функции, чтобы не было цикла)
def create_tables():
    from app import models
    Base.metadata.create_all(bind=engine)

create_tables()