@echo off
echo ============================================
echo HAK-GAL Hexagonal - Quick Setup
echo ============================================
echo.

echo Step 1: Copying database...
copy "D:\MCP Mods\HAK_GAL_SUITE\k_assistant.db" "D:\MCP Mods\HAK_GAL_HEXAGONAL\k_assistant_dev.db" >nul 2>&1
if exist k_assistant_dev.db (
    echo ✅ Database copied
) else (
    echo ⚠️ Database copy failed - please run copy_database.bat
)

echo.
echo Step 2: Running tests...
python test_parallel.py

echo.
echo ============================================
echo If all tests pass, run:
echo    setup_venv.bat    (to create virtual environment)
echo ============================================
pause
