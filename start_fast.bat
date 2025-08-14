@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - OPTIMIZED FAST START
echo ============================================================
echo.

REM Set cache paths to speed up model loading
set TRANSFORMERS_CACHE=%USERPROFILE%\.cache\huggingface
set SENTENCE_TRANSFORMERS_HOME=%USERPROFILE%\.cache\torch\sentence_transformers
set HF_HOME=%USERPROFILE%\.cache\huggingface
set TORCH_HOME=%USERPROFILE%\.cache\torch

REM Use local cache if models are already downloaded
set TRANSFORMERS_OFFLINE=0
set HF_HUB_OFFLINE=0

REM Tell Python to use cached models
set PYTHONPATH=D:\MCP Mods\HAK_GAL_SUITE\src;%PYTHONPATH%

REM Use correct database with 3079 facts
set HAK_GAL_DB_URI=sqlite:///D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant_dev.db

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

echo Cache paths configured for fast loading
echo Starting backend...
echo.

REM Start with unbuffered output
python -u start_working_backend.py

pause
