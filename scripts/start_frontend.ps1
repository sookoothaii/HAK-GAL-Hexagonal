# PowerShell Script - Start HAK-GAL Frontend
# ==========================================

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "STARTING HAK-GAL FRONTEND ON PORT 8088" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
$currentPath = Get-Location
if (-not (Test-Path "caddy.exe")) {
    Write-Host "ERROR: caddy.exe not found in current directory!" -ForegroundColor Red
    Write-Host "Current directory: $currentPath" -ForegroundColor Yellow
    Write-Host "Please navigate to: D:\MCP Mods\HAK_GAL_HEXAGONAL" -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if Caddyfile exists
if (-not (Test-Path "Caddyfile")) {
    Write-Host "ERROR: Caddyfile not found!" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if port 8088 is already in use
$portInUse = Get-NetTCPConnection -LocalPort 8088 -ErrorAction SilentlyContinue
if ($portInUse) {
    Write-Host "✅ Port 8088 is already in use - Caddy might be running" -ForegroundColor Green
    Write-Host "Try accessing: http://127.0.0.1:8088/query" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "If you want to restart Caddy, first stop the existing process." -ForegroundColor Yellow
    Read-Host "Press Enter to exit"
    exit 0
}

Write-Host "Starting Caddy Reverse Proxy..." -ForegroundColor Green
Write-Host ""
Write-Host "Frontend will be available at:" -ForegroundColor Cyan
Write-Host "  http://127.0.0.1:8088/" -ForegroundColor White
Write-Host "  http://127.0.0.1:8088/query" -ForegroundColor White
Write-Host ""
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Start Caddy
& .\caddy.exe run