@echo off
echo ============================================================
echo  HAK-GAL HEXAGONAL - RESTART WITH INTELLIGENT FACTS
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

REM Start Enhanced API with new features
echo.
echo ============================================================
echo Starting Enhanced API with Intelligent Fact Extraction...
echo  ✅ Context-aware fact suggestions
echo  ✅ Filters out test/example facts
echo  ✅ Generates relevant related facts
echo  ✅ Based on query context
echo ============================================================
echo.

python src_hexagonal/hexagonal_api_enhanced.py

pause
