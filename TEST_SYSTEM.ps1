# ================================
# HAK_GAL TEST SCRIPT
# ================================
# Testet ob alle benötigten Komponenten vorhanden sind

Write-Host "🔍 HAK_GAL SYSTEM CHECK" -ForegroundColor Cyan
Write-Host "=======================" -ForegroundColor Cyan
Write-Host ""

$BaseDir = "D:\MCP Mods\HAK_GAL_HEXAGONAL"
Set-Location $BaseDir

$allGood = $true

# Check 1: Python venv
Write-Host "📋 Checking Python Environment..." -ForegroundColor Yellow
if (Test-Path ".\.venv_hexa\Scripts\python.exe") {
    Write-Host "  ✅ Python venv gefunden" -ForegroundColor Green
} else {
    Write-Host "  ❌ Python venv FEHLT!" -ForegroundColor Red
    $allGood = $false
}

# Check 2: Wichtige Scripts
Write-Host ""
Write-Host "📋 Checking Scripts..." -ForegroundColor Yellow

$scripts = @(
    @{Path="hakgal_dashboard_no_psutil.py"; Name="Dashboard no psutil"},
    @{Path="hakgal_dashboard_ultra.py"; Name="Dashboard ultra"},
    @{Path="hakgal_prometheus_optimized.py"; Name="Prometheus"},
    @{Path="src_hexagonal\hexagonal_api_enhanced_clean.py"; Name="API"}
)

foreach ($script in $scripts) {
    if (Test-Path $script.Path) {
        Write-Host "  ✅ $($script.Name) gefunden" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $($script.Name) FEHLT! [$($script.Path)]" -ForegroundColor Red
        $allGood = $false
    }
}

# Check 3: Caddy
Write-Host ""
Write-Host "📋 Checking Caddy..." -ForegroundColor Yellow
if (Test-Path ".\caddy.exe") {
    Write-Host "  ✅ caddy.exe gefunden" -ForegroundColor Green
} else {
    Write-Host "  ❌ caddy.exe FEHLT!" -ForegroundColor Red
    $allGood = $false
}

if (Test-Path ".\Caddyfile") {
    Write-Host "  ✅ Caddyfile gefunden" -ForegroundColor Green
} else {
    Write-Host "  ❌ Caddyfile FEHLT!" -ForegroundColor Red
    $allGood = $false
}

# Check 4: NPM
Write-Host ""
Write-Host "📋 Checking NPM..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>$null
    if ($npmVersion) {
        Write-Host "  ✅ NPM installiert - Version $npmVersion" -ForegroundColor Green
    } else {
        Write-Host "  ❌ NPM nicht gefunden!" -ForegroundColor Red
        $allGood = $false
    }
} catch {
    Write-Host "  ❌ NPM nicht installiert oder nicht im PATH!" -ForegroundColor Red
    $allGood = $false
}

# Check 5: Package.json für Frontend
if (Test-Path ".\package.json") {
    Write-Host "  ✅ package.json gefunden" -ForegroundColor Green
} else {
    Write-Host "  ⚠️ package.json nicht im Hauptverzeichnis (möglicherweise in Unterordner)" -ForegroundColor Yellow
}

# Check 6: Startup Scripts
Write-Host ""
Write-Host "📋 Checking Startup Scripts..." -ForegroundColor Yellow

$startupScripts = @(
    "START_ALL_SERVICES.ps1",
    "STOP_ALL_SERVICES.ps1",
    "QUICK_START.ps1",
    "START_HAK_GAL.bat"
)

foreach ($script in $startupScripts) {
    if (Test-Path $script) {
        Write-Host "  ✅ $script vorhanden" -ForegroundColor Green
    } else {
        Write-Host "  ❌ $script FEHLT!" -ForegroundColor Red
    }
}

# Check 7: Port-Status
Write-Host ""
Write-Host "📋 Checking Port Status..." -ForegroundColor Yellow

$ports = @(
    @{Port=5000; Name="Dashboard"},
    @{Port=5002; Name="API"},
    @{Port=5173; Name="Frontend"},
    @{Port=8000; Name="Prometheus"},
    @{Port=8088; Name="Proxy"}
)

$portsInUse = @()
foreach ($item in $ports) {
    $tcpConnection = Test-NetConnection -ComputerName 127.0.0.1 -Port $item.Port -WarningAction SilentlyContinue -InformationLevel Quiet
    if ($tcpConnection) {
        Write-Host "  ⚠️ Port $($item.Port) bereits belegt [$($item.Name)]" -ForegroundColor Yellow
        $portsInUse += $item.Port
    } else {
        Write-Host "  ✅ Port $($item.Port) frei [$($item.Name)]" -ForegroundColor Green
    }
}

# Zusammenfassung
Write-Host ""
Write-Host ("=" * 50) -ForegroundColor White
if ($allGood) {
    Write-Host "✅ SYSTEM BEREIT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Sie können jetzt starten mit:" -ForegroundColor Cyan
    Write-Host "  • START_ALL_SERVICES.ps1 - alle Services" -ForegroundColor White
    Write-Host "  • QUICK_START.ps1 - interaktive Auswahl" -ForegroundColor White
    Write-Host "  • START_HAK_GAL.bat - Batch-Version" -ForegroundColor White
    
    if ($portsInUse.Count -gt 0) {
        Write-Host ""
        Write-Host "⚠️ Hinweis: Einige Ports sind bereits belegt." -ForegroundColor Yellow
        Write-Host "   Führen Sie STOP_ALL_SERVICES.ps1 aus um alte Services zu beenden." -ForegroundColor Yellow
    }
} else {
    Write-Host "⚠️ PROBLEME GEFUNDEN!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Bitte beheben Sie die oben genannten Probleme." -ForegroundColor Yellow
}

Write-Host ""
Read-Host "Enter zum Beenden"
