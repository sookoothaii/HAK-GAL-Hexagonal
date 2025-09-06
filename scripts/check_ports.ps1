# HAK-GAL Port Status Check
# ========================
# Ensures everything runs on 5002

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "HAK-GAL PORT STATUS CHECK" -ForegroundColor Yellow
Write-Host "Everything should be on PORT 5002!" -ForegroundColor Green
Write-Host "============================================`n" -ForegroundColor Cyan

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

# Check correct ports
Write-Host "CORRECT CONFIGURATION:" -ForegroundColor Green
Write-Host "---------------------" -ForegroundColor Gray

if (Test-Port 5002) {
    Write-Host "✅ Port 5002: HAK-GAL API (Governor+Reasoning+WebSocket)" -ForegroundColor Green
} else {
    Write-Host "❌ Port 5002: NOT RUNNING - This is the MAIN service!" -ForegroundColor Red
}

if (Test-Port 8088) {
    Write-Host "✅ Port 8088: Caddy Proxy (WebSocket relay)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port 8088: Not running (WebSocket proxy)" -ForegroundColor Yellow
}

if (Test-Port 5173) {
    Write-Host "✅ Port 5173: Frontend (Vite)" -ForegroundColor Green
} else {
    Write-Host "⚠️  Port 5173: Not running (Frontend)" -ForegroundColor Yellow
}

Write-Host "`nPROBLEMATIC PORTS (should NOT be running):" -ForegroundColor Red
Write-Host "-------------------------------------------" -ForegroundColor Gray

# Check wrong ports
if (Test-Port 5000) {
    Write-Host "❌ Port 5000: RUNNING (Wrong! Old API port)" -ForegroundColor Red
    Write-Host "   Kill this process immediately!" -ForegroundColor Yellow
} else {
    Write-Host "✅ Port 5000: Not running (Good!)" -ForegroundColor Green
}

if (Test-Port 5001) {
    Write-Host "❌ Port 5001: RUNNING (Wrong! Old Governor port)" -ForegroundColor Red
    Write-Host "   Governor should be integrated in 5002!" -ForegroundColor Yellow
} else {
    Write-Host "✅ Port 5001: Not running (Good!)" -ForegroundColor Green
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "SUMMARY:" -ForegroundColor Yellow

$all_good = $true

if (-not (Test-Port 5002)) {
    Write-Host "❌ CRITICAL: Main API on 5002 is not running!" -ForegroundColor Red
    $all_good = $false
}

if (Test-Port 5000 -or Test-Port 5001) {
    Write-Host "⚠️  WARNING: Old services running on wrong ports!" -ForegroundColor Yellow
    Write-Host "   Stop all services and use START_FIXED.bat" -ForegroundColor Yellow
    $all_good = $false
}

if ($all_good -and (Test-Port 5002)) {
    Write-Host "✅ PERFECT! Everything runs on 5002 as expected!" -ForegroundColor Green
    Write-Host "   API URL: http://localhost:5002" -ForegroundColor Gray
}

Write-Host "============================================`n" -ForegroundColor Cyan
