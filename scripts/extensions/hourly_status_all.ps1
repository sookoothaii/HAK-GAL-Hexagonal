Param(
	[int]$GoldenLimit = 5000
)
$ErrorActionPreference = 'Stop'

# Pfade
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."  # Projektwurzel
$root = Get-Location

# 5001/5002: bestehenden Runner nutzen
Write-Host "[A/3] 5001/5002 hourly runner"
& powershell -NoProfile -ExecutionPolicy Bypass -File "$here\hourly_status_runner.ps1" -Api5001 'http://127.0.0.1:5001' -Api5002 'http://127.0.0.1:5002' -GoldenLimit $GoldenLimit | Out-Host

# Venv-Python
$py = Join-Path $root '.venv_hexa/ScriptS/python.exe'
if (-not (Test-Path $py)) { $py = Join-Path $root '.venv_hexa/Scripts/python.exe' }
if (-not (Test-Path $py)) { throw "Python venv nicht gefunden: $py" }

# Zeitstempel
$ts = (Get-Date).ToString('yyyyMMdd_HHmm')

# 5003: Snapshot + Golden (read-only)
Write-Host "[B/3] 5003 snapshot"
& $py 'scripts/extensions/auto_snapshot_status.py' --api 'http://127.0.0.1:5003' --out "PROJECT_HUB/SNAPSHOT_5003_$ts.md" | Out-Host

Write-Host "[C/3] 5003 golden (limit=$GoldenLimit)"
$env:PYTHONPATH = (Join-Path $root 'native\mojo_kernels\build\Release') + ';' + ($env:PYTHONPATH)
& $py 'scripts/extensions/golden_mojo_vs_python.py' --api 'http://127.0.0.1:5003' --limit $GoldenLimit --out "PROJECT_HUB/REPORT_MOJO_GOLDEN_5003_$ts.md" | Out-Host

# Zusammenfassung schreiben
$summary = "PROJECT_HUB/AUTO_HOURLY_STATUS_ALL_$ts.md"
$lines = @()
$lines += "# AUTO HOURLY STATUS ALL ($ts)"
$lines += ""
$lines += "- 5001/5002 Runner ausgeführt"
$lines += "- 5003 Snapshot: PROJECT_HUB/SNAPSHOT_5003_$ts.md"
$lines += "- 5003 Golden:  PROJECT_HUB/REPORT_MOJO_GOLDEN_5003_$ts.md"
$lines += ""
$lines += "Alle Operationen sind read-only; keine Schreibpfade berührt."
Set-Content -LiteralPath $summary -Value ($lines -join "`n") -Encoding UTF8

Write-Host "[OK] Hourly status all written:" $summary


