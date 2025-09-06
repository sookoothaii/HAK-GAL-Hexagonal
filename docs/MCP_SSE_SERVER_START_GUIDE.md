# HAK_GAL MCP Server mit SuperAssistant SSE - Komplettanleitung

**Dokument-ID:** MCP-SSE-START-GUIDE-20250904  
**Status:** Produktiv getestet und verifiziert  
**Tools:** 66 (vollstaendig)

## SCHNELLSTART (Copy & Paste)

```bash
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\activate
npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse
```

Server laeuft dann auf: `http://localhost:3006/sse`

---

## DETAILLIERTE ANLEITUNG

### SCHRITT 1: Virtual Environment aktivieren

```bash
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.venv_hexa\Scripts\activate
```

**Verifizierung:** Prompt sollte `(.venv_hexa)` zeigen

### SCHRITT 2: MCP Server mit SSE starten

#### Option A: Mit Config-Datei (EMPFOHLEN)
```bash
npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse
```

#### Option B: Mit expliziten Parametern
```bash
npx @srbhptl39/mcp-superassistant-proxy@latest --stdio ".venv_hexa\Scripts\python.exe ultimate_mcp\hakgal_mcp_ultimate.py" --outputTransport sse --port 3006
```

#### Option C: Mit zusaetzlichen Optionen
```bash
npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse --port 3006 --ssePath /sse --messagePath /message
```

### SCHRITT 3: Erfolgreiche Start-Meldung

Nach erfolgreichem Start sollten Sie sehen:
```
[mcp-superassistant-proxy] Starting...
[mcp-superassistant-proxy] Starting mcp-superassistant-proxy ...
[mcp-superassistant-proxy]   - outputTransport: sse
[mcp-superassistant-proxy]   - port: 3006
[mcp-superassistant-proxy]   - CORS: enabled ("*")
[mcp-superassistant-proxy] Listening on localhost:3006
[mcp-superassistant-proxy] SSE endpoint: http://localhost:3006/sse
[mcp-superassistant-proxy] POST messages: http://localhost:3006/message
```

---

## KONFIGURATIONSDATEIEN

### Hauptkonfiguration: `mcp-superassistant.sse.config.json`

```json
{
  "mcpServers": {
    "hak-gal": {
      "type": "stdio",
      "command": ".\\.venv_hexa\\Scripts\\python.exe",
      "args": [
        "-u",
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\ultimate_mcp\\hakgal_mcp_ultimate.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL",
        "HAKGAL_API_BASE_URL": "http://127.0.0.1:5002",
        "HAKGAL_WRITE_ENABLED": "true",
        "HAKGAL_WRITE_TOKEN": "",
        "HAKGAL_HUB_PATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB",
        "HAKGAL_AUTO_SNAPSHOT_ON_SHUTDOWN": "false",
        "HAKGAL_AUTO_DIGEST_ON_INIT": "false"
      }
    }
  }
}
```

### Alternative Configs:
- **stdio:** `mcp-superassistant.stdio.config.json`
- **standard:** `mcp-superassistant.config.json`

---

## TRANSPORT-OPTIONEN

| Transport | Port | Endpoint | Verwendung |
|-----------|------|----------|------------|
| **sse** | 3006 | /sse | Server-Sent Events (empfohlen) |
| **streamableHttp** | 3006 | /stream | HTTP Streaming |
| **ws** | 3006 | /ws | WebSocket (Browser-Einschraenkungen) |

---

## TROUBLESHOOTING

### Problem: "can't open file"
**Loesung:** Pfad pruefen - muss `ultimate_mcp\hakgal_mcp_ultimate.py` sein

### Problem: "port already in use"
**Loesung:** 
```bash
# Windows: Port-Prozess finden und beenden
netstat -ano | findstr :3006
taskkill /PID <PID-Nummer> /F
```

### Problem: "module not found"
**Loesung:** Virtual Environment aktivieren!
```bash
.venv_hexa\Scripts\activate
pip install -r requirements.txt
```

