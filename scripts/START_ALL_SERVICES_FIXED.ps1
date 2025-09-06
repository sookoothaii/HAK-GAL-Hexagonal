# ============================================
# HAK-GAL FIXED LAUNCHER - CORRECT DATABASE
# ============================================
# Uses hexagonal_kb.db with 5000+ facts
# ============================================

param(
    [switch]$SkipVerification = $false
)

Write-Host "============================================" -ForegroundColor Red
Write-Host "🚀 HAK-GAL UNIFIED LAUNCHER v4.0" -ForegroundColor Yellow  
Write-Host "✅ ALL SERVICES ON PORT 5002" -ForegroundColor Green
Write-Host "📊 Database: hexagonal_kb.db (5911 facts)" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Red
Write-Host ""

# Set correct database path as environment variable
$env:HAKGAL_SQLITE_DB_PATH = "D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
Write-Host "📊 Database set to: $env:HAKGAL_SQLITE_DB_PATH" -ForegroundColor Cyan

# Step 1: Kill all existing processes
Write-Host ""
Write-Host "🛑 Stopping all existing services..." -ForegroundColor Yellow

# Kill Python processes
Get-Process python* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill Node processes  
Get-Process node* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill Caddy process
Get-Process caddy* -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue

# Kill processes on ports
$ports = @(5002, 5173, 8088)
foreach ($port in $ports) {
    try {
        $processes = Get-NetTCPConnection -LocalPort $port -State Listen -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -Unique
        if ($processes) {
            foreach ($pid in $processes) {
                Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {}
}

Write-Host "✅ All processes stopped" -ForegroundColor Green
Start-Sleep -Seconds 2

# Step 2: Verify database (unless skipped)
if (-not $SkipVerification) {
    Write-Host ""
    Write-Host "🔍 Verifying database..." -ForegroundColor Yellow
    
    if (Test-Path ".venv_hexa\Scripts\python.exe") {
        & .\.venv_hexa\Scripts\python.exe verify_database.py
    } else {
        python verify_database.py
    }
    
    Write-Host ""
    Write-Host "Press any key to continue..." -ForegroundColor Cyan
    pause
}

# Step 3: Activate virtual environment
Write-Host ""
Write-Host "🐍 Activating Python environment..." -ForegroundColor Yellow

if (Test-Path ".venv_hexa\Scripts\Activate.ps1") {
    & ".\.venv_hexa\Scripts\Activate.ps1"
    $PYTHON = ".\.venv_hexa\Scripts\python.exe"
    Write-Host "✅ Virtual environment activated" -ForegroundColor Green
} else {
    $PYTHON = "python"
    Write-Host "⚠️  Using system Python" -ForegroundColor Yellow
}

# Step 4: Start Ollama if not running
Write-Host ""
Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow

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

if (-not (Test-Port 11434)) {
    Write-Host "   Starting Ollama..." -ForegroundColor Gray
    Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

if (Test-Port 11434) {
    Write-Host "✅ Ollama is running" -ForegroundColor Green
} else {
    Write-Host "⚠️  Ollama not available" -ForegroundColor Yellow
}

# Step 5: Start HAK-GAL API (Port 5002)
Write-Host ""
Write-Host "1️⃣ Starting HAK-GAL API on port 5002..." -ForegroundColor Yellow

$api_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'HAK-GAL API - PORT 5002' -ForegroundColor Green
Write-Host '(Governor + Reasoning + WebSocket - ALL INTEGRATED)' -ForegroundColor Cyan
Write-Host 'Database: hexagonal_kb.db (5911 facts)' -ForegroundColor Yellow
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

# Set environment variable
`$env:HAKGAL_SQLITE_DB_PATH = 'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'
Write-Host "Using database: `$env:HAKGAL_SQLITE_DB_PATH" -ForegroundColor Cyan

cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'

# Activate virtual environment if available
if (Test-Path '.venv_hexa\Scripts\Activate.ps1') {
    & '.\.venv_hexa\Scripts\Activate.ps1'
}

# Start API
python src_hexagonal\hexagonal_api_enhanced_clean.py

if (`$LASTEXITCODE -ne 0) {
    Write-Host 'API crashed! Check the error above.' -ForegroundColor Red
    pause
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $api_script

# Step 6: Start Frontend (Port 5173)
Write-Host "2️⃣ Starting Frontend on port 5173..." -ForegroundColor Yellow

$frontend_paths = @(
    "D:\MCP Mods\HAK_GAL_HEXAGONAL\frontend",
    "D:\MCP Mods\HAK_GAL_SUITE\flask_frontend",
    "frontend",
    "..\HAK_GAL_SUITE\flask_frontend"
)

$frontend_found = $false
foreach ($path in $frontend_paths) {
    if (Test-Path $path) {
        $FRONTEND_DIR = $path
        $frontend_found = $true
        break
    }
}

if ($frontend_found) {
    $frontend_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'FRONTEND - PORT 5173' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''

cd '$FRONTEND_DIR'

# Check if npm packages are installed
if (-not (Test-Path 'node_modules')) {
    Write-Host 'Installing dependencies...' -ForegroundColor Yellow
    npm install
}

Write-Host 'Starting frontend...' -ForegroundColor Yellow
npm run dev

if (`$LASTEXITCODE -ne 0) {
    Write-Host 'Frontend crashed!' -ForegroundColor Red
    pause
}
"@
    
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontend_script
    Write-Host "   Frontend starting from: $FRONTEND_DIR" -ForegroundColor Gray
} else {
    Write-Host "   ⚠️ Frontend directory not found" -ForegroundColor Yellow
}

# Step 7: Start Caddy WebSocket Proxy
Write-Host "3️⃣ Starting WebSocket Proxy..." -ForegroundColor Yellow

# Start Caddy WebSocket Proxy on 8088
if (Test-Path "D:\MCP Mods\HAK_GAL_HEXAGONAL\Caddyfile") {
    Write-Host "   Starting Caddy WebSocket Proxy on port 8088..." -ForegroundColor Gray
    $caddy_script = @"
cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
caddy run --config Caddyfile
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $caddy_script
} elseif (Test-Path "D:\MCP Mods\HAK_GAL_SUITE\api_8088.py") {
    Write-Host "   Starting fallback service on port 8088..." -ForegroundColor Gray
    $service_script = @"
cd 'D:\MCP Mods\HAK_GAL_SUITE'
python api_8088.py
"@
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $service_script
}

# Step 8: Health check
Write-Host ""
Write-Host "⏳ Waiting for services to start..." -ForegroundColor Yellow
Start-Sleep -Seconds 5

Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

$services = @{
    "HAK-GAL API (5002)" = 5002
    "Frontend (5173)" = 5173
    "Caddy Proxy (8088)" = 8088
    "Ollama (11434)" = 11434
}

$all_healthy = $true
foreach ($service in $services.GetEnumerator()) {
    if (Test-Port $service.Value) {
        Write-Host "✅ $($service.Key) is responding" -ForegroundColor Green
    } else {
        if ($service.Value -eq 5002) {
            Write-Host "❌ $($service.Key) NOT RESPONDING!" -ForegroundColor Red
            $all_healthy = $false
        } else {
            Write-Host "⚠️  $($service.Key) not responding" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "📊 SUMMARY - EVERYTHING ON PORT 5002" -ForegroundColor Yellow
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Database: hexagonal_kb.db (5911 facts)" -ForegroundColor Green
Write-Host "API:      http://localhost:5002 ✅ ALL SERVICES HERE" -ForegroundColor White
Write-Host "          - Governor (integrated)" -ForegroundColor Gray
Write-Host "          - Reasoning Engine" -ForegroundColor Gray
Write-Host "          - WebSocket Server" -ForegroundColor Gray
Write-Host "Proxy:    http://localhost:8088 (WebSocket relay)" -ForegroundColor White
Write-Host "Frontend: http://localhost:5173" -ForegroundColor White
Write-Host ""

if ($all_healthy) {
    Write-Host "🎉 SYSTEM READY! Opening browser..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:5173"
} else {
    Write-Host "⚠️  Some services may still be starting..." -ForegroundColor Yellow
    Write-Host "   Wait a moment and refresh the browser" -ForegroundColor Gray
    Write-Host ""
    Write-Host "   If API is not starting, check:" -ForegroundColor Yellow
    Write-Host "   1. Database path is correct" -ForegroundColor Gray
    Write-Host "   2. Python environment is activated" -ForegroundColor Gray
    Write-Host "   3. No errors in API window" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit launcher (services continue running)..." -ForegroundColor Cyan
pause
