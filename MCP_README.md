# HAK_GAL MCP Integration - Minimale, sichere Implementierung

## Was wurde implementiert?

Eine **minimal-invasive MCP-Integration**, die:
- ✅ Die bestehende Architektur NICHT verändert
- ✅ Als separater Adapter in `infrastructure/mcp/` läuft
- ✅ Nur READ-ONLY Operationen (keine Gefährdung)
- ✅ Über HTTP mit der bestehenden API kommuniziert

## Architektur

```
Claude Desktop / Cursor
       ↓ (MCP Protocol via STDIO)
MCP Server (mcp_server.py)
       ↓ (HTTP Calls)
HAK_GAL API (Port 5001) ← Bleibt unverändert!
       ↓
Knowledge Base, HRM, LLM Ensemble
```

## Verfügbare MCP Tools

1. **search_knowledge** - Durchsucht die Wissensbasis
2. **get_system_status** - Zeigt System-Status und Metriken
3. **neural_reasoning** - Nutzt HRM Neural Reasoning
4. **list_recent_facts** - Listet aktuelle Fakten

## Installation & Start

### 1. HAK_GAL normal starten (Port 5001)
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
python src_hexagonal\hexagonal_api_enhanced_clean.py
```

### 2. MCP-Integration testen
```bash
python test_mcp_integration.py
```

### 3. Claude Desktop konfigurieren

Windows: Kopiere den Inhalt von `claude_desktop_config.json` nach:
```
%APPDATA%\Claude\claude_desktop_config.json
```

Linux/Mac: 
```
~/.config/Claude/claude_desktop_config.json
```

### 4. Claude Desktop neu starten

Die HAK_GAL Tools sind jetzt in Claude verfügbar!

## Sicherheitsgarantien

- **Keine Core-Änderungen**: MCP läuft komplett isoliert
- **Read-Only**: Keine schreibenden Operationen
- **HTTP-Client nur**: Verhält sich wie ein externer API-Client
- **Kein Hot-Swapping**: Keine dynamischen Code-Änderungen
- **Keine Autonomie**: Alles manuell gesteuert

## Troubleshooting

### "Connection error" beim Test
- Stelle sicher, dass HAK_GAL auf Port 5001 läuft
- Prüfe: http://127.0.0.1:5001/health

### Claude findet die Tools nicht
- Claude Desktop neu starten
- Prüfe den Pfad in claude_desktop_config.json
- Logs prüfen: `%APPDATA%\Claude\logs\`

### MCP Server startet nicht
- Python-Umgebung aktiviert? (.venv_hexa)
- httpx installiert? `pip install httpx`

## Nächste Schritte (Optional)

Nach erfolgreicher Test-Phase können Sie:
1. Weitere Read-Only Tools hinzufügen
2. Andere MCP-Server einbinden (Filesystem, Git, etc.)
3. Mit Cursor/anderen AI-Tools verbinden

## Wichtig

Diese Implementation ist **bewusst minimal** gehalten:
- Kein Multi-AI Orchestration
- Keine selbst-modifizierenden Systeme  
- Keine Runtime-Modifikationen
- Nur das, was sicher und sinnvoll ist

## Support

Bei Fragen zur Integration:
1. Logs prüfen (MCP Server gibt Feedback)
2. test_mcp_integration.py nutzen
3. HAK_GAL API direkt testen (Port 5001)
