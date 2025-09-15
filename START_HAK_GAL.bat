@echo off
title HAK_GAL System Startup - KORREKTE VERSION
color 0A

echo ========================================
echo     HAK_GAL COMPLETE SYSTEM STARTUP
echo     Reihenfolge: API - Proxy - Dashboard - Prometheus - Frontend
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo [1/5] Starting HAK_GAL API (Port 5002)...
start "API :5002" cmd /k "cd src_hexagonal && ..\.venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py"
timeout /t 3 >nul

echo [2/5] Starting Caddy Proxy (Port 8088)...
start "Caddy :8088" cmd /k "caddy.exe run --config Caddyfile"
timeout /t 1 >nul

echo [3/5] Starting Dashboard (Port 5000)...
start "Dashboard :5000" cmd /k ".\.venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py"
timeout /t 1 >nul

echo [4/5] Starting Prometheus (Port 8000)...
start "Prometheus :8000" cmd /k ".\.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py"
timeout /t 1 >nul

echo [5/5] Starting Frontend (Port 5173)...
start "Frontend :5173" cmd /k "npm run dev"

echo.
echo ========================================
echo    ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================
echo.
echo URLs (use 127.0.0.1 for best performance):
echo.
echo   API:        http://127.0.0.1:5002/api/v1/system/status
echo   Proxy:      http://127.0.0.1:8088
echo   Dashboard:  http://127.0.0.1:5000
echo   Prometheus: http://127.0.0.1:8000/metrics
echo   Frontend:   http://127.0.0.1:5173
echo.
echo WICHTIG: Verwenden Sie 127.0.0.1 statt localhost!
echo          (localhost hat 2-Sekunden-Delay in Windows)
echo.
pause
