@echo off
echo ============================================================
echo RESTARTING CLEAN API WITH WORKING LLM CONFIGURATION
echo ============================================================
echo.
echo VERIFIED STATUS:
echo [✅] DeepSeek API: WORKING (4.8s response time)
echo [❌] Mistral API: INVALID KEY (401 Unauthorized)
echo [?] Gemini API: Testing new models...
echo.
echo Configuration changes:
echo - DeepSeek as primary provider (confirmed working)
echo - Timeout increased to 60s for DeepSeek
echo - Mistral disabled (invalid key)
echo - Gemini with updated model list
echo.
echo ============================================================
echo.

REM Stop any running instances
echo Stopping any running instances on port 5001...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *5001*" 2>nul
timeout /t 2 /nobreak >nul

echo.
echo Starting Clean API...
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
echo ============================================================
echo.
python src_hexagonal\hexagonal_api_enhanced_clean.py

pause
