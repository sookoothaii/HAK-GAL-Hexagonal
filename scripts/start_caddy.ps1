param(
    [switch]$Foreground,
    [int]$WaitSeconds = 3
)

$ErrorActionPreference = 'Stop'
$exe = 'D:\MCP Mods\HAK_GAL_HEXAGONAL\caddy.exe'
$cfg = 'D:\MCP Mods\HAK_GAL_HEXAGONAL\Caddyfile'
$logOut = 'D:\MCP Mods\HAK_GAL_HEXAGONAL\caddy_out.log'
$logErr = 'D:\MCP Mods\HAK_GAL_HEXAGONAL\caddy_err.log'

if (-not (Test-Path $exe)) { Write-Error "caddy.exe not found at $exe" }
if (-not (Test-Path $cfg)) { Write-Error "Caddyfile not found at $cfg" }

# Optional: Validierung
try {
  & $exe validate --config $cfg | Out-Null
} catch {
  Write-Host "Caddyfile validation failed:" -ForegroundColor Red
  throw
}

# Falls bereits läuft, beenden
Get-Process caddy -ErrorAction SilentlyContinue | Stop-Process -Force

if ($Foreground) {
  Write-Host "Starting Caddy in FOREGROUND (Ctrl+C zum Beenden)..." -ForegroundColor Cyan
  & $exe run --config $cfg --watch
} else {
  Write-Host "Starting Caddy in BACKGROUND..." -ForegroundColor Cyan
  Start-Process -FilePath $exe -ArgumentList @('run','--config',$cfg,'--watch') -RedirectStandardOutput $logOut -RedirectStandardError $logErr -WindowStyle Hidden
  Start-Sleep -Seconds $WaitSeconds
  $listening = $false
  try {
    $conn = Test-NetConnection -ComputerName 127.0.0.1 -Port 8088 -WarningAction SilentlyContinue
    $listening = [bool]$conn.TcpTestSucceeded
  } catch {}

  if ($listening) {
    Write-Host "Caddy started with $cfg (port 8088)" -ForegroundColor Green
  } else {
    Write-Warning "Caddy scheint nicht zu laufen (Port 8088 nicht erreichbar). Zeige letzte Logzeilen:"
    if (Test-Path $logOut) { Write-Host "--- caddy_out.log (tail) ---" -ForegroundColor Yellow; Get-Content $logOut -Tail 50 }
    if (Test-Path $logErr) { Write-Host "--- caddy_err.log (tail) ---" -ForegroundColor Yellow; Get-Content $logErr -Tail 50 }
    Write-Host "Tipp: Foreground starten für direkte Fehlermeldung:" -ForegroundColor Yellow
    Write-Host "`n  cd 'D:\MCP Mods\HAK_GAL_HEXAGONAL'`n  .\caddy.exe run --config .\Caddyfile --watch`n" -ForegroundColor Gray
  }
}
