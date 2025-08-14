@echo off
echo ============================================================
echo Installing HAK_GAL MCP with Full Python Path
echo ============================================================
echo.
echo This fixes the space-in-path issue by using full Python path
echo.

REM Get AppData path
set CLAUDE_CONFIG_DIR=%APPDATA%\Claude

REM Create directory if it doesn't exist
if not exist "%CLAUDE_CONFIG_DIR%" (
    mkdir "%CLAUDE_CONFIG_DIR%"
    echo Created directory: %CLAUDE_CONFIG_DIR%
)

REM Backup existing config
if exist "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json" (
    copy /Y "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config_backup_%date:~-4%%date:~3,2%%date:~0,2%.json"
    echo Backed up existing configuration
)

REM Copy new configuration with full path
copy /Y "claude_config_full_path.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Configuration with FULL PYTHON PATH installed successfully!
    echo.
    echo What this fixes:
    echo - Uses full path to python.exe in venv
    echo - Handles spaces in "MCP Mods" directory correctly
    echo - Windows-compatible MCP server
    echo.
    echo Location: %CLAUDE_CONFIG_DIR%\claude_desktop_config.json
    echo.
    echo CRITICAL NEXT STEPS:
    echo ====================
    echo 1. COMPLETELY close Claude Desktop
    echo    - Close all windows
    echo    - Right-click system tray icon → Quit
    echo    - Check Task Manager: NO Claude.exe should be running
    echo.
    echo 2. Make sure HAK_GAL API is still running on port 5001
    echo.
    echo 3. Start Claude Desktop fresh
    echo.
    echo 4. Test by asking: "What MCP tools do you have available?"
    echo.
    echo If it still doesn't work, check logs at:
    echo %APPDATA%\Claude\logs\
) else (
    echo.
    echo ❌ Failed to copy configuration!
)

echo.
echo To manually test the MCP server, run:
echo "D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\mcp\mcp_server_windows.py"
echo.
pause
