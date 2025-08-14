@echo off
echo ============================================================
echo  HAK-GAL HEXAGONAL - CLEAN VERSION (NO MOCKS)
echo ============================================================

REM Kill existing process on port 5001
echo.
echo Stopping any existing API on port 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Activate virtual environment
if exist .venv_hexa (
    echo Activating virtual environment...
    call .venv_hexa\Scripts\activate.bat
) else (
    echo Creating virtual environment...
    python -m venv .venv_hexa
    call .venv_hexa\Scripts\activate.bat
    pip install flask flask-cors flask-socketio requests python-dotenv --quiet
)

REM Copy environment from HAK_GAL_SUITE if not exists
if not exist .env (
    if exist ..\HAK_GAL_SUITE\.env (
        echo.
        echo Copying environment from HAK_GAL_SUITE...
        copy ..\HAK_GAL_SUITE\.env .env >nul
    )
)

REM Start Clean API
echo.
echo ============================================================
echo Starting CLEAN API - No Mocks, No Fake Data
echo ============================================================
echo.
echo HONEST BEHAVIOR:
echo  ✅ If LLM not available: Returns error 503
echo  ✅ No fake "suggested facts" 
echo  ✅ No mock explanations
echo  ✅ Only real results or honest errors
echo.
echo To enable LLM explanations:
echo  1. Start original backend on port 5000
echo  OR
echo  2. Configure API keys in .env file
echo ============================================================
echo.

python src_hexagonal/hexagonal_api_enhanced_clean.py

pause
