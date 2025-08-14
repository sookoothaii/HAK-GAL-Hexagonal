@echo off
REM HAK_GAL MCP Integration - One-Click Setup
REM =========================================

echo.
echo ========================================
echo HAK_GAL MCP Integration Setup
echo ========================================
echo.

REM Step 1: Test MCP Server
echo [1/4] Testing MCP Server...
python "D:\MCP Mods\HAK_GAL_HEXAGONAL\test_mcp_v2.py"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: MCP Server test failed!
    pause
    exit /b 1
)

echo.
echo [2/4] Backing up existing Claude config...
if exist "%APPDATA%\Claude\claude_desktop_config.json" (
    copy "%APPDATA%\Claude\claude_desktop_config.json" "%APPDATA%\Claude\claude_desktop_config.backup.json" >nul
    echo Backup created: claude_desktop_config.backup.json
) else (
    echo No existing config found.
)

echo.
echo [3/4] Installing HAK_GAL MCP config...
copy "D:\MCP Mods\HAK_GAL_HEXAGONAL\claude_config_final.json" "%APPDATA%\Claude\claude_desktop_config.json" >nul
if %ERRORLEVEL% EQU 0 (
    echo ✓ Config installed successfully
) else (
    echo ERROR: Failed to install config!
    pause
    exit /b 1
)

echo.
echo [4/4] Checking Claude processes...
tasklist | findstr /i "claude" >nul
if %ERRORLEVEL% EQU 0 (
    echo.
    echo WARNING: Claude is currently running!
    echo Please:
    echo   1. Close Claude completely
    echo   2. Check System Tray and quit Claude
    echo   3. Restart Claude
    echo   4. Test with: "What MCP tools do you have?"
) else (
    echo ✓ Claude not running - ready to start
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo Next steps:
echo 1. Start Claude Desktop
echo 2. Wait for full initialization
echo 3. Type: "What MCP tools do you have?"
echo.
echo Expected response:
echo "I have access to the following MCP tools:"
echo "- search_knowledge: Search HAK_GAL knowledge base"
echo "- get_system_status: Get HAK_GAL system status"
echo.
echo If tools don't appear:
echo - Check: D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server_v2.log
echo - Open Claude DevTools (Ctrl+Shift+I) and check Console
echo.
pause
