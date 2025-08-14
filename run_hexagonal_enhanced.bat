@echo off
echo ============================================
echo HAK-GAL HEXAGONAL ARCHITECTURE v2.0
echo ============================================
echo.

REM Check if venv exists
if exist .venv_hexa (
    echo Activating Hexagonal Environment...
    call .venv_hexa\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found!
    echo    Please run setup_venv.bat first
    pause
    exit /b 1
)

REM Install enhanced dependencies if needed
pip install flask-socketio --quiet 2>nul

echo.
echo Starting Enhanced Hexagonal API on Port 5001...
echo ----------------------------------------
echo Features:
echo   ✅ /api/command endpoint (add_fact support)
echo   ✅ WebSocket Support
echo   ✅ Governor Integration
echo   ✅ Full Backend Compatibility
echo.

REM Kill any existing process on port 5001
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5001') do (
    taskkill /F /PID %%a 2>nul
)

timeout /t 2 /nobreak >nul

echo Starting Enhanced API...
python src_hexagonal/hexagonal_api_enhanced.py

pause
