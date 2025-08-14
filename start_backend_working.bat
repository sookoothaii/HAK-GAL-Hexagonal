@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - Starting with Legacy Mode (Working)
echo ============================================================
echo.
echo Using JSONL with Legacy Adapters (like before)
echo This is the working configuration
echo.

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
) else (
    echo WARNING: Virtual environment not found
)

REM Optional: Set offline mode to prevent hanging on model downloads
set TRANSFORMERS_OFFLINE=1
set HF_HUB_OFFLINE=1

echo.
echo Starting backend with legacy mode...
echo If it hangs on model loading, press Ctrl+C and run download_models.py first
echo.

REM Start the working backend configuration
python start_working_backend.py

pause
