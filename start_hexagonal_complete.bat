@echo off
echo ============================================================
echo STARTING HEXAGONAL COMPLETE SYSTEM
echo ============================================================
echo.

echo [1/3] Starting HEXAGONAL Backend (Port 5001)...
start "HEXAGONAL Backend" cmd /k "python src_hexagonal\hexagonal_api_enhanced_clean.py"

echo Waiting for backend to initialize...
timeout /t 5 /nobreak >nul

echo [2/3] Starting Frontend (Port 5173)...
cd frontend
start "HEXAGONAL Frontend" cmd /k "npm run dev"

echo.
echo [3/3] Starting Governor (if needed)...
echo Governor can be controlled from frontend

echo.
echo ============================================================
echo HEXAGONAL SYSTEM RUNNING
echo ============================================================
echo.
echo Backend:  http://localhost:5001
echo Frontend: http://localhost:5173
echo.
echo To stop: Close all command windows
echo.
pause
