@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - OFFLINE MODE (No Model Downloads)
echo ============================================================

REM Force offline mode - no downloads!
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1
set SENTENCE_TRANSFORMERS_HOME=D:\MCP Mods\HAK_GAL_HEXAGONAL\.cache
set TRANSFORMERS_CACHE=D:\MCP Mods\HAK_GAL_HEXAGONAL\.cache

REM Use correct database
set HAK_GAL_DB_URI=sqlite:///D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant_dev.db

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

echo.
echo Starting in OFFLINE mode (no model downloads)...
echo If models are missing, they will be skipped
echo.

REM Add timeout to Python
set PYTHONIOENCODING=utf-8
python -u start_working_backend.py

pause
