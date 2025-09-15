---
title: "Restart After Fix"
created: "2025-09-15T00:08:00.978851Z"
author: "system-cleanup"
topics: ["analysis"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# HAK/GAL Server Neustart nach WebSocket Fix

## 🛑 Server stoppen
Drücke `Ctrl+C` im Terminal, wo der Server läuft.

## 🚀 Server neu starten
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.venv_hexa\Scripts\activate
python src_hexagonal/hexagonal_api_enhanced_clean.py
```

## ✅ Erwartete Ausgabe (OHNE Fehler)
```
[OK] Eventlet monkey-patching applied.
[ENV] Loaded environment from D:\MCP Mods\HAK_GAL_SUITE\.env
[INFO] Using SQLite Adapters (Development DB)
[SQLite] Using database: D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db
[SQLite] Facts count: 5833
...
🎯 HAK-GAL HEXAGONAL ARCHITECTURE - CLEAN VERSION
============================================================
[START] Starting on http://127.0.0.1:5002
```

## 🧪 Test durchführen
In einem neuen Terminal:
```bash
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.venv_hexa\Scripts\activate
python scripts/test_websocket_fix.py
```

## 📋 Was wurde behoben?
- **NameError**: `logger` → `print` 
- **TypeError**: Handler akzeptieren jetzt die richtigen Parameter
- WebSocket-Verbindungen funktionieren wieder korrekt
- Agent-Bus ist bereit für Multi-Agent-Kollaboration

## 🎉 Erfolg!
Der Server sollte jetzt ohne WebSocket-Fehler laufen.
