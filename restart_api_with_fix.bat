@echo off
echo ========================================
echo Restarting Hexagonal API with Fix
echo ========================================

REM Kill existing Python processes on port 5001
echo Stopping existing API...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

REM Activate virtual environment
echo Activating virtual environment...
call .venv_hexa\Scripts\activate.bat

REM Start API
echo Starting Hexagonal API with fixes...
python src_hexagonal/hexagonal_api.py

pause
