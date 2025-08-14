@echo off
echo ============================================================
echo RESTARTING CLEAN API WITH EXTENDED TIMEOUTS (+50%%)
echo ============================================================
echo.
echo TIMEOUT CONFIGURATION:
echo [⏱️] DeepSeek: 90 seconds (was 60s)
echo [⏱️] Gemini: 70 seconds (was 45s)  
echo [⏱️] API Proxy: 40 seconds (was 25s)
echo [📝] Max Tokens: 1500 (was 1000)
echo.
echo MODEL PRIORITY:
echo 1. gemini-1.5-flash-latest (fastest)
echo 2. gemini-1.5-flash
echo 3. DeepSeek (slower but reliable)
echo.
echo ============================================================
echo.

REM Stop any running instances
echo Stopping any running instances on port 5001...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *5001*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Clean API with extended timeouts...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

REM Activate virtual environment
if exist ".venv_hexa\Scripts\activate.bat" (
    call .venv_hexa\Scripts\activate.bat
    echo ✅ Virtual environment activated
) else (
    echo ⚠️  Warning: Virtual environment not found
)

echo.
echo ============================================================
echo Starting API on http://localhost:5001
echo Extended timeouts are active for better LLM reliability
echo ============================================================
echo.
python src_hexagonal\hexagonal_api_enhanced_clean.py

pause
