@echo off
echo ============================================================
echo  Quick Install Dependencies for Hexagonal Architecture
echo ============================================================

REM Activate virtual environment
if exist .venv_hexa (
    call .venv_hexa\Scripts\activate.bat
) else (
    call .venv\Scripts\activate.bat
)

echo.
echo Installing required packages...

REM Install WebSocket client for testing
pip install python-socketio[client] --quiet

REM Install z3-solver (optional but removes warning)
pip install z3-solver --quiet

REM Install websocket-client for better transport
pip install websocket-client --quiet

echo.
echo ✅ Dependencies installed!
echo.
echo You can now run:
echo   python test_enhanced_complete.py
echo.
pause
