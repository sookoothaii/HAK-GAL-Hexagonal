# PowerShell Script to Start Port 5002 in WRITE Mode
# ====================================================

Write-Host "================================================" -ForegroundColor Cyan
Write-Host "Starting HAK-GAL Port 5002 - WRITE MODE" -ForegroundColor Green
Write-Host "Database: hexagonal_kb.db" -ForegroundColor Yellow
Write-Host "================================================" -ForegroundColor Cyan
Write-Host ""

# Set environment variables for WRITE mode
$env:HAKGAL_PORT = "5002"
$env:HAKGAL_SQLITE_READONLY = "false"
$env:HAKGAL_SQLITE_DB_PATH = "D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"

# Enable Mojo features
$env:MOJO_ENABLED = "true"
$env:MOJO_VALIDATE_ENABLED = "true"
$env:MOJO_DUPES_ENABLED = "true"

# Enable Governor and Auto-learning
$env:ENABLE_GOVERNOR = "true"
$env:ENABLE_AUTO_LEARNING = "true"
$env:THESIS_ENGINE_ENABLED = "true"
$env:AETHELRED_ENGINE_ENABLED = "true"

Write-Host "Configuration:" -ForegroundColor Cyan
Write-Host "  Port: 5002" -ForegroundColor White
Write-Host "  Database: hexagonal_kb.db" -ForegroundColor White
Write-Host "  Mode: WRITE ENABLED" -ForegroundColor Green
Write-Host "  Mojo: ENABLED" -ForegroundColor Green
Write-Host "  Governor: ENABLED" -ForegroundColor Green
Write-Host "  Auto-Learning: ENABLED" -ForegroundColor Green
Write-Host ""

# Navigate to project directory
Set-Location "D:\MCP Mods\HAK_GAL_HEXAGONAL"

# Activate virtual environment and start
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\.venv_hexa\Scripts\Activate.ps1"

Write-Host "Starting backend..." -ForegroundColor Yellow
Write-Host ""

# Start the backend
python scripts\launch_5002_mojo.py

# Keep window open on exit
Write-Host ""
Write-Host "Backend stopped. Press any key to exit..." -ForegroundColor Red
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
