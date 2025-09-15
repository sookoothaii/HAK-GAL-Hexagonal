@echo off
REM ================================
REM HAK_GAL START - API SPECIAL HANDLING
REM ================================

title HAK_GAL Startup - WORKING VERSION
color 0A

echo ========================================
echo     HAK_GAL STARTUP - WORKING VERSION
echo ========================================
echo.

REM [1] API - Spezieller Start weil es aus src_hexagonal laufen muss
echo [1/5] Starting API (Port 5002)...
echo       Special handling fuer src_hexagonal...
start "API :5002" cmd /c "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal && ..\venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py && pause"
timeout /t 3 >nul

REM [2] Caddy - Laeuft aus Hauptverzeichnis
echo [2/5] Starting Caddy Proxy (Port 8088)...
start "Caddy :8088" cmd /c "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && caddy.exe run --config Caddyfile"
timeout /t 1 >nul

REM [3] Dashboard - Laeuft aus Hauptverzeichnis
echo [3/5] Starting Dashboard (Port 5000)...
start "Dashboard :5000" cmd /c "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py && pause"
timeout /t 1 >nul

REM [4] Prometheus - Laeuft aus Hauptverzeichnis
echo [4/5] Starting Prometheus (Port 8000)...
start "Prometheus :8000" cmd /c "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py && pause"
timeout /t 1 >nul

REM [5] Frontend - NPM aus Hauptverzeichnis
echo [5/5] Starting Frontend (Port 5173)...
start "Frontend :5173" cmd /c "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && npm run dev"

echo.
echo ========================================
echo    SERVICES GESTARTET!
echo ========================================
echo.
echo Falls ein Service nicht startet:
echo   - Pruefen Sie die Fehlermeldung im jeweiligen Fenster
echo   - Starten Sie den Service manuell
echo.
echo URLs (mit 127.0.0.1):
echo   API:        http://127.0.0.1:5002
echo   Dashboard:  http://127.0.0.1:5000
echo   Prometheus: http://127.0.0.1:8000/metrics
echo   Proxy:      http://127.0.0.1:8088
echo   Frontend:   http://127.0.0.1:5173
echo.
pause
