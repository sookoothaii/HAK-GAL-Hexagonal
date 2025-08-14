@echo off
echo ============================================
echo HAK-GAL Hexagonal - Database Copy Script
echo ============================================
echo.

REM Copy database for development
echo Copying database for development use...
copy "D:\MCP Mods\HAK_GAL_SUITE\k_assistant.db" "D:\MCP Mods\HAK_GAL_HEXAGONAL\k_assistant_dev.db"

if %errorlevel% == 0 (
    echo ✅ Database successfully copied!
    echo    Original: HAK_GAL_SUITE\k_assistant.db
    echo    Dev Copy: HAK_GAL_HEXAGONAL\k_assistant_dev.db
) else (
    echo ❌ Failed to copy database!
    echo    Please copy manually.
)

echo.
pause
