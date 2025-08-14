@echo off
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
echo Starting Clean Migration to SQLite...
echo ============================================================
python migration_clean\clean_migration_to_sqlite.py
echo.
echo Migration completed. Press any key to exit...
pause > nul
