@echo off
echo ============================================================
echo  HAK-GAL HEXAGONAL ARCHITECTURE v2.0 - ENHANCED START
echo ============================================================

REM Check if virtual environment exists
if not exist .venv_hexa (
    echo Creating virtual environment...
    python -m venv .venv_hexa
)

REM Activate virtual environment
echo Activating virtual environment...
call .venv_hexa\Scripts\activate.bat

REM Install/Update dependencies
echo.
echo Installing enhanced dependencies...
pip install flask-socketio sentry-sdk --quiet

REM Kill any existing process on port 5001
echo.
echo Stopping any existing API on port 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Set environment variables
echo.
echo Setting environment variables...
set FLASK_APP=src_hexagonal/hexagonal_api_enhanced.py
set FLASK_ENV=development
set ENVIRONMENT=hexagonal-dev

REM Optional: Set Sentry DSN if you have one
REM set SENTRY_DSN=your_sentry_dsn_here

REM Start the enhanced API
echo.
echo ============================================================
echo Starting Enhanced Hexagonal API with:
echo  - WebSocket Support
echo  - Governor Integration  
echo  - Sentry Monitoring (if configured)
echo  - CUDA Acceleration
echo ============================================================
echo.

python src_hexagonal/hexagonal_api_enhanced.py

pause
