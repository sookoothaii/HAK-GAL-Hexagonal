@echo off
REM HAK_GAL Report Manager - Windows Batch Script
REM Usage: check_reports.bat [--live]

echo ================================================
echo      HAK_GAL Report Manager v1.0
echo      Automated Compliance ^& SSOT Tool
echo ================================================
echo.

REM Set paths
set PYTHON_PATH=python
set SCRIPT_PATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB\tools\report_manager.py"

REM Check if --live flag is provided
if "%1"=="--live" (
    echo [31m*** LIVE MODE - Changes will be applied! ***[0m
    echo Press Ctrl+C to cancel, or any key to continue...
    pause >nul
    %PYTHON_PATH% %SCRIPT_PATH% --live
) else (
    echo [34m*** DRY RUN MODE - No changes will be made ***[0m
    echo.
    %PYTHON_PATH% %SCRIPT_PATH%
    echo.
    echo To apply corrections, run: %0 --live
)

echo.
echo ================================================
echo Report saved to: PROJECT_HUB\docs\meta\compliance_report.md
echo ================================================
pause
