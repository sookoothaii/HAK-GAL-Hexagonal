# ================================
# HAK_GAL STOP ALL SERVICES
# ================================

Write-Host "🛑 HAK_GAL SHUTDOWN SCRIPT" -ForegroundColor Red
Write-Host "=========================" -ForegroundColor Red
Write-Host ""

Write-Host "📋 Suche laufende HAK_GAL Prozesse..." -ForegroundColor Yellow

# Python-Prozesse finden
$pythonProcesses = Get-Process python* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "hakgal|hexagonal|prometheus"
}

# Caddy-Prozess finden
$caddyProcesses = Get-Process caddy* -ErrorAction SilentlyContinue

# Node/NPM Prozesse finden (Frontend)
$nodeProcesses = Get-Process node* -ErrorAction SilentlyContinue | Where-Object {
    $_.CommandLine -match "dev|vite|react"
}

$totalProcesses = $pythonProcesses.Count + $caddyProcesses.Count + $nodeProcesses.Count

if ($totalProcesses -eq 0) {
    Write-Host "✅ Keine HAK_GAL Services gefunden" -ForegroundColor Green
} else {
    Write-Host "Gefundene Services: $totalProcesses" -ForegroundColor White
    Write-Host ""
    
    # Python Services beenden
    if ($pythonProcesses.Count -gt 0) {
        Write-Host "Python Services:" -ForegroundColor Cyan
        foreach ($proc in $pythonProcesses) {
            $cmdline = $proc.CommandLine
            $serviceName = "Unknown"
            
            if ($cmdline -match "dashboard") { $serviceName = "Dashboard" }
            elseif ($cmdline -match "prometheus") { $serviceName = "Prometheus" }
            elseif ($cmdline -match "hexagonal") { $serviceName = "API" }
            
            Write-Host "  Beende $serviceName (PID: $($proc.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Caddy beenden
    if ($caddyProcesses.Count -gt 0) {
        Write-Host "Caddy Proxy:" -ForegroundColor Cyan
        foreach ($proc in $caddyProcesses) {
            Write-Host "  Beende Caddy (PID: $($proc.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    # Node/Frontend beenden
    if ($nodeProcesses.Count -gt 0) {
        Write-Host "Frontend:" -ForegroundColor Cyan
        foreach ($proc in $nodeProcesses) {
            Write-Host "  Beende Node/Frontend (PID: $($proc.Id))..." -ForegroundColor Yellow
            Stop-Process -Id $proc.Id -Force -ErrorAction SilentlyContinue
        }
    }
    
    Write-Host ""
    Write-Host "✅ Alle HAK_GAL Services beendet" -ForegroundColor Green
}

Write-Host ""
Write-Host "📋 Port-Status nach Shutdown:" -ForegroundColor Cyan

$ports = @(
    @{Port=5000; Name="Dashboard"},
    @{Port=5002; Name="API"},
    @{Port=5173; Name="Frontend"},
    @{Port=8000; Name="Prometheus"},
    @{Port=8088; Name="Proxy"}
)

foreach ($item in $ports) {
    $tcpConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port $item.Port -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($tcpConnection) {
        Write-Host "  ⚠️ Port $($item.Port) ($($item.Name)) noch belegt" -ForegroundColor Yellow
    } else {
        Write-Host "  ✅ Port $($item.Port) ($($item.Name)) frei" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "💡 Tipp: Falls Ports noch belegt sind, warten Sie 2-3 Sekunden" -ForegroundColor Yellow
Write-Host "        oder führen Sie das Script erneut aus." -ForegroundColor Yellow
Write-Host ""
Read-Host "Drücken Sie Enter zum Beenden"
