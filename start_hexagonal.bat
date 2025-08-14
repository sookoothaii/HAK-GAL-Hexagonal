@echo off
chcp 65001 >nul
echo ============================================================
echo HAK-GAL HEXAGONAL - Native Mode
echo ============================================================
echo.
echo [INFO] Port: 5001
echo [INFO] Architecture: Clean Hexagonal
echo [INFO] Database: SQLite (k_assistant_dev.db)
echo [INFO] Legacy: REMOVED
echo.

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

REM Set UTF-8
set PYTHONIOENCODING=utf-8

echo Starting Hexagonal Backend...
python src_hexagonal\hexagonal_api.py

pause
