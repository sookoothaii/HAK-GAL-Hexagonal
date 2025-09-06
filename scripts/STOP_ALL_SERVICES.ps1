# ============================================
# HAK-GAL Stop All Services
# ============================================
# Stops all running HAK-GAL services
# ============================================

Write-Host "🛑 STOPPING HAK-GAL SERVICES" -ForegroundColor Red
Write-Host "=============================" -ForegroundColor Yellow

# Function to stop process on port
function Stop-ServiceOnPort {
    param(
        [int]$Port,
        [string]$ServiceName
    )
    
    try {
        $processes = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue | 
                     Select-Object -ExpandProperty OwningProcess -Unique
        
        if ($processes) {
            foreach ($pid in $processes) {
                $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Stopping $ServiceName on port $Port (PID: $pid)..." -ForegroundColor Yellow
                    Stop-Process -Id $pid -Force
                    Write-Host "  ✅ Stopped" -ForegroundColor Green
                }
            }
        } else {
            Write-Host "  ℹ️ No service running on port $Port" -ForegroundColor Gray
        }
    } catch {
        Write-Host "  ⚠️ Could not stop service on port $Port" -ForegroundColor Yellow
    }
}

# Stop all services
Write-Host ""
Stop-ServiceOnPort -Port 5002 -ServiceName "HAK-GAL API"
Stop-ServiceOnPort -Port 5173 -ServiceName "Frontend"
Stop-ServiceOnPort -Port 8088 -ServiceName "Additional Service"
Stop-ServiceOnPort -Port 5001 -ServiceName "Governor"
Stop-ServiceOnPort -Port 5000 -ServiceName "Legacy Service"

# Optional: Stop Ollama
Write-Host ""
Write-Host "Stop Ollama? (Y/N): " -ForegroundColor Yellow -NoNewline
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    Stop-ServiceOnPort -Port 11434 -ServiceName "Ollama"
}

# Kill any remaining Python/Node processes related to HAK-GAL
Write-Host ""
Write-Host "Cleaning up remaining processes..." -ForegroundColor Yellow

Get-Process python* -ErrorAction SilentlyContinue | 
    Where-Object { $_.Path -like "*HAK_GAL*" } | 
    Stop-Process -Force -ErrorAction SilentlyContinue

Get-Process node* -ErrorAction SilentlyContinue | 
    Where-Object { $_.Path -like "*HAK_GAL*" } | 
    Stop-Process -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "✅ All HAK-GAL services stopped!" -ForegroundColor Green
Write-Host ""
pause
