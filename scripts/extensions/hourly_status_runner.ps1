Param(
	[string]$Api5001 = 'http://127.0.0.1:5001',
	[string]$Api5002 = 'http://127.0.0.1:5002',
	[int]$GoldenLimit = 1000
)
$ErrorActionPreference = 'Stop'

# Pfade
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."  # Projektwurzel
$root = Get-Location
$py = Join-Path $root '.venv_hexa/ScriptS/python.exe'
if (-not (Test-Path $py)) { $py = Join-Path $root '.venv_hexa/Scripts/python.exe' }
if (-not (Test-Path $py)) { throw "Python venv nicht gefunden: $py" }

# Zeitstempel
$ts = (Get-Date).ToString('yyyyMMdd_HHmm')

# Ausgabedateien
$out5001 = "PROJECT_HUB/SNAPSHOT_5001_$ts.md"
$out5002 = "PROJECT_HUB/SNAPSHOT_5002_$ts.md"
$golden = "PROJECT_HUB/REPORT_MOJO_GOLDEN_5002_$ts.md"
$summary = "PROJECT_HUB/AUTO_HOURLY_STATUS_$ts.md"

Write-Host "[1/3] Snapshot 5001 -> $out5001"
& $py 'scripts/extensions/auto_snapshot_status.py' --api $Api5001 --out $out5001 | Out-Host

Write-Host "[2/3] Snapshot 5002 -> $out5002"
& $py 'scripts/extensions/auto_snapshot_status.py' --api $Api5002 --out $out5002 | Out-Host

Write-Host "[3/3] Golden 5002 (limit=$GoldenLimit) -> $golden"
& $py 'scripts/extensions/golden_mojo_vs_python.py' --api $Api5002 --limit $GoldenLimit --out $golden | Out-Host

# Zusammenfassung schreiben
$lines = @()
$lines += "# AUTO HOURLY STATUS ($ts)"
$lines += ""
$lines += "- 5001 Snapshot: $out5001"
$lines += "- 5002 Snapshot: $out5002"
$lines += "- Golden 5002: $golden"
$lines += ""
$lines += "Diese Artefakte sind read-only erzeugt; keine Schreibpfade berührt."
Set-Content -LiteralPath $summary -Value ($lines -join "`n") -Encoding UTF8

Write-Host "[OK] Hourly status written:" $summary
