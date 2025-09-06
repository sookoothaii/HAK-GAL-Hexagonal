# ============================================
# HAK-GAL Complete System Launcher
# ============================================
# Starts all required services in separate windows
# Ports: 5002 (API), 5173 (Frontend), 8088 (Additional Service)
# ============================================

param(
    [switch]$NoOllama = $false,
    [switch]$Debug = $false
)

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "🚀 HAK-GAL COMPLETE SYSTEM LAUNCHER" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Get current directory
$ROOT_DIR = Get-Location
$HEXAGONAL_DIR = Join-Path $ROOT_DIR "HAK_GAL_HEXAGONAL"
$FRONTEND_DIR = Join-Path $ROOT_DIR "HAK_GAL_SUITE\flask_frontend"
$ADDITIONAL_DIR = Join-Path $ROOT_DIR "HAK_GAL_SUITE"

# Check if running from correct location
if (-not (Test-Path "src_hexagonal")) {
    Write-Host "⚠️  Warning: Not in HAK_GAL_HEXAGONAL directory" -ForegroundColor Yellow
    if (Test-Path $HEXAGONAL_DIR) {
        Write-Host "📁 Switching to: $HEXAGONAL_DIR" -ForegroundColor Yellow
        Set-Location $HEXAGONAL_DIR
        $ROOT_DIR = Get-Location
    } else {
        Write-Host "❌ Error: Cannot find HAK_GAL_HEXAGONAL directory!" -ForegroundColor Red
        Write-Host "   Please run this script from the HAK_GAL_HEXAGONAL folder" -ForegroundColor Red
        pause
        exit 1
    }
}

# Function to check if port is in use
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

# Function to kill process on port
function Stop-ProcessOnPort {
    param($Port)
    try {
        $processId = (Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue).OwningProcess | Select-Object -Unique
        if ($processId) {
            Stop-Process -Id $processId -Force -ErrorAction SilentlyContinue
            Write-Host "✅ Stopped process on port $Port" -ForegroundColor Green
            Start-Sleep -Seconds 1
        }
    } catch {
        # Silently continue if no process found
    }
}

# Check Python environment
Write-Host "🐍 Checking Python environment..." -ForegroundColor Yellow
if (Test-Path ".venv_hexa\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment found: .venv_hexa" -ForegroundColor Green
    $PYTHON = ".\.venv_hexa\Scripts\python.exe"
    $ACTIVATE = ".\.venv_hexa\Scripts\Activate.ps1"
} elseif (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "✅ Virtual environment found: venv" -ForegroundColor Green
    $PYTHON = ".\venv\Scripts\python.exe"
    $ACTIVATE = ".\venv\Scripts\Activate.ps1"
} else {
    Write-Host "⚠️  No virtual environment found, using system Python" -ForegroundColor Yellow
    $PYTHON = "python"
    $ACTIVATE = $null
}

# Check Node/NPM
Write-Host "📦 Checking Node.js/NPM..." -ForegroundColor Yellow
try {
    $npmVersion = npm --version 2>$null
    Write-Host "✅ NPM version: $npmVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ NPM not found! Please install Node.js" -ForegroundColor Red
    Write-Host "   Download from: https://nodejs.org/" -ForegroundColor Yellow
    pause
    exit 1
}

