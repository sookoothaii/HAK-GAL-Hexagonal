# HAK_GAL MCP Config Validator
# Prüft und korrigiert die Claude Config

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "HAK_GAL MCP Config Validator" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

$configPath = "$env:APPDATA\Claude\claude_desktop_config.json"

# Teste ob Config existiert
if (-not (Test-Path $configPath)) {
    Write-Host "`n❌ Config nicht gefunden: $configPath" -ForegroundColor Red
    Write-Host "Erstelle neue Config..." -ForegroundColor Yellow
    
    $newConfig = @{
        mcpServers = @{
            "hak-gal" = @{
                command = "python"
                args = @("D:\MCP Mods\HAK_GAL_HEXAGONAL\hak_gal_mcp_v2.py")
            }
        }
    }
    
    $newConfig | ConvertTo-Json -Depth 10 | Set-Content $configPath
    Write-Host "✅ Neue Config erstellt!" -ForegroundColor Green
    exit
}

# Lade und prüfe Config
try {
    $config = Get-Content $configPath | ConvertFrom-Json
    Write-Host "`n✅ Config geladen" -ForegroundColor Green
    
    # Prüfe mcpServers
    if ($config.mcpServers) {
        Write-Host "✅ mcpServers gefunden" -ForegroundColor Green
        
        # Prüfe hak-gal
        if ($config.mcpServers.'hak-gal') {
            $hakgal = $config.mcpServers.'hak-gal'
            Write-Host "✅ hak-gal Server gefunden" -ForegroundColor Green
            
            # KRITISCH: Prüfe command Format
            if ($hakgal.command -is [array]) {
                Write-Host "❌ FEHLER: 'command' ist ein Array, sollte String sein!" -ForegroundColor Red
                Write-Host "   Aktuell: $($hakgal.command | ConvertTo-Json -Compress)" -ForegroundColor Yellow
                
                # Korrigiere
                Write-Host "`nKorrigiere Config..." -ForegroundColor Cyan
                $hakgal.command = $hakgal.command[0]  # Nimm erstes Element
                
                # Speichere korrigierte Config
                $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
                Write-Host "✅ Config korrigiert und gespeichert!" -ForegroundColor Green
                
            } elseif ($hakgal.command -is [string]) {
                Write-Host "✅ 'command' ist korrekt ein String: $($hakgal.command)" -ForegroundColor Green
            } else {
                Write-Host "⚠️ 'command' hat unerwarteten Typ: $($hakgal.command.GetType())" -ForegroundColor Yellow
            }
            
            # Prüfe args
            if ($hakgal.args) {
                if ($hakgal.args -is [array]) {
                    Write-Host "✅ 'args' ist korrekt ein Array" -ForegroundColor Green
                    Write-Host "   Args: $($hakgal.args -join ', ')" -ForegroundColor Gray
                } else {
                    Write-Host "⚠️ 'args' sollte ein Array sein" -ForegroundColor Yellow
                }
            }
            
        } else {
            Write-Host "❌ hak-gal Server nicht in Config" -ForegroundColor Red
            
            # Füge hinzu
            Write-Host "Füge hak-gal Server hinzu..." -ForegroundColor Yellow
            $config.mcpServers | Add-Member -MemberType NoteProperty -Name "hak-gal" -Value @{
                command = "python"
                args = @("D:\MCP Mods\HAK_GAL_HEXAGONAL\hak_gal_mcp_v2.py")
            }
            
            $config | ConvertTo-Json -Depth 10 | Set-Content $configPath
            Write-Host "✅ hak-gal Server hinzugefügt!" -ForegroundColor Green
        }
        
    } else {
        Write-Host "❌ Keine mcpServers in Config" -ForegroundColor Red
    }
    
} catch {
    Write-Host "`n❌ Fehler beim Parsen der Config:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    # Zeige problematischen Content
    Write-Host "`nConfig Inhalt:" -ForegroundColor Yellow
    Get-Content $configPath | Select-Object -First 20
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "Validierung abgeschlossen" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host "`nHINWEIS:" -ForegroundColor Yellow
Write-Host "Nach Config-Änderungen MUSS Claude neu gestartet werden!" -ForegroundColor Yellow
Write-Host "1. Claude komplett beenden (auch System Tray)" -ForegroundColor White
Write-Host "2. Claude neu starten" -ForegroundColor White
Write-Host "3. Testen mit: 'What MCP tools do you have?'" -ForegroundColor White
