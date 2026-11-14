@echo off
setlocal
cd /d "%~dp0"

echo ====================================================
echo   SKLAD System
echo ====================================================

IF NOT EXIST "venv" (
    echo [1/3] First run: creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Python is not installed! Download from python.org
        pause
        exit /b
    )
    echo [2/3] Installing dependencies...
    call "venv\Scripts\activate.bat"
    pip install -r requirements.txt
) ELSE (
    call "venv\Scripts\activate.bat"
)

echo [3/3] Starting server...
python run.py

echo.
echo Server stopped. Press any key to close.
pause >nul