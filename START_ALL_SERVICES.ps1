# ================================
# HAK_GAL COMPLETE STARTUP SCRIPT - KORREKTE VERSION
# ================================
# Startet alle Services in der richtigen Reihenfolge

Write-Host "🚀 HAK_GAL SYSTEM STARTUP" -ForegroundColor Cyan
Write-Host "=========================" -ForegroundColor Cyan
Write-Host ""

# Basis-Verzeichnis
$BaseDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
Set-Location $BaseDir

# Python aus venv
$venv = ".\.venv_hexa\Scripts\python.exe"

# Service-Definitionen in KORREKTER REIHENFOLGE
$services = @(
    @{
        Name = "HAK_GAL API"
        Port = 5002
        Command = "cd src_hexagonal && ..\.venv_hexa\Scripts\python.exe hexagonal_api_enhanced_clean.py"
        WorkDir = "$BaseDir\src_hexagonal"
        Color = "Blue"
        Title = "HAK_GAL API [:5002]"
        Order = 1
    },
    @{
        Name = "Caddy Proxy"
        Port = 8088
        Command = ".\caddy.exe run --config .\Caddyfile"
        WorkDir = $BaseDir
        Color = "Magenta"
        Title = "Caddy Proxy [:8088]"
        Order = 2
    },
    @{
        Name = "Dashboard"
        Port = 5000
        Command = ".\venv_hexa\Scripts\python.exe hakgal_dashboard_no_psutil.py"
        WorkDir = $BaseDir
        Color = "Green"
        Title = "HAK_GAL Dashboard [:5000]"
        Order = 3
    },
    @{
        Name = "Prometheus"
        Port = 8000
        Command = ".\.venv_hexa\Scripts\python.exe hakgal_prometheus_optimized.py"
        WorkDir = $BaseDir
        Color = "Yellow"
        Title = "Prometheus Metrics [:8000]"
        Order = 4
    },
    @{
        Name = "Frontend"
        Port = 5173
        Command = "npm run dev"
        WorkDir = $BaseDir  # Oder Frontend-Verzeichnis wenn anders
        Color = "Cyan"
        Title = "Frontend [:5173]"
        Order = 5
    }
)

# Sortiere nach Order
$services = $services | Sort-Object -Property Order

# Prüfe ob Ports bereits belegt sind
Write-Host "📋 Prüfe Port-Status..." -ForegroundColor White
$blockedPorts = @()

foreach ($service in $services) {
    $tcpConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port $service.Port -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($tcpConnection) {
        Write-Host "  ⚠️ Port $($service.Port) bereits belegt ($($service.Name))" -ForegroundColor Yellow
        $blockedPorts += $service.Port
    } else {
        Write-Host "  ✅ Port $($service.Port) frei ($($service.Name))" -ForegroundColor Green
    }
}

if ($blockedPorts.Count -gt 0) {
    Write-Host ""
    Write-Host "⚠️ Einige Ports sind bereits belegt!" -ForegroundColor Yellow
    Write-Host "Möchten Sie:" -ForegroundColor White
    Write-Host "  [1] Trotzdem fortfahren" -ForegroundColor White
    Write-Host "  [2] Alte Services beenden und neu starten" -ForegroundColor White
    Write-Host "  [3] Abbrechen" -ForegroundColor White
    $response = Read-Host "Wahl (1/2/3)"
    
    if ($response -eq '2') {
        Write-Host "Beende alte Services..." -ForegroundColor Yellow
        & "$BaseDir\STOP_ALL_SERVICES.ps1"
        Start-Sleep -Seconds 2
    } elseif ($response -eq '3') {
        Write-Host "Abgebrochen." -ForegroundColor Red
        exit
    }
}

Write-Host ""
Write-Host "🔧 Starte Services in Reihenfolge..." -ForegroundColor White
Write-Host ""

# Starte jeden Service in eigenem Fenster
foreach ($service in $services) {
    Write-Host "  [$($service.Order)/5] Starting $($service.Name) on port $($service.Port)..." -ForegroundColor $service.Color
    
    # PowerShell-Command für den Service
    $command = @"
Write-Host '==============================' -ForegroundColor $($service.Color)
Write-Host '$($service.Title)' -ForegroundColor $($service.Color)
Write-Host '==============================' -ForegroundColor $($service.Color)
Write-Host ''
Write-Host 'Service: $($service.Name)' -ForegroundColor White
Write-Host 'Port: $($service.Port)' -ForegroundColor White
Write-Host 'Directory: $($service.WorkDir)' -ForegroundColor White
Write-Host ''
Write-Host 'Starting...' -ForegroundColor Green
Set-Location '$($service.WorkDir)'
$($service.Command)
"@

    # Starte in neuem Fenster
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $command
    
    # Warte zwischen Services (API braucht mehr Zeit)
    if ($service.Name -eq "HAK_GAL API") {
        Start-Sleep -Seconds 3
    } else {
        Start-Sleep -Seconds 1
    }
}

Write-Host ""
Write-Host "✅ Alle Services gestartet!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 Service-URLs:" -ForegroundColor Cyan
Write-Host "  Dashboard:    http://127.0.0.1:5000" -ForegroundColor White
Write-Host "  API:          http://127.0.0.1:5002/api/v1/system/status" -ForegroundColor White
Write-Host "  Frontend:     http://127.0.0.1:5173" -ForegroundColor White
Write-Host "  Prometheus:   http://127.0.0.1:8000/metrics" -ForegroundColor White
Write-Host "  Proxy:        http://127.0.0.1:8088" -ForegroundColor White
Write-Host ""
Write-Host "💡 WICHTIG: Verwenden Sie 127.0.0.1 statt localhost!" -ForegroundColor Yellow
Write-Host "           (localhost hat 2-Sekunden-Delay in Windows)" -ForegroundColor Yellow
Write-Host ""

# Health-Check nach 5 Sekunden
Start-Sleep -Seconds 5
Write-Host "🔍 Führe Health-Check durch..." -ForegroundColor Cyan

$healthChecks = @(
    @{Name="API"; Url="http://127.0.0.1:5002/api/v1/system/status"},
    @{Name="Dashboard"; Url="http://127.0.0.1:5000/api/health"},
    @{Name="Prometheus"; Url="http://127.0.0.1:8000/metrics"},
    @{Name="Proxy"; Url="http://127.0.0.1:8088"},
    @{Name="Frontend"; Url="http://127.0.0.1:5173"}
)

foreach ($check in $healthChecks) {
    try {
        $response = Invoke-WebRequest -Uri $check.Url -TimeoutSec 2 -UseBasicParsing -ErrorAction SilentlyContinue
        Write-Host "  ✅ $($check.Name): ONLINE" -ForegroundColor Green
    } catch {
        Write-Host "  ⚠️ $($check.Name): Noch nicht bereit oder kein Health-Endpoint" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "✨ System bereit!" -ForegroundColor Green
Write-Host ""
Read-Host "Drücken Sie Enter zum Beenden dieses Fensters"
