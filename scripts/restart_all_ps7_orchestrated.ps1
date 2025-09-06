param(
    [int]$DelayBetweenStartsSec = 2,
    [int]$FinalWaitSec = 3
)

$ErrorActionPreference = 'Stop'

# --- Konfiguration ---
$root     = 'D:\MCP Mods\HAK_GAL_HEXAGONAL'
$frontend = Join-Path $root 'frontend'
$caddyExe = Join-Path $root 'caddy.exe'
$caddyCfg = Join-Path $root 'Caddyfile'

$ports = 5001,5002,5173,8088

function Stop-PortListeners {
  param([int[]]$Ports)
  Write-Host "[STOP] Ports: $($Ports -join ', ')" -ForegroundColor Yellow
  $pids = @()
  foreach ($p in $Ports) {
    try {
      $pid = (Get-NetTCPConnection -LocalPort $p -State Listen -ErrorAction SilentlyContinue | Select-Object -First 1 -ExpandProperty OwningProcess)
      if ($pid) { $pids += $pid }
    } catch {}
  }
  $pids = $pids | Sort-Object -Unique
  if ($pids.Count -gt 0) {
    Write-Host "[STOP] Killing PIDs: $($pids -join ', ')" -ForegroundColor Yellow
    foreach ($pid in $pids) { Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue }
  } else {
    Write-Host "[STOP] Keine Listener gefunden." -ForegroundColor DarkYellow
  }
}

function Stop-ProjectPython {
  Write-Host "[STOP] Suche Python-Prozesse des Projekts..." -ForegroundColor Yellow
  $procs = Get-CimInstance Win32_Process |
    Where-Object { $_.Name -match 'python' -and $_.CommandLine -match 'HAK_GAL_HEXAGONAL' }
  if ($procs) {
    $procs | ForEach-Object {
      Write-Host ("[STOP] PID {0} : {1}" -f $_.ProcessId, $_.CommandLine) -ForegroundColor Yellow
      Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue
    }
  } else {
    Write-Host "[STOP] Keine Python-Prozesse des Projekts gefunden." -ForegroundColor DarkYellow
  }
}

function Stop-CaddyAndVite {
  Get-Process caddy -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
  Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'vite' } | ForEach-Object { Stop-Process -Id $_.ProcessId -Force -ErrorAction SilentlyContinue }
}

# --- Stop-Phase ---
Stop-PortListeners -Ports $ports
Stop-ProjectPython
Stop-CaddyAndVite

# --- Start-Phase ---
Write-Host "[START] 5001 (NO_WEBSOCKET)" -ForegroundColor Cyan
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; if (Test-Path .\.venv_hexa\Scripts\Activate.ps1) { . .\.venv_hexa\Scripts\Activate.ps1 }; python diagnostic_scripts\launch_NO_WEBSOCKET.py; Read-Host '5001 beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $root
Start-Sleep -Seconds $DelayBetweenStartsSec

Write-Host "[START] 5002 (WRITE)" -ForegroundColor Cyan
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; if (Test-Path .\.venv_hexa\Scripts\Activate.ps1) { . .\.venv_hexa\Scripts\Activate.ps1 }; python scripts\launch_5002_WRITE.py; Read-Host '5002 beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $root
Start-Sleep -Seconds $DelayBetweenStartsSec

Write-Host "[START] Frontend (5173)" -ForegroundColor Cyan
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$frontend'; npm run dev; Read-Host 'Frontend beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $frontend
Start-Sleep -Seconds $DelayBetweenStartsSec

Write-Host "[START] Proxy (Caddy 8088)" -ForegroundColor Cyan
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; pwsh -NoProfile -File '$root\scripts\start_caddy.ps1' -Foreground"
) -WindowStyle Normal -WorkingDirectory $root

# --- Health-Checks ---
Start-Sleep -Seconds $FinalWaitSec
Write-Host "[CHECK] Proxy /health" -ForegroundColor Green
try { (Invoke-RestMethod http://127.0.0.1:8088/health -TimeoutSec 3) | ConvertTo-Json -Compress | Write-Host } catch { Write-Warning $_ }
Write-Host "[CHECK] Facts Count" -ForegroundColor Green
try { (Invoke-RestMethod http://127.0.0.1:8088/api/facts/count -TimeoutSec 3) | ConvertTo-Json -Compress | Write-Host } catch { Write-Warning $_ }

