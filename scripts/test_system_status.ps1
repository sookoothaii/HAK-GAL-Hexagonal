param(
    [string]$Url = 'http://127.0.0.1:8088/health'
)

try {
    $response = Invoke-RestMethod -Uri $Url -Method GET -TimeoutSec 2
    Write-Host "✅ System is running on 8088" -ForegroundColor Green
    Write-Host ($response | ConvertTo-Json -Compress)
    exit 0
} catch {
    Write-Host "❌ System is not running on 8088" -ForegroundColor Red
    Write-Host "Error: $_" -ForegroundColor Yellow
    exit 1
}
