# ================================
# HAK_GAL QUICK START - MIT OPTIONEN
# ================================

Write-Host "🚀 HAK_GAL QUICK START" -ForegroundColor Cyan
Write-Host "======================" -ForegroundColor Cyan
Write-Host ""

$BaseDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
Set-Location $BaseDir

# Dashboard-Auswahl
Write-Host "Welches Dashboard möchten Sie verwenden?" -ForegroundColor Yellow
Write-Host "  [1] hakgal_dashboard_no_psutil.py (schneller, ohne psutil)" -ForegroundColor White
Write-Host "  [2] hakgal_dashboard_ultra.py (mit allen Features)" -ForegroundColor White
$dashboardChoice = Read-Host "Wahl (1/2) [Standard: 1]"

if ($dashboardChoice -eq "2") {
    $dashboardScript = "hakgal_dashboard_ultra.py"
    Write-Host "Verwende Dashboard Ultra" -ForegroundColor Green
} else {
    $dashboardScript = "hakgal_dashboard_no_psutil.py"
    Write-Host "Verwende Dashboard ohne psutil (schneller)" -ForegroundColor Green
}

Write-Host ""
Write-Host "Welche Services möchten Sie starten?" -ForegroundColor Yellow
Write-Host "  [1] Alle Services (API, Proxy, Dashboard, Prometheus, Frontend)" -ForegroundColor White
Write-Host "  [2] Nur Backend (API, Dashboard, Prometheus)" -ForegroundColor White
Write-Host "  [3] Nur API und Dashboard" -ForegroundColor White
Write-Host "  [4] Custom (einzeln auswählen)" -ForegroundColor White
$serviceChoice = Read-Host "Wahl (1/2/3/4) [Standard: 1]"

# Service-Liste basierend auf Auswahl
$selectedServices = @()

switch ($serviceChoice) {
    "2" {
        # Nur Backend
        $selectedServices = @("API", "Dashboard", "Prometheus")
    }
    "3" {
        # Nur API und Dashboard
        $selectedServices = @("API", "Dashboard")
    }
    "4" {
        # Custom
        Write-Host ""
        Write-Host "Wählen Sie Services (j/n):" -ForegroundColor Yellow
        
        $services = @("API", "Proxy", "Dashboard", "Prometheus", "Frontend")
        foreach ($service in $services) {
            $response = Read-Host "  $service starten? (j/n)"
            if ($response -eq "j") {
                $selectedServices += $service
            }
        }
    }
    default {
        # Alle
        $selectedServices = @("API", "Proxy", "Dashboard", "Prometheus", "Frontend")
    }
}

Write-Host ""
Write-Host "Starte ausgewählte Services: $($selectedServices -join ', ')" -ForegroundColor Green
Write-Host ""

# Starte Services
if ($selectedServices -contains "API") {
    Write-Host "Starting API..." -ForegroundColor Blue
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal'; ..\.venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py"
    Start-Sleep -Seconds 3
}

if ($selectedServices -contains "Proxy") {
    Write-Host "Starting Caddy Proxy..." -ForegroundColor Magenta
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'D:\MCP Mods\HAK_GAL_HEXAGONAL'; .\caddy.exe run --config .\Caddyfile"
    Start-Sleep -Seconds 1
}

if ($selectedServices -contains "Dashboard") {
    Write-Host "Starting Dashboard..." -ForegroundColor Green
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'D:\MCP Mods\HAK_GAL_HEXAGONAL'; .\.venv_hexa\Scripts\python.exe $dashboardScript"
    Start-Sleep -Seconds 1
}

if ($selectedServices -contains "Prometheus") {
    Write-Host "Starting Prometheus..." -ForegroundColor Yellow
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'D:\MCP Mods\HAK_GAL_HEXAGONAL'; .\.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py"
    Start-Sleep -Seconds 1
}

if ($selectedServices -contains "Frontend") {
    Write-Host "Starting Frontend..." -ForegroundColor Cyan
    Start-Process powershell -ArgumentList "-NoExit", "-Command", "Set-Location 'D:\MCP Mods\HAK_GAL_HEXAGONAL'; npm run dev"
}

Write-Host ""
Write-Host "✅ Ausgewählte Services gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Aktive URLs:" -ForegroundColor Cyan

if ($selectedServices -contains "API") {
    Write-Host "  API:        http://127.0.0.1:5002/api/v1/system/status" -ForegroundColor White
}
if ($selectedServices -contains "Dashboard") {
    Write-Host "  Dashboard:  http://127.0.0.1:5000" -ForegroundColor White
}
if ($selectedServices -contains "Prometheus") {
    Write-Host "  Prometheus: http://127.0.0.1:8000/metrics" -ForegroundColor White
}
if ($selectedServices -contains "Proxy") {
    Write-Host "  Proxy:      http://127.0.0.1:8088" -ForegroundColor White
}
if ($selectedServices -contains "Frontend") {
    Write-Host "  Frontend:   http://127.0.0.1:5173" -ForegroundColor White
}

Write-Host ""
Write-Host "💡 Tipp: Verwenden Sie 127.0.0.1 statt localhost!" -ForegroundColor Yellow
Write-Host ""
Read-Host "Enter zum Beenden"
