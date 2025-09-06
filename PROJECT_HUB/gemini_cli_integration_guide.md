# Gemini CLI Integration mit HAK_GAL 45 Tools
## Praktische Anleitung für MCP-Integration

### Voraussetzungen
- Gemini CLI installiert
- HAK_GAL MCP Server läuft (hakgal_mcp_v31_REPAIRED.py)
- Python 3.11+ mit .venv

---

## 1. GEMINI CLI MCP-KONFIGURATION

### Konfigurationsdatei erstellen: `gemini_mcp_config.json`
```json
{
  "mcpServers": {
    "hak-gal": {
      "type": "stdio",
      "command": ".venv\\Scripts\\python.exe",
      "args": [
        "-u",
        "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hakgal_mcp_v31_REPAIRED.py"
      ],
      "env": {
        "PYTHONIOENCODING": "utf-8",
        "PYTHONPATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL",
        "HAKGAL_WRITE_ENABLED": "true",
        "HAKGAL_WRITE_TOKEN": "",
        "HAKGAL_HUB_PATH": "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB"
      }
    }
  }
}
```

### Gemini CLI mit MCP starten:
```bash
gemini --mcp-config gemini_mcp_config.json
```

---

## 2. VERFÜGBARE TOOLS FÜR GEMINI

### Wissensbasis-Management (10 Tools)
- `get_facts_count` - Anzahl Fakten abrufen
- `search_knowledge` - Semantische Suche
- `list_recent_facts` - Neueste Fakten
- `export_facts` - Fakten exportieren
- `get_predicates_stats` - Prädikat-Statistiken
- `get_entities_stats` - Entitäts-Statistiken
- `kb_stats` - Datenbank-Statistiken
- `get_system_status` - System-Status
- `health_check` - Gesundheitsprüfung

### Datei-Management (13 Tools)
- `read_file` - Datei lesen
- `write_file` - Datei schreiben
- `list_files` - Dateien auflisten
- `get_file_info` - Datei-Info
- `directory_tree` - Verzeichnisbaum
- `create_file` - Datei erstellen
- `delete_file` - Datei löschen
- `move_file` - Datei verschieben
- `grep` - Muster suchen
- `find_files` - Dateien finden
- `search` - Einheitliche Suche
- `edit_file` - Datei bearbeiten
- `multi_edit` - Mehrfach-Bearbeitung

### Analyse-Tools (8 Tools)
- `semantic_similarity` - Ähnlichkeitssuche
- `consistency_check` - Konsistenz prüfen
- `validate_facts` - Fakten validieren
- `analyze_duplicates` - Duplikate finden
- `find_isolated_facts` - Isolierte Fakten
- `growth_stats` - Wachstumsstatistiken
- `list_audit` - Audit-Log
- `get_fact_history` - Fakt-Historie

### Abfrage-Tools (8 Tools)
- `search_by_predicate` - Prädikat-Suche
- `query_related` - Verwandte Fakten
- `get_knowledge_graph` - Knowledge-Graph
- `inference_chain` - Inferenz-Ketten
- `add_fact` - Fakt hinzufügen
- `delete_fact` - Fakt löschen
- `update_fact` - Fakt aktualisieren
- `bulk_delete` - Bulk-Löschung

### Projekt-Management (3 Tools)
- `project_snapshot` - Snapshot erstellen
- `project_list_snapshots` - Snapshots auflisten
- `project_hub_digest` - Hub-Digest

### Backup-Tools (3 Tools)
- `backup_kb` - Backup erstellen
- `restore_kb` - Backup wiederherstellen
- `bulk_translate_predicates` - Prädikate übersetzen

---

## 3. PRAKTISCHE BEISPIELE

