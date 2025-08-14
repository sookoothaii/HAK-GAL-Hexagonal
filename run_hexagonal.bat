@echo off
echo ============================================
echo HAK-GAL HEXAGONAL ARCHITECTURE
echo ============================================
echo.

REM Check if venv exists
if exist .venv_hexa (
    echo Activating Hexagonal Environment...
    call .venv_hexa\Scripts\activate.bat
) else (
    echo ⚠️ Virtual environment not found!
    echo    Please run setup_venv.bat first
    pause
    exit /b 1
)

echo.
echo Starting Hexagonal API on Port 5001...
echo ----------------------------------------
echo.
echo Mode Options:
echo   1. Legacy (Use Original HAK-GAL) [DEFAULT]
echo   2. SQLite (Use Development DB)
echo.

set /p mode="Select mode (1 or 2, Enter for default): "

if "%mode%"=="2" (
    echo Starting with SQLite adapter...
    python start_hexagonal.py --sqlite
) else (
    echo Starting with Legacy adapter...
    python start_hexagonal.py --legacy
)

pause
