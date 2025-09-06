# Quick Database Check
# ====================

Write-Host "DATABASE CHECK" -ForegroundColor Yellow
Write-Host "==============" -ForegroundColor Cyan

# Check hexagonal_kb.db
$db_path = "D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"

if (Test-Path $db_path) {
    $fileInfo = Get-Item $db_path
    Write-Host "✅ hexagonal_kb.db found" -ForegroundColor Green
    Write-Host "   Size: $([math]::Round($fileInfo.Length / 1MB, 2)) MB" -ForegroundColor Gray
    Write-Host "   Path: $db_path" -ForegroundColor Gray
    
    # Try to get fact count using Python
    $python_check = @"
import sqlite3
conn = sqlite3.connect(r'$db_path')
cursor = conn.cursor()
cursor.execute('SELECT COUNT(*) FROM facts')
count = cursor.fetchone()[0]
conn.close()
print(f'Facts: {count}')
"@
    
    $python_check | python
    
} else {
    Write-Host "❌ hexagonal_kb.db NOT FOUND!" -ForegroundColor Red
    Write-Host "   Expected at: $db_path" -ForegroundColor Red
}

Write-Host ""
Write-Host "To start with correct database:" -ForegroundColor Yellow
Write-Host "  .\START_ALL_SERVICES_FIXED.ps1" -ForegroundColor White
Write-Host "  or" -ForegroundColor Gray
Write-Host "  START_FIXED.bat" -ForegroundColor White
