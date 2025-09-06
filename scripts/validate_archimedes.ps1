$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location -LiteralPath '..'

if (-not (Test-Path '.\.venv_hexa\Scripts\Activate.ps1')) { throw 'venv not found: .\.venv_hexa' }
& .\.venv_hexa\Scripts\Activate.ps1

Write-Host 'Running Archimedes outputs validation...'
python .\validate_archimedes_outputs.py
if ($LASTEXITCODE -ne 0) { throw "Validation failed with code $LASTEXITCODE" }
Write-Host 'Validation OK.'






