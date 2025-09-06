param(
    [string]$BaseUrl = 'http://127.0.0.1:8088',
    [string]$ApiKey = 'hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d'
)

$ErrorActionPreference = 'Stop'
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$fact = "TestFact(GPT5_ProxyWrite,$ts)"

$headers = @{ 'Content-Type' = 'application/json'; 'X-API-Key' = $ApiKey }

$postObj = [ordered]@{
  statement = $fact
  context   = [ordered]@{ source = 'apitest'; via = 'proxy'; ts = $ts }
}
$postJson = $postObj | ConvertTo-Json -Compress
$postResp = Invoke-RestMethod -Method POST -Uri ("$BaseUrl/api/facts") -Headers $headers -Body $postJson

Start-Sleep -Milliseconds 100

$searchObj = [ordered]@{ query = $fact; limit = 10 }
$searchJson = $searchObj | ConvertTo-Json -Compress
$verifyResp = Invoke-RestMethod -Method POST -Uri ("$BaseUrl/api/search") -Headers $headers -Body $searchJson

[pscustomobject]@{
  fact   = $fact
  post   = $postResp
  verify = $verifyResp
} | ConvertTo-Json -Compress



