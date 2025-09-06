# HAK-GAL Backend Starter PowerShell Script
Write-Host "========================================"
Write-Host "Starting HAK-GAL Backend" -ForegroundColor Green
Write-Host "========================================"
Write-Host ""

# Change to project directory
Set-Location "D:\MCP Mods\HAK_GAL_HEXAGONAL"

# Check if venv exists
if (-not (Test-Path ".\venv_hexa\Scripts\activate.ps1")) {
    Write-Host "❌ Virtual environment not found!" -ForegroundColor Red
    Write-Host "   Please create it first with: python -m venv venv_hexa" -ForegroundColor Yellow
    pause
    exit
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& ".\venv_hexa\Scripts\activate.ps1"

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
