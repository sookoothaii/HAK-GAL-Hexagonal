@echo off
echo ========================================
echo HAK-GAL MCP Ultimate Server Starter
echo 66 Tools Version
echo ========================================
echo.

REM Aktiviere Python Virtual Environment
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
call .venv_hexa\Scripts\activate.bat

REM Setze Environment Variablen
set PYTHONPATH=D:\MCP Mods\HAK_GAL_HEXAGONAL

echo Starting HAK-GAL MCP Ultimate Server...
echo Tools: 66
echo.

REM Starte den MCP Server
python "D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\hakgal_mcp_ultimate.py"

pause
