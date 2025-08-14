@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - Starting with SQLite Database
echo ============================================================
echo.
echo Switching from JSONL to SQLite as primary data source
echo Database: k_assistant.db
echo.

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
)

REM Check SQLite databases first
echo Checking available databases...
python check_sqlite_facts.py
echo.
echo ============================================================
echo Starting backend with SQLite...
echo ============================================================
echo.

REM Start the SQLite backend
python start_sqlite_backend.py

pause
