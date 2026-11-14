import os
import sys
import subprocess
import threading
import time
import webbrowser
import urllib.request

def ensure_venv():
    venv_python = os.path.join(os.path.dirname(os.path.abspath(__file__)), "venv", "Scripts", "python.exe")
    if os.path.exists(venv_python) and os.path.abspath(sys.executable) != os.path.abspath(venv_python):
        print("🔄 Перезапуск через виртуальное окружение...")
        subprocess.run([venv_python, __file__] + sys.argv[1:])
        sys.exit(0)

ensure_venv()

import uvicorn

def update_structure():
    try:
        subprocess.run([sys.executable, "generate_structure.py"], check=True)
        print("✅ structure.txt обновлён")
    except Exception as e:
        print(f"⚠️ Не удалось обновить structure.txt: {e}")

def open_browser_when_ready():
    url = "http://127.0.0.1:8000"
    for _ in range(20):
        try:
            urllib.request.urlopen(url, timeout=1)
            break
        except Exception:
            time.sleep(1)

    chrome_paths = [
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"
    ]
    opened = False
    for path in chrome_paths:
        if os.path.exists(path):
            subprocess.Popen([path, f"--app={url}"])
            opened = True
            break
    if not opened:
        webbrowser.open(url)
    print(f"🌐 Система открыта: {url}")

if __name__ == "__main__":
    try:
        update_structure()
        threading.Thread(target=open_browser_when_ready, daemon=True).start()
        
        print("=" * 60)
        print("🚀 Складская система запускается...")
        print("📍 Адрес: http://127.0.0.1:8000")
        print("🛑 Для остановки: Ctrl+C")
        print("=" * 60)
        
        uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
    except Exception as e:
        print("\n" + "="*60)
        print("❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ:")
        print(e)
        print("="*60)
        input("Нажмите Enter, чтобы закрыть это окно...")