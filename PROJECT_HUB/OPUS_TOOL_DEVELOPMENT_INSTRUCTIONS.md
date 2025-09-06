# 👑 QUEEN'S ANWEISUNGEN FÜR OPUS - NEUE TOOL-ENTWICKLUNG

## 🎯 MISSION: 3 NEUE MCP TOOLS FÜR HAK_GAL SUITE

### 📋 VORAUSSETZUNGEN
- **Basis**: 44 existierende Tools in `hak_gal_mcp_sqlite_full.py`
- **Datenbank**: SQLite mit 5,951 Fakten
- **Architektur**: MCP Server mit JSON-RPC
- **Ziel**: 3 neue Tools implementieren

## 🛠️ TOOL 1: `smart_search` - INTELLIGENTE SUCHE

### Funktion
Semantische Suche mit LLM-Integration für bessere Suchergebnisse

### Implementierung
```python
{
    "name": "smart_search",
    "description": "Intelligente semantische Suche mit LLM-Integration",
    "inputSchema": {
        "type": "object",
        "properties": {
            "query": {"type": "string", "description": "Suchbegriff"},
            "search_type": {"type": "string", "enum": ["semantic", "exact", "fuzzy"], "default": "semantic"},
            "limit": {"type": "integer", "description": "Max Ergebnisse", "default": 10},
            "use_llm": {"type": "boolean", "description": "LLM für semantische Analyse nutzen", "default": true}
        },
        "required": ["query"]
    }
}
```

### Logik
1. **Exact Search**: Direkte SQLite-Suche
2. **Fuzzy Search**: Ähnlichkeitssuche mit Levenshtein-Distance
3. **Semantic Search**: LLM-basierte Bedeutungssuche
4. **Ranking**: Kombinierte Relevanz-Bewertung

## 🛠️ TOOL 2: `auto_categorize` - AUTOMATISCHE KATEGORISIERUNG

### Funktion
Automatische Kategorisierung von Fakten basierend auf Prädikaten und Inhalten

### Implementierung
```python
{
    "name": "auto_categorize",
    "description": "Automatische Kategorisierung von Fakten",
    "inputSchema": {
        "type": "object",
        "properties": {
            "fact": {"type": "string", "description": "Fakt zum Kategorisieren"},
            "category_system": {"type": "string", "enum": ["predicate_based", "content_based", "hybrid"], "default": "hybrid"},
            "confidence_threshold": {"type": "number", "description": "Mindest-Konfidenz", "default": 0.7}
        },
        "required": ["fact"]
    }
}
```

### Logik
1. **Predicate-based**: Kategorisierung nach Prädikat-Typ
2. **Content-based**: LLM-Analyse des Inhalts
3. **Hybrid**: Kombination beider Ansätze
4. **Confidence**: Rückgabe der Kategorisierungs-Sicherheit

## 🛠️ TOOL 3: `workflow_automation` - WORKFLOW-AUTOMATISIERUNG

### Funktion
Automatisierte Workflows für wiederkehrende Aufgaben

### Implementierung
```python
{
    "name": "workflow_automation",
    "description": "Automatisierte Workflows für wiederkehrende Aufgaben",
    "inputSchema": {
        "type": "object",
        "properties": {
            "workflow_name": {"type": "string", "description": "Name des Workflows"},
            "steps": {"type": "array", "items": {"type": "object"}, "description": "Workflow-Schritte"},
            "trigger": {"type": "string", "enum": ["manual", "scheduled", "event"], "default": "manual"},
            "schedule": {"type": "string", "description": "Cron-Expression für geplante Ausführung"}
        },
        "required": ["workflow_name", "steps"]
    }
}
```

### Logik
1. **Step Definition**: Definierte Workflow-Schritte
2. **Execution Engine**: Sequenzielle oder parallele Ausführung
3. **Error Handling**: Fehlerbehandlung und Rollback
4. **Monitoring**: Status-Tracking und Logging

## 📝 IMPLEMENTIERUNGSANWEISUNGEN

### 1. DATEI-STRUKTUR
- **Hauptdatei**: `hak_gal_mcp_sqlite_full.py`
- **Tool-Definitionen**: In `handle_list_tools()` hinzufügen
- **Tool-Logik**: In `handle_tool_call()` implementieren

### 2. CODING-STANDARDS
- **Python 3.8+** kompatibel
- **SQLite** für Datenbank-Operationen
- **JSON-RPC** für MCP-Kommunikation
- **Error Handling** für alle Operationen
- **Logging** für Debugging

### 3. TESTING
- **Unit Tests** für jede Tool-Funktion
- **Integration Tests** mit MCP-Server
- **Performance Tests** für große Datenmengen
- **Error Tests** für Edge Cases

### 4. DOKUMENTATION
- **Tool-Beschreibungen** in Deutsch
- **Parameter-Dokumentation** vollständig
- **Beispiele** für jede Tool-Nutzung
- **Changelog** für Änderungen

## 🎯 ERFOLGSKRITERIEN

### Funktionale Kriterien
- ✅ Alle 3 Tools funktional
- ✅ Integration in bestehenden MCP-Server
- ✅ Kompatibilität mit 44 existierenden Tools
- ✅ Fehlerfreie Ausführung

### Performance-Kriterien
- ✅ <100ms Response-Zeit für einfache Queries
- ✅ <500ms für komplexe LLM-Operationen
- ✅ Skalierbarkeit für 10,000+ Fakten
- ✅ Memory-Effizienz

### Qualitäts-Kriterien
- ✅ 100% Test-Coverage
- ✅ Vollständige Dokumentation
- ✅ HAK_GAL Verfassung konform
- ✅ Code-Review bereit

## 🚀 NÄCHSTE SCHRITTE

1. **Code-Review** der bestehenden 44 Tools
2. **Architektur-Planung** für neue Tools
3. **Implementierung** der 3 neuen Tools
4. **Testing** und Validierung
5. **Integration** in HAK_GAL Suite

## 👑 QUEEN'S ERWARTUNGEN

**Opus soll:**
- **Professionellen Code** liefern
- **Vollständige Implementierung** aller 3 Tools
- **Dokumentation** und Tests
- **Integration** in bestehende Architektur

**Priorität**: Hoch - kritisch für HAK_GAL Suite Entwicklung

---
**QUEEN'S AUTHORITY**: Diese Anweisungen sind bindend und müssen vollständig umgesetzt werden.