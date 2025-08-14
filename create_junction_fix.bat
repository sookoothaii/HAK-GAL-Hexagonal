@echo off
echo ============================================================
echo Creating Junction Link without spaces for HAK_GAL
echo ============================================================
echo.
echo This creates a link D:\HAK_GAL pointing to your project
echo to avoid space-in-path issues with Claude Desktop
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% == 0 (
    echo ✅ Running as Administrator
) else (
    echo ❌ This script needs Administrator privileges!
    echo    Right-click and select "Run as Administrator"
    pause
    exit /b 1
)

REM Check if junction already exists
if exist "D:\HAK_GAL" (
    echo.
    echo Junction D:\HAK_GAL already exists!
    echo Do you want to remove it and recreate? (Y/N)
    choice /C YN /N
    if errorlevel 2 goto :skip_junction
    
    rmdir "D:\HAK_GAL"
    echo Removed existing junction
)

REM Create junction
mklink /J "D:\HAK_GAL" "D:\MCP Mods\HAK_GAL_HEXAGONAL"

if %ERRORLEVEL% == 0 (
    echo.
    echo ✅ Junction created successfully!
    echo    D:\HAK_GAL → D:\MCP Mods\HAK_GAL_HEXAGONAL
    echo.
    
    REM Create new config with junction path
    echo Creating Claude config with junction path...
    
    (
    echo {
    echo   "mcpServers": {
    echo     "hak-gal": {
    echo       "command": "D:\\HAK_GAL\\.venv_hexa\\Scripts\\python.exe",
    echo       "args": [
    echo         "D:\\HAK_GAL\\src_hexagonal\\infrastructure\\mcp\\mcp_server_windows.py"
    echo       ],
    echo       "env": {
    echo         "PYTHONPATH": "D:\\HAK_GAL",
    echo         "PYTHONUNBUFFERED": "1"
    echo       }
    echo     }
    echo   }
    echo }
    ) > claude_config_junction.json
    
    echo Config created: claude_config_junction.json
    
    REM Install the config
    set CLAUDE_CONFIG_DIR=%APPDATA%\Claude
    
    if not exist "%CLAUDE_CONFIG_DIR%" (
        mkdir "%CLAUDE_CONFIG_DIR%"
    )
    
    copy /Y "claude_config_junction.json" "%CLAUDE_CONFIG_DIR%\claude_desktop_config.json"
    
    echo.
    echo ✅ Configuration installed with junction paths!
    echo.
    echo NEXT STEPS:
    echo ===========
    echo 1. COMPLETELY restart Claude Desktop
    echo 2. HAK_GAL API should be running on port 5001
    echo 3. Test by asking: "What MCP tools do you have available?"
    echo.
    echo The junction D:\HAK_GAL eliminates space-in-path issues!
    
) else (
    echo.
    echo ❌ Failed to create junction!
    echo    Make sure you're running as Administrator
)

:skip_junction
echo.
pause
