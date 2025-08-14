@echo off
echo ============================================================
echo Installing HAK_GAL MCP Configuration for Claude Desktop
echo ============================================================
echo.

REM Get AppData path
set CLAUDE_CONFIG_DIR=%APPDATA%\Claude

REM Create directory if it doesn't exist
if not exist "%CLAUDE_CONFIG_DIR%" (
    mkdir "%CLAUDE_CONFIG_DIR%"
    echo Created directory: %CLAUDE_CONFIG_DIR%
)

REM Copy configuration
copy /Y "claude_desktop_config_windows.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Configuration installed successfully!
    echo.
    echo Location: %CLAUDE_CONFIG_DIR%\claude_desktop_config.json
    echo.
    echo Next steps:
    echo 1. Close Claude Desktop completely (check system tray)
    echo 2. Start HAK_GAL API if not running:
    echo    python src_hexagonal\hexagonal_api_enhanced_clean.py
    echo 3. Restart Claude Desktop
    echo 4. The HAK_GAL tools should now be available!
    echo.
    echo To test in Claude, try asking:
    echo - "Use the search_knowledge tool to find facts about neural networks"
    echo - "Get the HAK_GAL system status"
    echo - "List recent facts from the knowledge base"
) else (
    echo.
    echo ❌ Failed to copy configuration!
    echo Please copy manually:
    echo FROM: claude_desktop_config_windows.json
    echo TO:   %CLAUDE_CONFIG_DIR%\claude_desktop_config.json
)

echo.
pause
