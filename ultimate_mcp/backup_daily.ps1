$ErrorActionPreference='Stop'
Set-Location -LiteralPath 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp'
& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py' backup_now
& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\ultimate_mcp\db_maintenance.py' rotate --keep-last 10
