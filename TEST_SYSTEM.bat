@echo off
REM ================================
REM HAK_GAL TEST SCRIPT - BATCH VERSION
REM ================================
REM Robuster Test in Batch

echo.
echo ========================================
echo     HAK_GAL SYSTEM CHECK
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo [1] Checking Python venv...
if exist ".\.venv_hexa\Scripts\python.exe" (
    echo     OK - Python venv gefunden
) else (
    echo     FEHLER - Python venv nicht gefunden!
)

echo.
echo [2] Checking Scripts...
if exist "hakgal_dashboard_no_psutil.py" (
    echo     OK - Dashboard no_psutil gefunden
) else (
    echo     FEHLER - Dashboard no_psutil fehlt!
)

if exist "hakgal_dashboard_ultra.py" (
    echo     OK - Dashboard ultra gefunden
) else (
    echo     FEHLER - Dashboard ultra fehlt!
)

if exist "hakgal_prometheus_optimized.py" (
    echo     OK - Prometheus gefunden
) else (
    echo     FEHLER - Prometheus fehlt!
)

if exist "src_hexagonal\hexagonal_api_enhanced_clean.py" (
    echo     OK - API gefunden
) else (
    echo     FEHLER - API fehlt!
)

echo.
echo [3] Checking Caddy...
if exist "caddy.exe" (
    echo     OK - caddy.exe gefunden
) else (
    echo     FEHLER - caddy.exe fehlt!
)

if exist "Caddyfile" (
    echo     OK - Caddyfile gefunden
) else (
    echo     FEHLER - Caddyfile fehlt!
)

echo.
echo [4] Checking NPM...
npm --version >nul 2>&1
if %errorlevel% == 0 (
    echo     OK - NPM installiert
) else (
    echo     FEHLER - NPM nicht gefunden!
)

echo.
echo [5] Checking Startup Scripts...
if exist "START_ALL_SERVICES.ps1" (
    echo     OK - START_ALL_SERVICES.ps1 vorhanden
) else (
    echo     FEHLER - START_ALL_SERVICES.ps1 fehlt!
)

if exist "STOP_ALL_SERVICES.ps1" (
    echo     OK - STOP_ALL_SERVICES.ps1 vorhanden
) else (
    echo     FEHLER - STOP_ALL_SERVICES.ps1 fehlt!
)

if exist "START_HAK_GAL.bat" (
    echo     OK - START_HAK_GAL.bat vorhanden
) else (
    echo     FEHLER - START_HAK_GAL.bat fehlt!
)

echo.
echo [6] Checking Ports...
netstat -an | findstr :5000 >nul 2>&1
if %errorlevel% == 0 (
    echo     WARNUNG - Port 5000 bereits belegt
) else (
    echo     OK - Port 5000 frei
)

netstat -an | findstr :5002 >nul 2>&1
if %errorlevel% == 0 (
    echo     WARNUNG - Port 5002 bereits belegt
) else (
    echo     OK - Port 5002 frei
)

netstat -an | findstr :8000 >nul 2>&1
if %errorlevel% == 0 (
    echo     WARNUNG - Port 8000 bereits belegt
) else (
    echo     OK - Port 8000 frei
)

netstat -an | findstr :8088 >nul 2>&1
if %errorlevel% == 0 (
    echo     WARNUNG - Port 8088 bereits belegt
) else (
    echo     OK - Port 8088 frei
)

netstat -an | findstr :5173 >nul 2>&1
if %errorlevel% == 0 (
    echo     WARNUNG - Port 5173 bereits belegt
) else (
    echo     OK - Port 5173 frei
)

echo.
echo ========================================
echo     SYSTEM CHECK ABGESCHLOSSEN
echo ========================================
echo.
echo Starten Sie mit:
echo   - START_HAK_GAL.bat (Doppelklick)
echo   - START_ALL_SERVICES.ps1 (PowerShell)
echo.
pause
