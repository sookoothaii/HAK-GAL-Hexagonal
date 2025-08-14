@echo off
chcp 65001 >nul
echo ============================================================
echo CLEANUP: Archive Legacy Scripts
echo ============================================================
echo.
echo This will move old/legacy scripts to an archive folder
echo.

REM Create archive folder
if not exist "_archive_legacy" mkdir "_archive_legacy"

echo Moving legacy scripts to _archive_legacy...

REM Move old startup scripts
move start_backend_working.bat _archive_legacy\ 2>nul
move start_with_dev_db.bat _archive_legacy\ 2>nul
move start_fast.bat _archive_legacy\ 2>nul
move start_offline.bat _archive_legacy\ 2>nul
move start_sqlite.bat _archive_legacy\ 2>nul
move start_clean_api.bat _archive_legacy\ 2>nul
move start_enhanced_api.bat _archive_legacy\ 2>nul

REM Move restart scripts
move restart_*.bat _archive_legacy\ 2>nul

REM Move old fixes
move COMPLETE_FIX.bat _archive_legacy\ 2>nul
move FIX_CONFIG_ERROR.bat _archive_legacy\ 2>nul
move diagnose_slow_start.bat _archive_legacy\ 2>nul

REM Move migration scripts (completed)
move MIGRATE_TO_NATIVE*.bat _archive_legacy\ 2>nul
move RUN_SQLITE_MIGRATION.bat _archive_legacy\ 2>nul
move migrate_complete_system.bat _archive_legacy\ 2>nul

REM Move old run scripts
move run_hexagonal.bat _archive_legacy\ 2>nul
move run_hexagonal_enhanced.bat _archive_legacy\ 2>nul

echo.
echo ============================================================
echo CLEANUP COMPLETE!
echo ============================================================
echo.
echo Active scripts:
echo   - start_hexagonal.bat (Main startup)
echo   - start_native.bat (Native mode)
echo   - setup_venv.bat (Environment setup)
echo.
echo Archived scripts moved to: _archive_legacy\
echo.
echo You can safely delete _archive_legacy\ folder later
echo ============================================================

pause
