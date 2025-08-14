@echo off
echo ============================================================
echo Testing MCP Server with Full Path
echo ============================================================
echo.

echo Testing if Python and MCP server can be reached...
echo.

REM Test with full path including spaces
"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" -c "print('✅ Python in venv works!')"

if %ERRORLEVEL% == 0 (
    echo.
    echo Now testing MCP server...
    echo Press Ctrl+C to stop the test
    echo.
    "D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe" "D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\mcp\mcp_server_windows.py"
) else (
    echo ❌ Python path not working!
    echo Check if venv exists at:
    echo D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe
)

pause
