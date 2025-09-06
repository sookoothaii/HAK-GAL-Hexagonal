# PowerShell Script for Starting HAK-GAL System
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "HAK-GAL SYSTEM STARTUP (PowerShell)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Set working directory
Set-Location "D:\MCP Mods\HAK_GAL_HEXAGONAL"

# Kill existing processes
Write-Host "[1] Stopping existing services..." -ForegroundColor Yellow
Stop-Process -Name python -ErrorAction SilentlyContinue
Stop-Process -Name node -ErrorAction SilentlyContinue
Stop-Process -Name caddy -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

# Start Backend
Write-Host "[2] Starting Backend (Port 5002)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && .venv_hexa\Scripts\activate && python start_5002_simple.py" -WindowStyle Normal
Start-Sleep -Seconds 3

# Start Frontend
Write-Host "[3] Starting Frontend (Port 5173)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend && npm run dev" -WindowStyle Normal
Start-Sleep -Seconds 5

# Start Caddy
Write-Host "[4] Starting Caddy Proxy (Port 8088)..." -ForegroundColor Yellow
Start-Process cmd -ArgumentList "/k", "cd /d D:\MCP Mods\HAK_GAL_HEXAGONAL && caddy reverse-proxy --from :8088 --to localhost:5173" -WindowStyle Normal
Start-Sleep -Seconds 2

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "Backend:  http://localhost:5002" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "Main:     http://127.0.0.1:8088" -ForegroundColor Green
Write-Host ""
Write-Host "Opening browser..." -ForegroundColor Cyan
Start-Sleep -Seconds 3
Start-Process "http://127.0.0.1:8088/dashboard"

Write-Host ""
Write-Host "Press any key to exit..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")