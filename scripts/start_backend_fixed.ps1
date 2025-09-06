# HAK-GAL Backend Starter PowerShell Script (Fixed)
Write-Host "========================================"
Write-Host "Starting HAK-GAL Backend" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""

# Check if we're already in a virtual environment
if ($env:VIRTUAL_ENV) {
    Write-Host "✅ Virtual environment already active: $env:VIRTUAL_ENV" -ForegroundColor Green
} else {
    # Try to activate venv_hexa
    if (Test-Path ".\venv_hexa\Scripts\activate.ps1") {
        Write-Host "Activating virtual environment..." -ForegroundColor Cyan
        & ".\venv_hexa\Scripts\activate.ps1"
    } else {
        Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
        Write-Host "   Please activate it manually or create with: python -m venv venv_hexa" -ForegroundColor Yellow
        pause
        exit
    }
}

# Check if backend module exists
if (-not (Test-Path ".\backend\main.py")) {
    Write-Host "❌ Backend module not found!" -ForegroundColor Red
    Write-Host "   Expected at: .\backend\main.py" -ForegroundColor Yellow
    pause
    exit
}

Write-Host ""
Write-Host "Starting Backend on Port 5002..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

# Start the backend
python -m backend.main
