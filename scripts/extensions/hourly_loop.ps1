Param(
	[int]$GoldenLimit = 5000,
	[int]$IntervalMinutes = 60
)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."

Write-Host "[Loop] Starting hourly loop (Interval=$IntervalMinutes min)"
while ($true) {
	try {
		& powershell -NoProfile -ExecutionPolicy Bypass -File "$here/hourly_status_all.ps1" -GoldenLimit $GoldenLimit | Out-Host
	} catch {
		Write-Warning $_
	}
	Start-Sleep -Seconds ([Math]::Max(60, $IntervalMinutes * 60))
}


