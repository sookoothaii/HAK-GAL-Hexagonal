$env:OPENAI_API_KEY = "YOUR_OPENAI_API_KEY_HERE"
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "YOUR_OPENAI_API_KEY_HERE", "User")
Write-Host "OPENAI_API_KEY wurde gesetzt!" -ForegroundColor Green
