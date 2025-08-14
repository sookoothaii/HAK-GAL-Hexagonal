@echo off
echo ============================================================
echo HAK-GAL COMPLETE SQLITE MIGRATION TOOL
echo ============================================================
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

echo [1] Checking current state...
echo.
python verify_state.py
echo.

echo ============================================================
echo.
set /p choice="Do you want to run the migration? (y/n): "

if /i "%choice%"=="y" (
    echo.
    echo [2] Running migration...
    echo.
    python direct_migrate.py
    echo.
    
    echo ============================================================
    echo.
    echo [3] Verifying migration...
    echo.
    python verify_state.py
    echo.
    
    echo ============================================================
    echo MIGRATION COMPLETE!
    echo.
    echo NEXT STEPS:
    echo 1. Stop the backend (Ctrl+C in the backend window)
    echo 2. Restart with: start_enhanced_api.bat
    echo 3. The system will now use the clean SQLite database
    echo ============================================================
) else (
    echo.
    echo Migration cancelled.
)

echo.
echo Press any key to exit...
pause > nul
