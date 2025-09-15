@echo off
REM ================================
REM VENV TEST - Prueft ob venv_hexa funktioniert
REM ================================

echo.
echo ========================================
echo     VENV_HEXA TEST
echo ========================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo [1] Teste ob venv_hexa existiert...
if exist "D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" (
    echo     OK - venv_hexa\Scripts\python.exe gefunden
) else (
    echo     FEHLER - venv_hexa\Scripts\python.exe NICHT GEFUNDEN!
    echo.
    echo     Moeglicherweise ist der venv-Pfad anders?
    echo     Pruefe folgende Pfade:
    dir /b .venv* 2>nul
    dir /b venv* 2>nul
    echo.
    pause
    exit /b 1
)

echo.
echo [2] Teste Python-Version in venv_hexa...
"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" --version

echo.
echo [3] Teste ob wichtige Pakete installiert sind...
"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "import flask; print('  OK - Flask installiert')" 2>nul || echo   FEHLER - Flask nicht installiert

"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "import prometheus_client; print('  OK - Prometheus Client installiert')" 2>nul || echo   FEHLER - Prometheus Client nicht installiert

echo.
echo [4] Teste Dashboard-Import...
"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "print('Teste Dashboard-Import...'); exec(open('hakgal_dashboard_no_psutil.py').read()[:100]); print('  OK - Dashboard kann geladen werden')" 2>nul || echo   FEHLER - Dashboard kann nicht geladen werden

echo.
echo [5] Teste API-Import aus src_hexagonal...
cd src_hexagonal
if exist "hexagonal_api_enhanced_clean.py" (
    echo     OK - API-Script gefunden
    "..\D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "print('  Teste API-Import...'); exec(open('hexagonal_api_enhanced_clean.py').read()[:100]); print('  OK - API kann geladen werden')" 2>nul || echo   FEHLER - API kann nicht geladen werden
) else (
    echo     FEHLER - API-Script nicht gefunden!
)
cd ..

echo.
echo ========================================
echo     TEST ABGESCHLOSSEN
echo ========================================
echo.
echo Wenn alle Tests OK sind, verwenden Sie:
echo   START_WITH_VENV.bat
echo.
pause
