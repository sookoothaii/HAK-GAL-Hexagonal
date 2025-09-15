@echo off
REM ================================
REM EINZELNE SERVICE STARTER
REM ================================
REM Startet nur einen Service nach Wahl

echo.
echo ========================================
echo     HAK_GAL - SERVICE AUSWAHL
echo ========================================
echo.
echo Welchen Service moechten Sie starten?
echo.
echo   [1] API (Port 5002)
echo   [2] Dashboard (Port 5000)
echo   [3] Prometheus (Port 8000)
echo   [4] Caddy Proxy (Port 8088)
echo   [5] Frontend (Port 5173)
echo   [A] ALLE Services
echo   [X] Beenden
echo.

set /p choice="Ihre Wahl: "

if /i "%choice%"=="1" goto API
if /i "%choice%"=="2" goto DASHBOARD
if /i "%choice%"=="3" goto PROMETHEUS
if /i "%choice%"=="4" goto CADDY
if /i "%choice%"=="5" goto FRONTEND
if /i "%choice%"=="A" goto ALL
if /i "%choice%"=="X" goto END

echo Ungueltige Wahl!
pause
goto END

:API
echo Starting API...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal"
..\venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py
pause
goto END

:DASHBOARD
echo Starting Dashboard...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py
pause
goto END

:PROMETHEUS
echo Starting Prometheus...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py
pause
goto END

:CADDY
echo Starting Caddy...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
caddy.exe run --config Caddyfile
pause
goto END

:FRONTEND
echo Starting Frontend...
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
npm run dev
pause
goto END

:ALL
echo Starting ALL services...
call START_WORKING.bat
goto END

:END
echo.
echo Beendet.
