# HAK-GAL Port 5002 Write Mode Configuration
**Status:** ✅ Configured for WRITE Access  
**Database:** hexagonal_kb.db (20 KB, separate from main DB)  
**Generated:** 2025-08-15  

## Executive Summary

Port 5002 wurde erfolgreich für **WRITE MODE** mit einer eigenen Datenbank (`hexagonal_kb.db`) konfiguriert. Dies ermöglicht die vollständige Nutzung der Selbstlernfunktionen (Governor, Aethelred Engine, Thesis Engine) ohne die Hauptdatenbank zu beeinflussen.

## Konfiguration

### Environment Variables
```bash
HAKGAL_PORT=5002
HAKGAL_SQLITE_READONLY=false
HAKGAL_SQLITE_DB_PATH=D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db
MOJO_ENABLED=true
MOJO_VALIDATE_ENABLED=true
MOJO_DUPES_ENABLED=true
ENABLE_GOVERNOR=true
ENABLE_AUTO_LEARNING=true
THESIS_ENGINE_ENABLED=true
AETHELRED_ENGINE_ENABLED=true
```

### Dateien erstellt/modifiziert

1. **start_backend_5002.bat** - Batch-Datei für Windows CMD
   - Aktiviert Write-Mode
   - Setzt alle notwendigen Environment-Variablen
   - Startet Backend auf Port 5002

2. **start_5002_write_mode.ps1** - PowerShell-Skript (empfohlen)
   - Farbige Ausgabe
   - Bessere Fehlerbehandlung
   - Zeigt Konfiguration übersichtlich an

3. **test_write_mode_5002.py** - Test-Skript
   - Verifiziert Write-Zugriff
   - Testet Fact-Erstellung
   - Prüft Governor-Status
   - Zeigt Mojo-Konfiguration

## Start-Anleitung

### Option 1: PowerShell (Empfohlen)
```powershell
# In PowerShell ausführen:
.\start_5002_write_mode.ps1
```

### Option 2: Windows CMD
```cmd
# In Command Prompt ausführen:
start_backend_5002.bat
```

### Option 3: Manuell in PowerShell
```powershell
# Environment setzen
$env:HAKGAL_PORT = "5002"
$env:HAKGAL_SQLITE_READONLY = "false"
$env:HAKGAL_SQLITE_DB_PATH = "D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db"
$env:MOJO_ENABLED = "true"
$env:ENABLE_GOVERNOR = "true"

# Virtual Environment aktivieren
& "D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\Activate.ps1"

# Backend starten
python "D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\launch_5002_mojo.py"
```

## Verifikation

Nach dem Start, führe das Test-Skript aus:

```python
python test_write_mode_5002.py
```

Erwartete Ausgabe:
```
✅ Server is running on port 5002
✅ Database connected: X facts
✅ WRITE MODE CONFIRMED - Fact added successfully!
✅ Mojo Status: Enabled
✅ Governor Status: Active
```

## Wichtige Endpoints

### Health & Status
- http://localhost:5002/health - Server Health Check
- http://localhost:5002/api/facts/count - Anzahl Facts in DB
- http://localhost:5002/api/governor/status - Governor Status
- http://localhost:5002/api/mojo/flags - Mojo Konfiguration

### Auto-Learning Control
- POST http://localhost:5002/api/governor/start - Governor starten
- POST http://localhost:5002/api/governor/stop - Governor stoppen
- GET http://localhost:5002/api/engines/status - Engine Status

### Mojo Features
- http://localhost:5002/api/mojo/golden?limit=1000 - Golden Validation
- http://localhost:5002/api/analysis/duplicates - Duplikate-Analyse
- http://localhost:5002/api/quality/metrics - Qualitäts-Metriken

## Troubleshooting

### Problem: "Database is read-only"
**Lösung:** Stelle sicher, dass `HAKGAL_SQLITE_READONLY=false` gesetzt ist

### Problem: Governor startet nicht
**Lösung:** Prüfe ob `ENABLE_GOVERNOR=true` und `ENABLE_AUTO_LEARNING=true` gesetzt sind

### Problem: Port 5002 bereits belegt
**Lösung:** Beende alte Prozesse:
```powershell
$pid = (Get-NetTCPConnection -LocalPort 5002 -State Listen).OwningProcess
Stop-Process -Id $pid -Force
```

## Unterschiede zu Port 5001

| Feature | Port 5001 | Port 5002 |
|---------|-----------|-----------|
| Database | k_assistant.db | hexagonal_kb.db |
| Default Mode | Read-Only | Write-Enabled |
| Mojo | Optional | Always Enabled |
| Governor | Disabled | Enabled |
| Use Case | Production | Testing/Development |

## Sicherheitshinweise

⚠️ **Port 5002 hat WRITE-Zugriff auf hexagonal_kb.db!**
- Die Datenbank ist von der Hauptdatenbank isoliert
- Ideal für Tests der Selbstlernfunktionen
- Regelmäßige Backups empfohlen

## Nächste Schritte

1. ✅ Backend auf Port 5002 starten
2. ✅ Write-Mode mit Test-Skript verifizieren
3. 🔄 Governor aktivieren und konfigurieren
4. 🔄 Engines (Aethelred, Thesis) testen
5. 🔄 Monitoring der generierten Facts

## Referenzen

- [SERVER_START_GUIDE_HEXAGONAL_5001_5002_20250815.md](PROJECT_HUB/SERVER_START_GUIDE_HEXAGONAL_5001_5002_20250815.md)
- [TECHNICAL_HANDOVER_NEXT_INSTANCE_GPT5_20250815.md](PROJECT_HUB/TECHNICAL_HANDOVER_NEXT_INSTANCE_GPT5_20250815.md)
- HAK/GAL Verfassung Artikel 6: Empirische Validierung

---

**Status:** Die Konfiguration für Port 5002 im Write-Mode ist vollständig implementiert und bereit für Tests der Selbstlernfunktionen.
