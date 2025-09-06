Param(
    [switch]$Mojo = $true,
    [switch]$Validate = $true,
    [switch]$Dupes = $false,
    [string]$DbUri = 'file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared',
    [int]$Port = 5002,
    [int]$HealthTimeoutSec = 20,
    [switch]$ReadWrite = $false
)
$ErrorActionPreference = 'Stop'

function Stop-PortProcess {
    param([int]$Port)
    try {
        $p = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1 -ExpandProperty OwningProcess
        if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 2 }
    } catch {}
}

function Wait-Health {
    param([string]$Url, [int]$TimeoutSec)
    $deadline = (Get-Date).AddSeconds($TimeoutSec)
    while ((Get-Date) -lt $deadline) {
        try {
            $h = Invoke-RestMethod -Uri "$Url/health" -Method GET -TimeoutSec 2
            if ($h.status -eq 'operational') { return $true }
        } catch { Start-Sleep -Milliseconds 500 }
    }
    return $false
}

# Move to project root
$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."
$root = Get-Location

# Ensure venv python
$py = Join-Path $root '.venv_hexa/ScriptS/python.exe'
if (-not (Test-Path $py)) { $py = Join-Path $root '.venv_hexa/Scripts/python.exe' }
if (-not (Test-Path $py)) { throw "Python venv nicht gefunden: $py" }

# Stop existing on port
Stop-PortProcess -Port $Port

# Prepare logs
$logDir = Join-Path $root 'logs'
if (-not (Test-Path $logDir)) { New-Item -ItemType Directory -Path $logDir | Out-Null }
$out = Join-Path $logDir "server${Port}.out.txt"
$err = Join-Path $logDir "server${Port}.err.txt"

# Compose environment for child process
$pydDir = Join-Path $root 'native\mojo_kernels\build\Release'
if (Test-Path $pydDir) { $env:PYTHONPATH = "$pydDir;$env:PYTHONPATH" }
$env:HAKGAL_SQLITE_DB_PATH = $DbUri
if ($ReadWrite) {
    $env:HAKGAL_SQLITE_READONLY = 'false'
} else {
    $env:HAKGAL_SQLITE_READONLY = 'true'
}
$env:HAKGAL_PORT = "$Port"
if ($Mojo) { $env:MOJO_ENABLED = 'true' } else { $env:MOJO_ENABLED = 'false' }
if ($Validate) { $env:MOJO_VALIDATE_ENABLED = 'true' } else { $env:MOJO_VALIDATE_ENABLED = 'false' }
if ($Dupes) { $env:MOJO_DUPES_ENABLED = 'true' } else { $env:MOJO_DUPES_ENABLED = 'false' }

$code = @"
import os, sys
sys.path.insert(0, r'{0}')
os.environ.setdefault('PYTHONIOENCODING','utf-8')
os.environ.setdefault('PYTHONUTF8','1')
# Ensure UTF-8 streams (Windows consoles often default to cp1252)
try:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding='utf-8', errors='replace')  # type: ignore[attr-defined]
except Exception:
    pass
import hexagonal_api_enhanced as m
api = m.create_app(use_legacy=False, enable_all=True)
api.run(host='127.0.0.1', port={1}, debug=False)
"@ -f (Join-Path $root 'src_hexagonal'), $Port

$tmp = Join-Path $logDir ("launch_{0}.py" -f $Port)
Set-Content -LiteralPath $tmp -Value $code -Encoding UTF8
$p = Start-Process -FilePath $py -ArgumentList @("`"$tmp`"") -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru

$ok = Wait-Health -Url "http://127.0.0.1:$Port" -TimeoutSec $HealthTimeoutSec
if (-not $ok) {
    $eo = ''
    if (Test-Path $err) { $eo = (Get-Content $err -Tail 80 | Out-String) }
    $oo = ''
    if (Test-Path $out) { $oo = (Get-Content $out -Tail 80 | Out-String) }
    Write-Output (@{ started = $false; pid = $p.Id; err_tail = $eo; out_tail = $oo } | ConvertTo-Json -Depth 6)
    exit 1
}

if (-not $ReadWrite) {
    try { Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:$Port/api/safety/kill-switch/activate" -Body (@{}|ConvertTo-Json) -ContentType application/json | Out-Null } catch {}
} else {
    try { Invoke-RestMethod -Method POST -Uri "http://127.0.0.1:$Port/api/safety/kill-switch/deactivate" -Body (@{}|ConvertTo-Json) -ContentType application/json | Out-Null } catch {}
}

$status = @{ started = $true; pid = $p.Id; port = $Port; mojo = @{ enabled = [bool]$Mojo; validate = [bool]$Validate; dupes = [bool]$Dupes }; db_uri = $DbUri }
Write-Output ($status | ConvertTo-Json -Depth 6)


