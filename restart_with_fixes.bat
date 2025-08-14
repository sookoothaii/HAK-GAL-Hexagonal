@echo off
echo ============================================================
echo  HAK-GAL HEXAGONAL - RESTART WITH FIXES
echo ============================================================
echo.

echo [1/3] Stopping any existing processes on port 5001...
for /f "tokens=5" %%a in ('netstat -aon ^| find ":5001" ^| find "LISTENING"') do (
    echo Killing process %%a
    taskkill /F /PID %%a 2>nul
)
timeout /t 2 /nobreak >nul

echo.
echo [2/3] Activating virtual environment...
call .venv_hexa\Scripts\activate.bat

echo.
echo [3/3] Starting Enhanced API with fixes...
echo ============================================================
echo FIXES APPLIED:
echo - Governor Import: BayesianGovernorService fixed
echo - WebSocket: Enabled for Frontend
echo - Performance: Ready for testing
echo ============================================================
echo.

python src_hexagonal\hexagonal_api_enhanced.py

pause
