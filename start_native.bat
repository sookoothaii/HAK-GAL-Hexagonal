@echo off
echo ============================================================
echo HAK-GAL HEXAGONAL - NATIVE MODE (Fast Start)
echo ============================================================
echo.
echo Starting WITHOUT legacy dependencies...
echo Expected startup time: 5-10 seconds
echo.

REM Activate virtual environment
if exist .venv_hexa\Scripts\activate.bat (
    call .venv_hexa\Scripts\activate.bat
)

REM Start native backend
python start_native.py

pause
