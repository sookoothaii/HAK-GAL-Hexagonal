# START ALL SERVICES - KORRIGIERTE VERSION
# Mit korrekten venv-Pfaden

Clear-Host
Write-Host ""
Write-Host "HAK_GAL STARTUP" -ForegroundColor Green
Write-Host "===============" -ForegroundColor Green
Write-Host ""

$BaseDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
cd $BaseDir

Write-Host "Starting services mit venv_hexa..." -ForegroundColor Yellow
Write-Host ""

# 1. API (muss aus src_hexagonal starten)
Write-Host "[1/5] Starting API..." -ForegroundColor Blue
$apiCmd = @"
Write-Host 'API Service [:5002]' -ForegroundColor Blue
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal'
& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' hexagonal_api_enhanced_clean.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $apiCmd
Start-Sleep -Seconds 3

# 2. Caddy
Write-Host "[2/5] Starting Caddy Proxy..." -ForegroundColor Magenta
$caddyCmd = @"
Write-Host 'Caddy Proxy [:8088]' -ForegroundColor Magenta
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
& '.\caddy.exe' run --config .\Caddyfile
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $caddyCmd
Start-Sleep -Seconds 1

# 3. Dashboard
Write-Host "[3/5] Starting Dashboard..." -ForegroundColor Green
$dashCmd = @"
Write-Host 'Dashboard [:5000]' -ForegroundColor Green
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' hakgal_dashboard_no_psutil.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $dashCmd
Start-Sleep -Seconds 1

# 4. Prometheus
Write-Host "[4/5] Starting Prometheus..." -ForegroundColor Yellow
$promCmd = @"
Write-Host 'Prometheus [:8000]' -ForegroundColor Yellow
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' hakgal_prometheus_optimized.py
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $promCmd
Start-Sleep -Seconds 1

# 5. Frontend
Write-Host "[5/5] Starting Frontend..." -ForegroundColor Cyan
$frontCmd = @"
Write-Host 'Frontend [:5173]' -ForegroundColor Cyan
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
npm run dev
"@
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontCmd

Write-Host ""
Write-Host "===================" -ForegroundColor Green
Write-Host "ALL SERVICES STARTED" -ForegroundColor Green
Write-Host "===================" -ForegroundColor Green
Write-Host ""
Write-Host "URLs:" -ForegroundColor Yellow
Write-Host "  Dashboard:  http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  API:        http://127.0.0.1:5002" -ForegroundColor White
Write-Host "  Frontend:   http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  Prometheus: http://127.0.0.1:8000/metrics" -ForegroundColor White
Write-Host "  Proxy:      http://127.0.0.1:8088" -ForegroundColor White
Write-Host ""
Write-Host "WICHTIG: Verwenden Sie 127.0.0.1 statt localhost!" -ForegroundColor Yellow
Write-Host ""
Write-Host "Druecken Sie eine Taste zum Beenden..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
