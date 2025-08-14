@echo off
echo ============================================================
echo RESTARTING CLEAN API WITH LLM FIXES
echo ============================================================
echo.
echo Changes applied:
echo - DeepSeek timeout increased to 60 seconds
echo - Mistral model changed to mistral-small-latest
echo - Added Gemini provider with 45s timeout
echo - Better error messages and logging
echo - Trying Gemini first, then Mistral, then DeepSeek
echo.
echo Stopping any running instances...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq *5001*" 2>nul

echo.
echo Starting Clean API on port 5001...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

REM Activate virtual environment if it exists
if exist ".venv_hexa\Scripts\activate.bat" (
    call .venv_hexa\Scripts\activate.bat
) else (
    echo Warning: Virtual environment not found
)

echo.
echo Starting API with fixes...
python src_hexagonal\hexagonal_api_enhanced_clean.py

pause
