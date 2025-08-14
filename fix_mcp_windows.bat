@echo off
echo ============================================================
echo Fixing HAK_GAL MCP for Windows
echo ============================================================
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
    copy /Y "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config_backup.json"
    echo Backed up existing configuration
)

REM Copy fixed Windows configuration
copy /Y "claude_desktop_config_windows_fixed.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Windows-compatible configuration installed successfully!
    echo.
    echo The fix includes:
    echo - Windows-compatible STDIO handling
    echo - Proper buffering settings
    echo - Binary mode for Windows pipes
    echo.
    echo Location: %CLAUDE_CONFIG_DIR%\claude_desktop_config.json
    echo.
    echo IMPORTANT NEXT STEPS:
    echo ====================
    echo 1. COMPLETELY close Claude Desktop (check system tray!)
    echo 2. Make sure HAK_GAL API is running:
    echo    python src_hexagonal\hexagonal_api_enhanced_clean.py
    echo 3. Restart Claude Desktop
    echo 4. Test by asking: "What MCP tools do you have available?"
    echo.
    echo The Windows-fixed MCP server is now configured.
) else (
    echo.
    echo ❌ Failed to copy configuration!
    echo Please copy manually:
    echo FROM: claude_desktop_config_windows_fixed.json
    echo TO:   %CLAUDE_CONFIG_DIR%\claude_desktop_config.json
)

echo.
pause
