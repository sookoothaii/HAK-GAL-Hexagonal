param(
    [string]$Url = 'http://127.0.0.1:8088/health',
    [int]$N = 50,
    [int]$DelayMs = 30,
    [int]$TimeoutSec = 10
)

$ErrorActionPreference = 'Stop'
$times = New-Object System.Collections.Generic.List[double]

for ($i = 0; $i -lt $N; $i++) {
    $sw = [System.Diagnostics.Stopwatch]::StartNew()
    try {
        Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec $TimeoutSec | Out-Null
    } catch {
        # ignore errors, still record time
    }
    $sw.Stop()
    [void]$times.Add($sw.Elapsed.TotalMilliseconds)
    Start-Sleep -Milliseconds $DelayMs
}

$sorted = $times | Sort-Object
if ($sorted.Count -eq 0) {
    [pscustomobject]@{ count = 0; p95_ms = 0; avg_ms = 0 } | ConvertTo-Json -Compress
    exit 0
}
$idx = [int]([math]::Ceiling($sorted.Count * 0.95) - 1)
if ($idx -lt 0) { $idx = 0 }
$p95 = [math]::Round($sorted[$idx], 1)
$avg = [math]::Round((($times | Measure-Object -Average).Average), 2)

[pscustomobject]@{ count = $sorted.Count; p95_ms = $p95; avg_ms = $avg } | ConvertTo-Json -Compress


