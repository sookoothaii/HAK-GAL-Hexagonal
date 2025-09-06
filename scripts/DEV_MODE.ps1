# ============================================
# HAK-GAL Development Mode Launcher
# ============================================
# Starts services with debug output and hot-reload
# ============================================

param(
    [switch]$ApiOnly = $false,
    [switch]$FrontendOnly = $false,
    [switch]$NoFrontend = $false,
    [switch]$Verbose = $false
)

Write-Host "🔧 HAK-GAL DEVELOPMENT MODE" -ForegroundColor Magenta
Write-Host "============================" -ForegroundColor Cyan
Write-Host ""

# Set debug environment variables
$env:FLASK_DEBUG = "1"
$env:FLASK_ENV = "development"
$env:NODE_ENV = "development"
$env:PYTHONDONTWRITEBYTECODE = "1"

if ($Verbose) {
    $env:HAKGAL_DEBUG = "1"
    Write-Host "Verbose mode enabled" -ForegroundColor Yellow
}

# Get root directory
$ROOT_DIR = Get-Location

# Activate virtual environment
if (Test-Path ".venv_hexa\Scripts\Activate.ps1") {
    & ".\.venv_hexa\Scripts\Activate.ps1"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
}

# Function to start service with monitoring
function Start-ServiceWithMonitor {
    param(
        [string]$Name,
        [string]$Command,
        [string]$WorkDir,
        [int]$Port
    )
    
    $script = @"
Write-Host '============================================' -ForegroundColor Magenta
Write-Host '$Name - DEVELOPMENT MODE' -ForegroundColor Yellow
Write-Host 'Port: $Port | Hot-Reload: ENABLED' -ForegroundColor Cyan
Write-Host '============================================' -ForegroundColor Magenta
Write-Host ''
cd '$WorkDir'

# Monitor for crashes and auto-restart
while (`$true) {
    Write-Host '[$(Get-Date -Format "HH:mm:ss")] Starting $Name...' -ForegroundColor Green
    $Command
    
    if (`$LASTEXITCODE -ne 0) {
        Write-Host '[$(Get-Date -Format "HH:mm:ss")] $Name crashed with code: ' `$LASTEXITCODE -ForegroundColor Red
        Write-Host 'Restarting in 3 seconds... (Press Ctrl+C twice to stop)' -ForegroundColor Yellow
        Start-Sleep -Seconds 3
    } else {
        Write-Host '[$(Get-Date -Format "HH:mm:ss")] $Name stopped normally' -ForegroundColor Green
        break
    }
}
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $script
}

# Start services based on parameters
if (-not $FrontendOnly) {
    Write-Host "🚀 Starting API with hot-reload..." -ForegroundColor Yellow
    
    # API with debugging and auto-reload
    $api_cmd = @"
    `$env:FLASK_DEBUG = '1'
    `$env:WERKZEUG_DEBUG_PIN = 'off'
    python -u src_hexagonal\hexagonal_api_enhanced_clean.py
"@
    
    Start-ServiceWithMonitor -Name "HAK-GAL API" -Command $api_cmd -WorkDir $ROOT_DIR -Port 5002
    
    # Also start Ollama if not running
    if (-not (Test-Port 11434)) {
        Write-Host "🤖 Starting Ollama..." -ForegroundColor Yellow
        Start-Process "ollama" -ArgumentList "serve" -WindowStyle Minimized
    }
}

if (-not $ApiOnly -and -not $NoFrontend) {
    Write-Host "🎨 Starting Frontend with hot-reload..." -ForegroundColor Yellow
    
    $frontend_dir = if (Test-Path "frontend") { 
        Join-Path $ROOT_DIR "frontend" 
    } else { 
        Join-Path $ROOT_DIR "..\HAK_GAL_SUITE\flask_frontend" 
    }
    
    if (Test-Path $frontend_dir) {
        $frontend_cmd = "npm run dev -- --host"
        Start-ServiceWithMonitor -Name "Frontend" -Command $frontend_cmd -WorkDir $frontend_dir -Port 5173
    } else {
        Write-Host "⚠️ Frontend directory not found" -ForegroundColor Yellow
    }
}

# Start log viewer in main window
Write-Host ""
Write-Host "📊 DEVELOPMENT DASHBOARD" -ForegroundColor Cyan
Write-Host "========================" -ForegroundColor Gray
Write-Host ""

# Function to test port
function Test-Port {
    param($Port)
    try {
        $connection = New-Object System.Net.Sockets.TcpClient
        $connection.Connect("127.0.0.1", $Port)
        $connection.Close()
        return $true
    } catch {
        return $false
    }
}

# Monitor loop
while ($true) {
    Clear-Host
    Write-Host "🔧 HAK-GAL DEVELOPMENT MONITOR" -ForegroundColor Magenta
    Write-Host "===============================" -ForegroundColor Cyan
    Write-Host "Time: $(Get-Date -Format 'HH:mm:ss')" -ForegroundColor Gray
    Write-Host ""
    
    # Service status
    Write-Host "SERVICE STATUS:" -ForegroundColor Yellow
    
    if (Test-Port 5002) {
        Write-Host "  ✅ API:      http://localhost:5002" -ForegroundColor Green
    } else {
        Write-Host "  ❌ API:      Not responding" -ForegroundColor Red
    }
    
    if (Test-Port 5173) {
        Write-Host "  ✅ Frontend: http://localhost:5173" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Frontend: Not responding" -ForegroundColor Yellow
    }
    
    if (Test-Port 11434) {
        Write-Host "  ✅ Ollama:   http://localhost:11434" -ForegroundColor Green
    } else {
        Write-Host "  ⚠️  Ollama:   Not running" -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "COMMANDS:" -ForegroundColor Yellow
    Write-Host "  [R] Restart API" -ForegroundColor Gray
    Write-Host "  [F] Restart Frontend" -ForegroundColor Gray
    Write-Host "  [B] Open Browser" -ForegroundColor Gray
    Write-Host "  [T] Run Tests" -ForegroundColor Gray
    Write-Host "  [L] Show Logs" -ForegroundColor Gray
    Write-Host "  [Q] Quit" -ForegroundColor Gray
    Write-Host ""
    Write-Host "Press a key or wait (refreshes every 5s)..." -ForegroundColor Cyan
    
    # Wait for input with timeout
    $key = $null
    $counter = 0
    while ($counter -lt 50 -and -not $Host.UI.RawUI.KeyAvailable) {
        Start-Sleep -Milliseconds 100
        $counter++
    }
    
    if ($Host.UI.RawUI.KeyAvailable) {
        $key = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown").Character
        
        switch ($key) {
            'r' {
                Write-Host "Restarting API..." -ForegroundColor Yellow
                Get-Process python* | Where-Object { $_.MainWindowTitle -like "*HAK-GAL API*" } | Stop-Process -Force
            }
            'f' {
                Write-Host "Restarting Frontend..." -ForegroundColor Yellow
                Get-Process node* | Where-Object { $_.MainWindowTitle -like "*Frontend*" } | Stop-Process -Force
            }
            'b' {
                Start-Process "http://localhost:5173"
            }
            't' {
                Write-Host "Running tests..." -ForegroundColor Yellow
                & python -m pytest tests/ -v
                pause
            }
            'l' {
                if (Test-Path "logs") {
                    Get-ChildItem "logs\*.log" | Get-Content -Tail 20
                    pause
                }
            }
            'q' {
                Write-Host "Stopping all services..." -ForegroundColor Red
                Get-Process python*,node* | Where-Object { 
                    $_.MainWindowTitle -like "*HAK-GAL*" -or 
                    $_.MainWindowTitle -like "*Frontend*" 
                } | Stop-Process -Force
                exit
            }
        }
    }
}
