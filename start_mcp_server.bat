@echo off
echo ============================================================
echo Starting HAK_GAL MCP Server - Minimal Safe Implementation
echo ============================================================
echo.
echo This MCP server provides safe, read-only access to HAK_GAL
echo - Runs independently from main system
echo - Only makes HTTP calls to API
echo - No modifications to core architecture
echo.

cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"

REM Activate virtual environment if it exists
if exist ".venv_hexa\Scripts\activate.bat" (
    call .venv_hexa\Scripts\activate.bat
) else if exist ".venv\Scripts\activate.bat" (
    call .venv\Scripts\activate.bat
)

echo Starting MCP Server (STDIO mode for Claude Desktop)...
python src_hexagonal\infrastructure\mcp\mcp_server.py

pause