### Problem: Nur 43 Tools statt 66
**Loesung:** Falscher MCP Server - muss `ultimate_mcp\hakgal_mcp_ultimate.py` sein

---

## VERIFIKATION

### 1. Im Browser oeffnen
```
http://localhost:3006/sse
```
Sollte SSE-Stream zeigen

### 2. In Claude/DeepSeek
- Server Configuration → Server Connected ✓
- Available Tools → 66 tools

### 3. Test-Commands
```bash
# Health Check
curl http://localhost:3006/message -X POST -H "Content-Type: application/json" -d "{\"method\":\"health_check\"}"

# Facts Count
curl http://localhost:3006/message -X POST -H "Content-Type: application/json" -d "{\"method\":\"get_facts_count\"}"
```

---

## AUTOMATISIERUNG

### Windows Batch Script: `start_mcp_sse.bat`
```batch
@echo off
echo ========================================
echo HAK-GAL MCP SSE Server Starter
echo 66 Tools Version
echo ========================================
cd /d "D:\MCP Mods\HAK_GAL_HEXAGONAL"
call .venv_hexa\Scripts\activate
npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse
pause
```

### PowerShell Script: `start_mcp_sse.ps1`
```powershell
Write-Host "Starting HAK-GAL MCP SSE Server (66 Tools)" -ForegroundColor Green
Set-Location "D:\MCP Mods\HAK_GAL_HEXAGONAL"
& ".\.venv_hexa\Scripts\Activate.ps1"
npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse
```

---

## ENVIRONMENT VARIABLEN

| Variable | Wert | Zweck |
|----------|------|-------|
| PYTHONIOENCODING | utf-8 | Encoding fuer Python I/O |
| PYTHONPATH | D:\MCP Mods\HAK_GAL_HEXAGONAL | Python Module Path |
| HAKGAL_API_BASE_URL | http://127.0.0.1:5002 | HAK-GAL API Endpoint |
| HAKGAL_WRITE_ENABLED | true | Schreibzugriff aktiviert |
| HAKGAL_HUB_PATH | ...\PROJECT_HUB | Projekt Hub Pfad |

---

## TOOL-UEBERSICHT (66 GESAMT)

### Knowledge Base (32 Tools)
- Core: 14 (get_facts_count, search_knowledge, add_fact...)
- Analysis: 13 (semantic_similarity, consistency_check...)
- Advanced: 5 (inference_chain, project_snapshot...)

### File & Database (20 Tools)
- File Operations: 13 (read_file, write_file, grep...)
- Database: 7 (db_backup_now, db_vacuum...)

### AI & System (14 Tools)
- Nischen: 7 (niche_list, niche_stats...)
- Meta/AI: 4 (consensus_evaluator, delegation_optimizer...)
- System: 3 (delegate_task, execute_code, health_check)

---

## WICHTIGE PFADE

```
D:\MCP Mods\HAK_GAL_HEXAGONAL\
├── ultimate_mcp\
│   └── hakgal_mcp_ultimate.py     # Der korrekte MCP Server (66 Tools)
├── .venv_hexa\                     # Virtual Environment
├── hexagonal_kb.db                 # Knowledge Base (6,511+ Fakten)
├── mcp-superassistant.sse.config.json  # SSE Konfiguration
└── PROJECT_HUB\                    # Projekt-Dokumentation
```

---

## BACKUP DER ARBEITS-KONFIGURATION

Die funktionierende Konfiguration ist gesichert in:
- `mcp-superassistant.sse.config.json` - Hauptconfig fuer SSE
- `mcp-superassistant.stdio.config.json` - Alternative stdio
- `mcp-superassistant.config.json` - Standard-Config

---

**Letzte erfolgreiche Verbindung:** 2025-09-04  
**Verifizierte Tools:** 66  
**Status:** ✅ Produktiv

---

## QUICK COMMANDS

```bash
# Start
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL" && .venv_hexa\Scripts\activate && npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse

# Stop
Ctrl+C

# Restart
Ctrl+C && npx @srbhptl39/mcp-superassistant-proxy@latest --config mcp-superassistant.sse.config.json --outputTransport sse
```
