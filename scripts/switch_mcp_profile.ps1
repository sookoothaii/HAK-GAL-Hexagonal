param(
    [ValidateSet('readonly','write')]
    [string]$Profile = 'readonly'
)

$root = Split-Path -Parent $MyInvocation.MyCommand.Path
$proj = Split-Path -Parent $root
$cursorDir = Join-Path $proj '.cursor'
$target = Join-Path $cursorDir 'mcp.json'
$src = Join-Path $cursorDir "mcp.$Profile.json"

if (-not (Test-Path $src)) {
    Write-Error "Profil-Datei nicht gefunden: $src"
    exit 1
}

if ($Profile -eq 'write' -and $env:HAKGAL_WRITE_TOKEN) {
    # Ersetze Platzhalter durch Env-Token
    $json = Get-Content -Raw -Path $src
    $json = $json.Replace('${HAKGAL_WRITE_TOKEN}', $env:HAKGAL_WRITE_TOKEN)
    Set-Content -Path $target -Value $json -Encoding UTF8
} else {
    Copy-Item -Path $src -Destination $target -Force
}

Write-Host "MCP-Profil umgeschaltet auf: $Profile"
Write-Host "Ziel: $target"


