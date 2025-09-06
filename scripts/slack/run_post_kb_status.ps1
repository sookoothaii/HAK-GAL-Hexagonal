Param(
    [Parameter(Mandatory=$true)] [string]$WebhookUrl,
    [string]$PythonPath = ".\.venv_hexa\\Scripts\\python.exe"
)

$ErrorActionPreference = 'Stop'
Push-Location (Split-Path -Parent $MyInvocation.MyCommand.Path)
try {
    Set-Location ..\..
    $env:SLACK_WEBHOOK_URL = $WebhookUrl
    $env:PYTHONIOENCODING = 'utf-8'
    $env:PYTHONUNBUFFERED = '1'
    if (-not (Test-Path $PythonPath)) { throw "Python nicht gefunden: $PythonPath" }
    & $PythonPath scripts\slack\post_kb_status.py | Out-Host
}
finally {
    Pop-Location
}


