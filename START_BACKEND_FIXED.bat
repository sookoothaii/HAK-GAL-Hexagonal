@echo off
echo ========================================
echo HAK_GAL BACKEND STARTER - FIXED VERSION
echo ========================================
echo.

REM Aktiviere Virtual Environment
call D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\activate.bat

REM Setze Umgebungsvariablen
set PYTHONIOENCODING=utf-8
set PYTHONUNBUFFERED=1
set GOVERNANCE_VERSION=v3
set GOVERNANCE_BYPASS=false
set HAKGAL_WRITE_ENABLED=true

echo [OK] Environment aktiviert

REM Wechsle ins richtige Verzeichnis
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal"

echo [OK] Verzeichnis gewechselt

REM Starte Backend
echo.
echo Starting HAK_GAL Backend on Port 5002...
echo ----------------------------------------
python hexagonal_api_enhanced_clean.py

REM Falls es crasht, pausieren
if errorlevel 1 (
    echo.
    echo ========================================
    echo BACKEND CRASHED! Check logs above.
    echo ========================================
    pause
)
