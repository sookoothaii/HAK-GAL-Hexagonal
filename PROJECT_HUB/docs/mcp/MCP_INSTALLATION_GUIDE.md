---
title: "Mcp Installation Guide"
created: "2025-09-15T00:08:01.036619Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK_GAL MCP Integration - Installation Guide

## ✅ Status: MCP Server ist bereit!

Die Tests zeigen, dass Ihr System funktioniert:
- 391 Facts in der Datenbank
- API läuft auf Port 5001
- MCP Server ist implementiert und getestet

## 📋 Installation in 3 Schritten

### Schritt 1: HAK_GAL API starten (falls nicht läuft)
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.\.venv_hexa\Scripts\activate
python src_hexagonal\hexagonal_api_enhanced_clean.py
```
Lassen Sie dieses Terminal offen!

### Schritt 2: Claude Desktop konfigurieren
```bash
# In neuem Terminal:
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.\install_claude_config.bat
```

### Schritt 3: Claude Desktop neu starten
1. Claude Desktop komplett schließen (auch im System Tray!)
2. Claude Desktop neu starten
3. Fertig! 

## 🧪 Testen in Claude Desktop

Fragen Sie Claude nach der Installation:

- "What tools do you have available?"
- "Use the search_knowledge tool to find facts about neural networks"
- "Get the HAK_GAL system status"
- "List 5 recent facts from the knowledge base"
- "Use neural_reasoning to analyze 'What is hexagonal architecture?'"

## 🔧 Troubleshooting

### Claude findet die Tools nicht?
1. Prüfen Sie: `%APPDATA%\Claude\claude_desktop_config.json` existiert
2. Pfad muss GENAU stimmen: `D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal\\infrastructure\\mcp\\mcp_server.py`
3. Claude Desktop KOMPLETT neu starten (nicht nur Fenster schließen)

### "Connection refused" Fehler?
- HAK_GAL API läuft nicht → Starten Sie sie mit dem Befehl oben

### MCP Server startet nicht?
```bash
# Direkter Test:
python test_mcp_server_direct.py
```

### Logs prüfen:
- Windows: `%APPDATA%\Claude\logs\`
- Suchen Sie nach "mcp" oder "hak-gal" in den Logs

## 🎯 Was funktioniert jetzt?

Mit dieser Integration kann Claude:

1. **Knowledge Base durchsuchen** - 391 Facts verfügbar
2. **System-Status abfragen** - Architektur, Facts-Count, etc.
3. **Neural Reasoning nutzen** - HRM-Engine Zugriff
4. **Facts auflisten** - Aktuelle Facts aus der KB

## 🚀 Nächste Schritte (Optional)

Nach erfolgreicher Installation können Sie:

1. **Weitere Tools hinzufügen** (in `mcp_server.py`)
   - `add_fact` - Neue Facts hinzufügen (mit Validierung)
   - `explain_topic` - LLM-Erklärungen generieren
   - `analyze_code` - Code-Analyse mit HAK_GAL

2. **Andere MCP Server einbinden**
   - Filesystem MCP Server
   - GitHub MCP Server
   - Slack MCP Server

3. **Mit Cursor verbinden**
   - HTTP-Transport auf Port 5002 hinzufügen
   - Cursor MCP-Konfiguration erstellen

## 📊 Architektur-Übersicht

```
Claude Desktop
    ↓ STDIO (JSON-RPC)
MCP Server (mcp_server.py)
    ↓ HTTP
HAK_GAL API (Port 5001)
    ↓
├── Knowledge Base (391 Facts)
├── HRM Neural Reasoning
├── LLM Ensemble
└── Governor System
```

## ✅ Erfolgs-Checkliste

- [ ] HAK_GAL API läuft auf Port 5001
- [ ] `test_mcp_integration.py` zeigt Facts
- [ ] `install_claude_config.bat` erfolgreich ausgeführt
- [ ] Claude Desktop neu gestartet
- [ ] Claude findet HAK_GAL tools

## 🔒 Sicherheit

Diese Implementation ist bewusst sicher:
- **Read-Only**: Keine gefährlichen Schreiboperationen
- **Isoliert**: MCP läuft als separater Prozess
- **Minimal**: Nur 4 sichere Tools
- **Transparent**: Alle Aktionen werden geloggt

## 📝 Notizen

- MCP Server macht nur HTTP-Calls zur API
- Keine Änderung der Core-Architektur
- Hexagonal Architecture bleibt intakt
- Kann jederzeit entfernt werden (nur `mcp/` Ordner löschen)

---

**Viel Erfolg mit Ihrer HAK_GAL MCP Integration!**

Bei Fragen: Die Implementation ist in `src_hexagonal/infrastructure/mcp/mcp_server.py`
