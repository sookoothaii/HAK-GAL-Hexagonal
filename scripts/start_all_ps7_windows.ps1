$ErrorActionPreference = 'Stop'

# Wurzelpfad
$root = 'D:\MCP Mods\HAK_GAL_HEXAGONAL'

# 1) 5001 – Hexagonal API (WS aus)
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; if (Test-Path .\.venv_hexa\Scripts\Activate.ps1) { . .\.venv_hexa\Scripts\Activate.ps1 }; python diagnostic_scripts\launch_NO_WEBSOCKET.py; Read-Host '5001 beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $root

Start-Sleep -Seconds 1

# 2) 5002 – Read-only + WS
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; if (Test-Path .\.venv_hexa\Scripts\Activate.ps1) { . .\.venv_hexa\Scripts\Activate.ps1 }; python diagnostic_scripts\launch_5002_FIXED.py; Read-Host '5002 beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $root

Start-Sleep -Seconds 1

# 3) Frontend (5173)
$frontend = Join-Path $root 'frontend'
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$frontend'; npm run dev; Read-Host 'Frontend beendet – Taste drücken'"
) -WindowStyle Normal -WorkingDirectory $frontend

Start-Sleep -Seconds 1

# 4) Proxy (8088)
Start-Process pwsh -ArgumentList @(
  '-NoProfile','-Command',
  "Set-Location '$root'; pwsh -NoProfile -File '$root\scripts\start_caddy.ps1' -Foreground"
) -WindowStyle Normal -WorkingDirectory $root

Write-Host 'Alle Komponenten wurden in separaten Fenstern gestartet.' -ForegroundColor Green

