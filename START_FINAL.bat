@echo off
REM ================================
REM HAK_GAL START - KORREKTE VENV NUTZUNG
REM ================================
REM venv_hexa funktioniert NUR aus dem Hauptverzeichnis

title HAK_GAL Startup - FINAL VERSION
color 0A

echo ========================================
echo     HAK_GAL COMPLETE SYSTEM STARTUP
echo     KORREKTE VENV-NUTZUNG
echo ========================================
echo.

REM WICHTIG: Immer ins Hauptverzeichnis wechseln
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo [1/5] Starting HAK_GAL API (Port 5002)...
echo       API muss aus src_hexagonal laufen...
start "API :5002" cmd /k "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\python.exe src_hexagonal\hexagonal_api_enhanced_clean.py"
timeout /t 3 >nul

echo [2/5] Starting Caddy Proxy (Port 8088)...
start "Caddy :8088" cmd /k "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && caddy.exe run --config Caddyfile"
timeout /t 1 >nul

echo [3/5] Starting Dashboard (Port 5000)...
start "Dashboard :5000" cmd /k "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py"
timeout /t 1 >nul

echo [4/5] Starting Prometheus (Port 8000)...
start "Prometheus :8000" cmd /k "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py"
timeout /t 1 >nul

echo [5/5] Starting Frontend (Port 5173)...
start "Frontend :5173" cmd /k "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && npm run dev"

echo.
echo ========================================
echo    ALL SERVICES STARTED SUCCESSFULLY!
echo ========================================
echo.
echo WICHTIG:
echo   - Verwenden Sie 127.0.0.1 statt localhost!
echo   - API braucht 3-5 Sekunden zum Starten
echo.
echo URLs:
echo   API:        http://127.0.0.1:5002/api/v1/system/status
echo   Proxy:      http://127.0.0.1:8088
echo   Dashboard:  http://127.0.0.1:5000
echo   Prometheus: http://127.0.0.1:8000/metrics
echo   Frontend:   http://127.0.0.1:5173
echo.
pause
