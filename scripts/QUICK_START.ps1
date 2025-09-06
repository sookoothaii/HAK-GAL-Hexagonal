# ============================================
# HAK-GAL Quick Launcher (Minimal Version)
# ============================================
# Starts: API (5002), Frontend (5173), Service (8088)
# ============================================

Write-Host "🚀 HAK-GAL QUICK START" -ForegroundColor Green
Write-Host "======================" -ForegroundColor Cyan

# Kill existing processes on ports
Get-NetTCPConnection -LocalPort 5002,5173,8088,5001 -State Listen -ErrorAction SilentlyContinue | 
    ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }

Start-Sleep -Seconds 1

# Start API on 5002
Write-Host "Starting API (5002)..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; .\.venv_hexa\Scripts\Activate.ps1; python src_hexagonal\hexagonal_api_enhanced_clean.py"

# Start Frontend on 5173
Write-Host "Starting Frontend (5173)..." -ForegroundColor Yellow
$frontend = if (Test-Path "frontend") { "frontend" } else { "..\HAK_GAL_SUITE\flask_frontend" }
if (Test-Path $frontend) {
    Start-Process powershell -ArgumentList "-Command", "cd '$frontend'; npm run dev"
}

# Start Service on 8088 (if exists)
Write-Host "Starting Service (8088)..." -ForegroundColor Yellow
if (Test-Path "..\HAK_GAL_SUITE\api_8088.py") {
    Start-Process powershell -ArgumentList "-Command", "cd '..\HAK_GAL_SUITE'; python api_8088.py"
} elseif (Test-Path "service_8088.py") {
    Start-Process powershell -ArgumentList "-Command", "cd '$PWD'; .\.venv_hexa\Scripts\Activate.ps1; python service_8088.py"
} else {
    Write-Host "  No service for 8088 found" -ForegroundColor Gray
}

# Optional: Start Governor on 5001
if (Test-Path "..\HAK_GAL_SUITE\launch_5001_READONLY_STABLE_PORT.py") {
    Write-Host "Starting Governor (5001)..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-Command", "cd '..\HAK_GAL_SUITE'; python launch_5001_READONLY_STABLE_PORT.py"
}

Write-Host ""
Write-Host "✅ Services starting!" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  API:      http://localhost:5002" -ForegroundColor White
Write-Host "  Frontend: http://localhost:5173" -ForegroundColor White
Write-Host "  Service:  http://localhost:8088" -ForegroundColor White
Write-Host ""

Start-Sleep -Seconds 5
Start-Process "http://localhost:5173"
