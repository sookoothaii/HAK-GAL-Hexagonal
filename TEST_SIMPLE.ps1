# HAK_GAL SIMPLE TEST
# Einfache Version ohne komplexe Syntax

Clear-Host
Write-Host ""
Write-Host "HAK_GAL SYSTEM CHECK" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""

cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"

# Test 1: Python venv
Write-Host "Checking Python venv..." -ForegroundColor Yellow
$venvPath = ".\.venv_hexa\Scripts\python.exe"
if (Test-Path $venvPath) {
    Write-Host "  OK - Python venv gefunden" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - Python venv nicht gefunden" -ForegroundColor Red
}

# Test 2: Scripts
Write-Host ""
Write-Host "Checking Scripts..." -ForegroundColor Yellow

if (Test-Path "hakgal_dashboard_no_psutil.py") {
    Write-Host "  OK - Dashboard no_psutil" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - Dashboard no_psutil fehlt" -ForegroundColor Red
}

if (Test-Path "hakgal_dashboard_ultra.py") {
    Write-Host "  OK - Dashboard ultra" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - Dashboard ultra fehlt" -ForegroundColor Red
}

if (Test-Path "hakgal_prometheus_optimized.py") {
    Write-Host "  OK - Prometheus" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - Prometheus fehlt" -ForegroundColor Red
}

if (Test-Path "src_hexagonal\hexagonal_api_enhanced_clean.py") {
    Write-Host "  OK - API" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - API fehlt" -ForegroundColor Red
}

# Test 3: Caddy
Write-Host ""
Write-Host "Checking Caddy..." -ForegroundColor Yellow

if (Test-Path "caddy.exe") {
    Write-Host "  OK - caddy.exe" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - caddy.exe fehlt" -ForegroundColor Red
}

if (Test-Path "Caddyfile") {
    Write-Host "  OK - Caddyfile" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - Caddyfile fehlt" -ForegroundColor Red
}

# Test 4: Startup Scripts
Write-Host ""
Write-Host "Checking Startup Scripts..." -ForegroundColor Yellow

if (Test-Path "START_ALL_SERVICES.ps1") {
    Write-Host "  OK - START_ALL_SERVICES.ps1" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - START_ALL_SERVICES.ps1 fehlt" -ForegroundColor Red
}

if (Test-Path "STOP_ALL_SERVICES.ps1") {
    Write-Host "  OK - STOP_ALL_SERVICES.ps1" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - STOP_ALL_SERVICES.ps1 fehlt" -ForegroundColor Red
}

if (Test-Path "START_HAK_GAL.bat") {
    Write-Host "  OK - START_HAK_GAL.bat" -ForegroundColor Green
} else {
    Write-Host "  FEHLER - START_HAK_GAL.bat fehlt" -ForegroundColor Red
}

Write-Host ""
Write-Host "===================" -ForegroundColor Cyan
Write-Host "CHECK ABGESCHLOSSEN" -ForegroundColor Cyan
Write-Host "===================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Zum Starten verwenden Sie:" -ForegroundColor Yellow
Write-Host "  START_HAK_GAL.bat" -ForegroundColor White
Write-Host "  START_ALL_SERVICES.ps1" -ForegroundColor White
Write-Host ""
Write-Host "Druecken Sie eine Taste zum Beenden..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
