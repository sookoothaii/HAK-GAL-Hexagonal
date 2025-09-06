Param(
	[string]$Api = 'http://127.0.0.1:5001',
	[int]$Limit = 2000,
	[string]$Out = 'PROJECT_HUB/REPORT_MOJO_BENCHMARK.md',
	[switch]$EnableMojo = $false
)

$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."

if ($EnableMojo) {
	# Nur für diesen Prozess setzen
	$env:MOJO_ENABLED = 'true'
	$env:PYTHONPATH = (Join-Path (Get-Location) 'src_hexagonal') + ';' + ($env:PYTHONPATH)
	Write-Host "[Env] MOJO_ENABLED=true"
	Write-Host "[Env] PYTHONPATH=$($env:PYTHONPATH)"
}

# Python in lokaler Hex-Venv bevorzugen, sonst System-Python
$py = Join-Path (Get-Location) '.venv_hexa/ScriptS/python.exe'
if (-not (Test-Path $py)) {
	$py = Join-Path (Get-Location) '.venv_hexa/Scripts/python.exe'
}
if (-not (Test-Path $py)) {
	$py = 'python'
}

Write-Host "[Run] Using python: $py"
Write-Host "[Run] API: $Api | Limit: $Limit | Out: $Out"

& $py 'scripts/extensions/benchmark_mojo_adapter.py' --api $Api --limit $Limit --out $Out | Write-Host

if (Test-Path $Out) {
	Write-Host "[OK] Report written: $Out"
} else {
	Write-Warning "Report was not written: $Out"
}
