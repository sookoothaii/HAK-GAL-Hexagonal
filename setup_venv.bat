@echo off
echo ============================================
echo HAK-GAL Hexagonal - Environment Setup
echo ============================================
echo.

echo Creating virtual environment .venv_hexa...
python -m venv .venv_hexa

if %errorlevel% == 0 (
    echo ✅ Virtual environment created!
    echo.
    echo Activating environment...
    call .venv_hexa\Scripts\activate.bat
    
    echo.
    echo Installing required packages...
    pip install flask torch numpy requests sqlalchemy
    
    echo.
    echo ✅ Environment setup complete!
    echo.
    echo To activate in future, run:
    echo    .venv_hexa\Scripts\activate
) else (
    echo ❌ Failed to create virtual environment!
    echo    Make sure Python is installed.
)

echo.
pause
