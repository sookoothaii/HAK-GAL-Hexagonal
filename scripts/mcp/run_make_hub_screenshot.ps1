Param(
    [string]$PythonPath = ".\.venv_hexa\\Scripts\\python.exe"
)

$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
try {
    Set-Location ..\..
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUNBUFFERED = '1'
    if (-not (Test-Path $PythonPath)) { throw "Python nicht gefunden: $PythonPath" }
    & $PythonPath scripts\mcp\make_hub_screenshot.py | Out-Host
}
finally {
    Pop-Location
}


