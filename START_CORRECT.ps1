# KORREKTE PowerShell Version
# venv_hexa funktioniert nur aus Hauptverzeichnis

Clear-Host
Write-Host ""
Write-Host "HAK_GAL STARTUP - KORREKTE VERSION" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""

# WICHTIG: Hauptverzeichnis
$BaseDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL"

# 1. API - Muss aus src_hexagonal laufen, aber venv aus parent
Write-Host "[1/5] Starting API..." -ForegroundColor Blue
$apiCmd = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal'
& '..\venv_hexa\Scripts\python.exe' hexagonal_api_enhanced_clean.py
"@
Start-Process cmd -ArgumentList "/k", $apiCmd
Start-Sleep -Seconds 3

# 2. Caddy
Write-Host "[2/5] Starting Caddy..." -ForegroundColor Magenta
$caddyCmd = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
.\caddy.exe run --config .\Caddyfile
"@
Start-Process cmd -ArgumentList "/k", $caddyCmd
Start-Sleep -Seconds 1

# 3. Dashboard
Write-Host "[3/5] Starting Dashboard..." -ForegroundColor Green
$dashCmd = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
.venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py
"@
Start-Process cmd -ArgumentList "/k", $dashCmd
Start-Sleep -Seconds 1

# 4. Prometheus
Write-Host "[4/5] Starting Prometheus..." -ForegroundColor Yellow
$promCmd = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py
"@
Start-Process cmd -ArgumentList "/k", $promCmd
Start-Sleep -Seconds 1

# 5. Frontend
Write-Host "[5/5] Starting Frontend..." -ForegroundColor Cyan
$frontCmd = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
npm run dev
"@
Start-Process cmd -ArgumentList "/k", $frontCmd

Write-Host ""
Write-Host "===================================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED" -ForegroundColor Green
Write-Host "===================================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs (verwenden Sie 127.0.0.1):" -ForegroundColor Yellow
Write-Host "  API:        http://127.0.0.1:5002" -ForegroundColor White
Write-Host "  Dashboard:  http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  Prometheus: http://127.0.0.1:8000/metrics" -ForegroundColor White
Write-Host "  Proxy:      http://127.0.0.1:8088" -ForegroundColor White
Write-Host "  Frontend:   http://127.0.0.1:5173" -ForegroundColor White
Write-Host ""
Read-Host "Enter zum Beenden"
