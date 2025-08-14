@echo off
echo ============================================================
echo MIGRATE HAK-GAL TO FULLY NATIVE HEXAGONAL
echo ============================================================
echo.
echo This will make you COMPLETELY INDEPENDENT from HAK_GAL_SUITE
echo.
echo Benefits after migration:
echo   - Fast startup (5-10 seconds instead of 60+)
echo   - No legacy dependencies
echo   - Clean hexagonal architecture
echo   - Full control over all components
echo.
echo ============================================================
pause

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

REM Run migration
python MIGRATE_TO_NATIVE.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================================
    echo MIGRATION SUCCESSFUL!
    echo ============================================================
    echo.
    echo You can now start the backend with:
    echo   python start_native.py
    echo.
    echo Or use the batch file:
    echo   start_native.bat
    echo.
) else (
    echo.
    echo ============================================================
    echo MIGRATION FAILED - Check the errors above
    echo ============================================================
)

pause
