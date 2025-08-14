@echo off
echo ============================================================
echo COMPLETE SOLUTION - Two Steps
echo ============================================================
echo.
echo STEP 1: Fix the database (copy correct facts)
echo STEP 2: Choose how to run backend
echo.
echo ============================================================
echo STEP 1: FIXING DATABASE...
echo ============================================================

python QUICK_FIX.py

echo.
echo ============================================================
echo STEP 2: CHOOSE YOUR MODE
echo ============================================================
echo.
echo You have 3 options:
echo.
echo [1] Download models first (one-time, 5 minutes)
echo     Then backend starts instantly every time
echo     Run: python download_models_now.py
echo     Then: start_backend_working.bat
echo.
echo [2] Start WITHOUT models (instant, no downloads)
echo     No semantic search, but everything else works
echo     Run: python start_no_models.py
echo.
echo [3] Try original start (might hang on download)
echo     Run: start_backend_working.bat
echo.
echo ============================================================
echo.
set /p choice="Enter your choice (1, 2, or 3): "

if "%choice%"=="1" (
    echo.
    echo Downloading models...
    python download_models_now.py
    if %ERRORLEVEL%==0 (
        echo.
        echo Models downloaded! Starting backend...
        call start_backend_working.bat
    )
) else if "%choice%"=="2" (
    echo.
    echo Starting without models...
    python start_no_models.py
) else if "%choice%"=="3" (
    echo.
    echo Starting normally (might hang)...
    call start_backend_working.bat
) else (
    echo Invalid choice!
)

pause
