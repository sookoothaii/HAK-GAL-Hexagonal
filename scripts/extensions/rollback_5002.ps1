Param(
    [int]$Port = 5002
)
$ErrorActionPreference = 'Stop'

$here = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location "$here\..\.."
$root = Get-Location

function Stop-PortProcess {
    param([int]$Port)
    try {
        $p = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction Stop | Select-Object -First 1 -ExpandProperty OwningProcess
        if ($p) { Stop-Process -Id $p -Force -ErrorAction SilentlyContinue; Start-Sleep -Seconds 2 }
    } catch {}
}

# Stop running 5002
Stop-PortProcess -Port $Port

# Start baseline (SQLite SoT, Mojo disabled) read-only for safety
$py = Join-Path $root '.venv_hexa/ScriptS/python.exe'
if (-not (Test-Path $py)) { $py = Join-Path $root '.venv_hexa/Scripts/python.exe' }
if (-not (Test-Path $py)) { throw "Python venv nicht gefunden: $py" }

$env:MOJO_ENABLED='false'
$env:MOJO_VALIDATE_ENABLED='false'
$env:MOJO_DUPES_ENABLED='false'
$env:HAKGAL_SQLITE_READONLY='true'
$env:HAKGAL_SQLITE_DB_PATH='file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared'

$out = Join-Path $root 'logs/server5002.rollback.out.txt'
$err = Join-Path $root 'logs/server5002.rollback.err.txt'
$code = @"
import os, sys
sys.path.insert(0, r'{0}')
os.environ.setdefault('PYTHONIOENCODING','utf-8')
os.environ.setdefault('PYTHONUTF8','1')
import hexagonal_api_enhanced as m
api = m.create_app(use_legacy=False, enable_all=True)
api.run(host='127.0.0.1', port={1}, debug=False)
"@ -f (Join-Path $root 'src_hexagonal'), $Port

$p = Start-Process -FilePath $py -ArgumentList @('-c', $code) -WindowStyle Hidden -RedirectStandardOutput $out -RedirectStandardError $err -PassThru
Start-Sleep -Seconds 3

Write-Output ((@{ ok = $true; pid = $p.Id; port = $Port; mode = 'rollback_baseline_ro' }) | ConvertTo-Json -Depth 6)