# Check Ollama (unless -NoOllama flag is set)
if (-not $NoOllama) {
    Write-Host "🤖 Checking Ollama..." -ForegroundColor Yellow
    if (Test-Port 11434) {
        Write-Host "✅ Ollama is running on port 11434" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Ollama not running, attempting to start..." -ForegroundColor Yellow
        try {
            Start-Process "ollama" -ArgumentList "serve" -WindowStyle Hidden
            Start-Sleep -Seconds 2
            if (Test-Port 11434) {
                Write-Host "✅ Ollama started successfully" -ForegroundColor Green
            } else {
                Write-Host "⚠️  Could not start Ollama - continuing anyway" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "⚠️  Ollama not installed or cannot start - continuing anyway" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "🔍 Checking port availability..." -ForegroundColor Yellow

# Check and clear ports
$ports = @(5002, 5173, 8088, 5001, 5000)
foreach ($port in $ports) {
    if (Test-Port $port) {
        Write-Host "⚠️  Port $port is in use, attempting to free it..." -ForegroundColor Yellow
        Stop-ProcessOnPort $port
    } else {
        Write-Host "✅ Port $port is available" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "🚀 Starting services..." -ForegroundColor Cyan
Write-Host ""

# Service 1: HAK-GAL Hexagonal API (Port 5002)
Write-Host "1️⃣ Starting HAK-GAL API on port 5002..." -ForegroundColor Yellow
$api_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'HAK-GAL HEXAGONAL API - PORT 5002' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
cd '$ROOT_DIR'
$(if ($ACTIVATE) { "& '$ACTIVATE'" } else { "" })
Write-Host 'Starting API...' -ForegroundColor Yellow
& '$PYTHON' src_hexagonal\hexagonal_api_enhanced_clean.py
if (`$LASTEXITCODE -ne 0) {
    Write-Host 'API crashed! Check the error above.' -ForegroundColor Red
    pause
}
"@

Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $api_script

# Wait for API to start
Write-Host "   Waiting for API to start..." -ForegroundColor Gray
Start-Sleep -Seconds 3

# Service 2: Frontend (Port 5173)
Write-Host "2️⃣ Starting Frontend on port 5173..." -ForegroundColor Yellow

# Try multiple frontend locations
$frontend_paths = @(
    (Join-Path $ROOT_DIR "frontend"),
    (Join-Path $ROOT_DIR "..\HAK_GAL_SUITE\flask_frontend"),
    (Join-Path $ROOT_DIR "..\frontend"),
    $FRONTEND_DIR
)

$frontend_found = $false
foreach ($path in $frontend_paths) {
    if (Test-Path $path) {
        $FRONTEND_DIR = $path
        $frontend_found = $true
        Write-Host "   Found frontend at: $FRONTEND_DIR" -ForegroundColor Gray
        break
    }
}

if ($frontend_found) {
    # Check if package.json exists
    if (Test-Path (Join-Path $FRONTEND_DIR "package.json")) {
        $frontend_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'FRONTEND - PORT 5173' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
cd '$FRONTEND_DIR'
Write-Host 'Installing dependencies...' -ForegroundColor Yellow
npm install --silent
Write-Host 'Starting development server...' -ForegroundColor Yellow
npm run dev
if (`$LASTEXITCODE -ne 0) {
    Write-Host 'Frontend crashed! Check the error above.' -ForegroundColor Red
    pause
}
"@
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $frontend_script
        Write-Host "   Frontend starting..." -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️ No package.json found in frontend directory" -ForegroundColor Yellow
    }
} else {
    Write-Host "   ⚠️ Frontend directory not found - skipping" -ForegroundColor Yellow
}

# Service 3: Additional Service (Port 8088)
Write-Host "3️⃣ Starting Additional Service on port 8088..." -ForegroundColor Yellow

# Check for various possible services on 8088
$service_8088_found = $false

# Option 1: Check for a specific Python service
$service_paths = @(
    (Join-Path $ROOT_DIR "service_8088.py"),
    (Join-Path $ROOT_DIR "..\HAK_GAL_SUITE\api_8088.py"),
    (Join-Path $ROOT_DIR "src_hexagonal\api_8088.py")
)

foreach ($path in $service_paths) {
    if (Test-Path $path) {
        $service_8088_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'ADDITIONAL SERVICE - PORT 8088' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
cd '$(Split-Path $path -Parent)'
$(if ($ACTIVATE) { "& '$ACTIVATE'" } else { "" })
Write-Host 'Starting service on port 8088...' -ForegroundColor Yellow
& '$PYTHON' '$path'
if (`$LASTEXITCODE -ne 0) {
    Write-Host 'Service crashed! Check the error above.' -ForegroundColor Red
    pause
}
"@
        Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $service_8088_script
        $service_8088_found = $true
        Write-Host "   Service starting from: $path" -ForegroundColor Gray
        break
    }
}

if (-not $service_8088_found) {
    Write-Host "   ⚠️ No service found for port 8088 - skipping" -ForegroundColor Yellow
    Write-Host "   To add a service on 8088, create service_8088.py" -ForegroundColor Gray
}

# Service 4: Governor on Port 5001 (Optional)
Write-Host "4️⃣ Checking Governor Service on port 5001..." -ForegroundColor Yellow
if (Test-Path (Join-Path $ROOT_DIR "..\HAK_GAL_SUITE\launch_5001_READONLY_STABLE_PORT.py")) {
    $governor_script = @"
Write-Host '============================================' -ForegroundColor Cyan
Write-Host 'GOVERNOR SERVICE - PORT 5001' -ForegroundColor Green
Write-Host '============================================' -ForegroundColor Cyan
Write-Host ''
cd '$(Join-Path $ROOT_DIR "..\HAK_GAL_SUITE")'
$(if ($ACTIVATE) { "& '$ACTIVATE'" } else { "" })
Write-Host 'Starting Governor...' -ForegroundColor Yellow
& '$PYTHON' launch_5001_READONLY_STABLE_PORT.py
if (`$LASTEXITCODE -ne 0) {
    Write-Host 'Governor crashed! Check the error above.' -ForegroundColor Red
    pause
}
"@
    Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-Command", $governor_script
    Write-Host "   Governor starting..." -ForegroundColor Gray
} else {
    Write-Host "   ⚠️ Governor service not found - skipping" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "✅ ALL SERVICES LAUNCHED!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "📊 Service Status:" -ForegroundColor Yellow
Write-Host "   API:        http://localhost:5002" -ForegroundColor White
Write-Host "   Frontend:   http://localhost:5173" -ForegroundColor White
Write-Host "   Service:    http://localhost:8088" -ForegroundColor White
Write-Host "   Governor:   http://localhost:5001" -ForegroundColor White
Write-Host "   Ollama:     http://localhost:11434" -ForegroundColor White
Write-Host ""
Write-Host "💡 Tips:" -ForegroundColor Yellow
Write-Host "   - Each service runs in its own window" -ForegroundColor Gray
Write-Host "   - Close individual windows to stop services" -ForegroundColor Gray
Write-Host "   - Run with -NoOllama to skip Ollama check" -ForegroundColor Gray
Write-Host "   - Run with -Debug for verbose output" -ForegroundColor Gray
Write-Host ""
Write-Host "🔍 Checking service health..." -ForegroundColor Yellow

# Wait a moment for services to start
Start-Sleep -Seconds 5

# Health checks
$healthy = $true

if (Test-Port 5002) {
    Write-Host "✅ API is responding on port 5002" -ForegroundColor Green
} else {
    Write-Host "⚠️  API not responding yet on port 5002" -ForegroundColor Yellow
    $healthy = $false
}

if (Test-Port 5173) {
    Write-Host "✅ Frontend is responding on port 5173" -ForegroundColor Green
} else {
    Write-Host "⚠️  Frontend not responding yet on port 5173" -ForegroundColor Yellow
}

if (Test-Port 8088) {
    Write-Host "✅ Additional service is responding on port 8088" -ForegroundColor Green
} else {
    Write-Host "⚠️  No service responding on port 8088" -ForegroundColor Gray
}

if (Test-Port 5001) {
    Write-Host "✅ Governor is responding on port 5001" -ForegroundColor Green
}

Write-Host ""
if ($healthy) {
    Write-Host "🎉 System is ready! Opening browser..." -ForegroundColor Green
    Start-Sleep -Seconds 2
    Start-Process "http://localhost:5173"
} else {
    Write-Host "⚠️  Some services may still be starting..." -ForegroundColor Yellow
    Write-Host "   Wait a few seconds and refresh the browser" -ForegroundColor Gray
}

Write-Host ""
Write-Host "Press any key to exit this launcher (services will continue running)..." -ForegroundColor Cyan
pause
