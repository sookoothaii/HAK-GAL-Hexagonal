# 🔑 API-Key Setup & Multi-Agent Test

## ✅ API-Key wurde konfiguriert!

Der HAK/GAL API-Key wurde in beiden .env Dateien gespeichert:
- `D:\MCP Mods\HAK_GAL_SUITE\.env`
- `D:\MCP Mods\HAK_GAL_HEXAGONAL\.env`

**API-Key:** `hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d`

## 🚀 Server neu starten (WICHTIG!)

Der Server muss neu gestartet werden, um die .env Datei zu laden:

```bash
# Terminal 1: Server stoppen (Ctrl+C) und neu starten
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.venv_hexa\Scripts\activate
python src_hexagonal/hexagonal_api_enhanced_clean.py
```

Warte auf:
```
[ENV] Loaded environment from D:\MCP Mods\HAK_GAL_HEXAGONAL\.env
```

## 🧪 Multi-Agent Tests

### Option 1: Vollständiger Test (alle Agenten)
```bash
# Terminal 2: Alle Agenten testen
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.venv_hexa\Scripts\activate
python scripts\test_multi_agent.py
```

### Option 2: Schneller Gemini-Test
```bash
# Terminal 2: Nur Gemini testen
cd D:\MCP Mods\HAK_GAL_HEXAGONAL
.venv_hexa\Scripts\activate
python scripts\test_gemini_quick.py
```

## 📋 Erwartete Ergebnisse

### ✅ Gemini (sollte funktionieren)
```
🤖 Testing delegation to: gemini
✅ Request successful!
📝 Result: 
Hexagon umschließt,
HAK und GAL im Einklang -
Wissen strukturiert.
```

### ⚠️ Andere Agenten
- **Claude CLI**: Benötigt installierte Claude CLI
- **Claude Desktop**: Experimentell, benötigt laufendes Claude Desktop
- **Cursor**: Benötigt Cursor IDE mit Extension

## 🔍 Fehlersuche

Falls immer noch "403 Forbidden":
1. Stelle sicher, dass der Server NEU GESTARTET wurde
2. Prüfe in der Server-Ausgabe: `[ENV] Loaded environment...`
3. Prüfe, ob der richtige API-Key geladen wurde

Falls Gemini nicht funktioniert:
- Prüfe Internet-Verbindung
- Prüfe, ob GOOGLE_API_KEY in .env korrekt ist

## 🎯 Direkt-Test mit MCP Tool

Du kannst auch direkt das MCP Tool verwenden:

```python
delegate_task(
    target_agent='gemini',
    task_description='Erstelle ein Haiku über HAK/GAL',
    context={'style': 'poetisch'}
)
```

Viel Erfolg! 🚀
