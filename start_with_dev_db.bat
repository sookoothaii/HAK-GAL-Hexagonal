@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - Using k_assistant_dev.db (3079 facts)
echo ============================================================

REM Set database override
set HAK_GAL_DB_URI=sqlite:///D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant_dev.db

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

echo Starting with correct database...
python start_working_backend.py

pause
