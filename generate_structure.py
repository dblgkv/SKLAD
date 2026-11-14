"""
Генератор структуры проекта.
Запуск: python generate_structure.py
Результат: structure.txt в корне проекта
"""
import os

# Файлы и папки, которые не нужно показывать в структуре
IGNORE_DIRS = {
    "venv", ".venv", "__pycache__", ".git", ".idea", ".vscode",
    "node_modules", "uploads", "data", ".pytest_cache", "dist", "build"
}
IGNORE_FILES = {
    "structure.txt", ".DS_Store", "Thumbs.db", ".gitignore",
    "*.pyc", "*.pyo", "*.log", "*.db"
}

# Комментарии к ключевым файлам (что делает файл)
DESCRIPTIONS = {
    "app": "Код приложения",
    "app/__init__.py": "Пакет приложения",
    "app/main.py": "Точка входа: страницы + API",
    "app/database.py": "Настройка SQLite и сессий",
    "app/models.py": "Модели БД: Document, DocumentItem, StockTransaction",
    "app/schemas.py": "Pydantic-схемы для валидации",
    "app/services": "Бизнес-логика",
    "app/services/__init__.py": "Пакет сервисов",
    "app/services/excel_import.py": "Парсинг Excel (parse_excel_preview + import_excel)",
    "app/services/excel_export.py": "Экспорт спецификаций в Excel",
    "app/services/stock_logic.py": "Логика FIFO и расчёт остатков",
    "app/routers": "Резерв для роутеров (опционально)",
    "app/routers/__init__.py": "Пакет роутеров",
    "app/templates": "HTML-шаблоны (Jinja2)",
    "app/templates/base.html": "Каркас: меню, стили",
    "app/templates/upload.html": "Загрузка заказа/отгрузки",
    "app/templates/stock.html": "Склад с фильтрами",
    "app/templates/logs.html": "Журнал операций",
    "data": "Данные (SQLite)",
    "data/warehouse.db": "Файл базы (создаётся автоматически)",
    "uploads": "Временные загрузки (можно чистить)",
    "static": "Статика (CSS, JS, картинки)",
    "requirements.txt": "Зависимости Python",
    "run.py": "Запуск приложения",
    "README.md": "Инструкция для пользователя",
    "structure.txt": "Карта проекта (генерируется)",
    "generate_structure.py": "Генератор этого файла",
}


def should_ignore(name: str, is_dir: bool) -> bool:
    if is_dir and name in IGNORE_DIRS:
        return True
    if not is_dir:
        if name in IGNORE_FILES:
            return True
        # Игнорируем по маске (*.pyc, *.db, *.log)
        for pattern in IGNORE_FILES:
            if pattern.startswith("*") and name.endswith(pattern[1:]):
                return True
    return False


def get_description(rel_path: str) -> str:
    """Возвращает комментарий к файлу, если он есть."""
    rel_path = rel_path.replace("\\", "/")
    return DESCRIPTIONS.get(rel_path, "")


def build_tree(start_path: str, rel_prefix: str = "", prefix: str = "") -> list:
    """Рекурсивно строит список строк дерева."""
    lines = []
    try:
        entries = sorted(os.listdir(start_path))
    except PermissionError:
        return lines

    # Разделяем на папки и файлы, сортируем: сначала папки, потом файлы
    dirs = [e for e in entries if os.path.isdir(os.path.join(start_path, e)) and not should_ignore(e, True)]
    files = [e for e in entries if os.path.isfile(os.path.join(start_path, e)) and not should_ignore(e, False)]

    all_entries = dirs + files

    for i, entry in enumerate(all_entries):
        full_path = os.path.join(start_path, entry)
        is_last = (i == len(all_entries) - 1)
        connector = "└── " if is_last else "├── "
        
        # Путь относительно корня проекта (для поиска описания)
        rel_path = (rel_prefix + "/" + entry) if rel_prefix else entry
        desc = get_description(rel_path)
        
        # Для папок добавляем "/" в конец
        display_name = entry + ("/" if os.path.isdir(full_path) else "")
        desc_part = f"  # {desc}" if desc else ""
        
        lines.append(f"{prefix}{connector}{display_name}{desc_part}")

        if os.path.isdir(full_path):
            new_prefix = prefix + ("    " if is_last else "│   ")
            lines.extend(build_tree(full_path, rel_path, new_prefix))

    return lines


def main():
    project_root = os.path.dirname(os.path.abspath(__file__))
    root_name = os.path.basename(project_root)
    
    lines = [
        f"{root_name}/",
        "│",
        "│  Структура автоматически генерируется: python generate_structure.py",
        "│  Дата генерации: " + __import__("datetime").datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "│",
    ]
    lines.extend(build_tree(project_root))
    
    output_path = os.path.join(project_root, "structure.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    
    print(f"✅ Готово: {output_path}")
    print(f"📄 Строк в файле: {len(lines)}")
    print(f"📁 Файлов и папок: {len(lines) - 4}")


if __name__ == "__main__":
    main()