import configparser
import os
import shutil
from datetime import datetime

from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from app.database import Base, engine, CONFIG_PATH, get_engine_and_session
from app.routers import pages, api

# 1. Создаем таблицы при старте
Base.metadata.create_all(bind=engine)

# 2. СОЗДАЕМ ПАПКУ STATIC, ЕСЛИ ЕЁ НЕТ (защита от ошибок при скачивании с GitHub)
os.makedirs("static", exist_ok=True)

# 3. Создаем приложение
app = FastAPI(title="Складская система")

# 4. Подключаем статику (теперь папка точно существует)
app.mount("/static", StaticFiles(directory="static"), name="static")

# 5. Подключаем роутеры
app.include_router(pages.router)
app.include_router(api.router)

# 6. Настройки
@app.post("/settings")
def save_settings(db_folder: str = Form(...), action: str = Form(...)):
    try:
        os.makedirs(db_folder, exist_ok=True)
        
        if action == "copy":
            current_engine, _ = get_engine_and_session()
            current_db_path = current_engine.url.database
            
            if os.path.exists(current_db_path):
                today_str = datetime.now().strftime("%Y-%m-%d")
                new_db_filename = f"sklad_database_{today_str}.db"
                new_db_path = os.path.join(db_folder, new_db_filename)
                
                if not os.path.exists(new_db_path):
                    shutil.copy2(current_db_path, new_db_path)
        
        config = configparser.ConfigParser()
        config["DATABASE"] = {"db_folder": db_folder}
        with open(CONFIG_PATH, "w", encoding="utf-8") as f:
            config.write(f)
            
        return RedirectResponse(url="/settings?msg=Настройки сохранены.", status_code=303)
    except Exception as e:
        return RedirectResponse(url=f"/settings?error=Ошибка: {str(e)}", status_code=303)