### Beispiel 1: Wissensbasis-Analyse
```
Gemini: "Analysiere die HAK_GAL Wissensbasis und erstelle einen Bericht"

Gemini kann folgende Tools nutzen:
1. get_system_status - System-Status prüfen
2. get_facts_count - Anzahl Fakten ermitteln
3. get_predicates_stats - Top-Prädikate analysieren
4. get_entities_stats - Häufigste Entitäten finden
5. growth_stats - Wachstum analysieren
6. write_file - Bericht erstellen
```

### Beispiel 2: Code-Analyse
```
Gemini: "Analysiere die Python-Dateien im Projekt"

Gemini kann folgende Tools nutzen:
1. list_files - Python-Dateien finden
2. grep - Code-Patterns suchen
3. read_file - Dateien lesen
4. directory_tree - Projektstruktur anzeigen
5. write_file - Analyse-Bericht erstellen
```

### Beispiel 3: Automatisierte Wartung
```
Gemini: "Führe eine System-Wartung durch"

Gemini kann folgende Tools nutzen:
1. health_check - System-Gesundheit prüfen
2. consistency_check - Datenkonsistenz prüfen
3. analyze_duplicates - Duplikate finden
4. backup_kb - Backup erstellen
5. list_audit - Änderungen protokollieren
```

---

## 4. GEMINI PROMPT-VORLAGEN

### Für Wissensbasis-Arbeit:
```
Du hast Zugriff auf 45 HAK_GAL MCP Tools. Nutze sie für:
- Wissensbasis-Analyse und -Optimierung
- Automatisierte Berichterstattung
- Datenqualitätsprüfung
- Intelligente Suche und Abfragen
```

### Für Code-Analyse:
```
Nutze die verfügbaren Datei-Management-Tools für:
- Code-Review und -Analyse
- Projektstruktur-Übersichten
- Pattern-Suche in Codebase
- Automatisierte Dokumentation
```

### Für System-Monitoring:
```
Verwende die Monitoring-Tools für:
- System-Status-Überwachung
- Performance-Analyse
- Wachstums-Tracking
- Audit-Log-Analyse
```

---

## 5. FEHLERBEHEBUNG

### Häufige Probleme:

**Problem:** "Unknown tool" Fehler
**Lösung:** MCP-Server neu starten, Konfiguration prüfen

**Problem:** Verbindungsfehler
**Lösung:** Python-Pfad und .venv prüfen

**Problem:** Tool nicht verfügbar
**Lösung:** hakgal_mcp_v31_REPAIRED.py läuft korrekt?

### Debugging:
```bash
# MCP-Server direkt testen
python hakgal_mcp_v31_REPAIRED.py

# Gemini mit Debug-Output
gemini --mcp-config gemini_mcp_config.json --verbose
```

---

## 6. ERWEITERTE NUTZUNG

### Automatisierte Workflows:
```bash
# Tägliche System-Checks
gemini "Führe tägliche System-Wartung durch"

# Wöchentliche Berichte
gemini "Erstelle wöchentlichen Wissensbasis-Report"

# Monatliche Analysen
gemini "Analysiere Monats-Performance und Trends"
```

### Batch-Operationen:
```bash
# Bulk-Datenanalyse
gemini "Analysiere alle Fakten mit Prädikat 'HasProperty'"

# Automatisierte Cleanup
gemini "Entferne Duplikate und optimiere Wissensbasis"
```

---

## 7. BEST PRACTICES

### Für Gemini:
- Nutze spezifische Tool-Namen
- Gib klare Anweisungen
- Prüfe Ergebnisse vor weiteren Schritten
- Dokumentiere Änderungen

### Für MCP-Server:
- Regelmäßige Backups
- Monitoring der Tool-Performance
- Logging für Debugging
- Sicherheits-Updates

---

## 8. NÄCHSTE SCHRITTE

1. **Konfiguration testen** - Erste Tool-Verbindung
2. **Einfache Befehle** - Basis-Funktionalität
3. **Komplexe Workflows** - Automatisierung
4. **Integration** - In bestehende Prozesse

---

*Guide erstellt: 2025-01-23*  
*Status: READY FOR INTEGRATION* 🚀