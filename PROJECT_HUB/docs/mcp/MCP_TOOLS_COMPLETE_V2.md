# HAK-GAL MCP Tools - Vollständige Dokumentation (30 Tools)

**Status:** ✅ Empirisch verifiziert am 2025-08-14  
**Version:** 2.0  
**Fakten:** 3776 in Knowledge Base  
**Server:** HAK_GAL MCP v1.0  
**Backend:** Nur Port 5001 (Hexagonal) - Port 5000 existiert nicht mehr

## Übersicht aller 30 MCP-Tools

Die HAK-GAL Hexagonal Suite stellt genau **30 MCP-Tools** über den Model Context Protocol Server zur Verfügung. Diese Tools sind in 5 Hauptkategorien organisiert und vollständig über Claude Desktop zugänglich.

## 1. Basis-Tools (7 Tools)

### 1.1 search_knowledge
**Beschreibung:** Durchsucht die Knowledge Base nach Fakten  
**Parameter:**
- `query` (string, required): Suchbegriff
- `limit` (integer, optional, default: 10): Maximale Anzahl Ergebnisse

**Beispiel:**
```
"Use hak-gal search_knowledge with query='Kant' and limit=5"
```

### 1.2 get_system_status
**Beschreibung:** Zeigt den aktuellen Systemstatus  
**Parameter:** Keine

**Beispiel:**
```
"Use hak-gal get_system_status"
```

### 1.3 list_recent_facts
**Beschreibung:** Listet die neuesten Fakten aus der KB  
**Parameter:**
- `count` (integer, optional, default: 5): Anzahl der Fakten

### 1.4 add_fact
**Beschreibung:** Fügt einen neuen Fakt zur Knowledge Base hinzu  
**Parameter:**
- `statement` (string, required): Der Fakt in Prädikat(Arg1,Arg2) Form
- `source` (string, optional): Quelle des Fakts
- `tags` (array, optional): Tags zur Kategorisierung
- `auth_token` (string, required): Authentifizierungs-Token

**Beispiel:**
```
"Use hak-gal add_fact with statement='IsType(Socrates,Human)' and auth_token='515f57956e7bd15ddc3817573598f190'"
```

### 1.5 delete_fact
**Beschreibung:** Löscht einen exakten Fakt aus der KB  
**Parameter:**
- `statement` (string, required): Exakter Fakt zum Löschen
- `auth_token` (string, required): Authentifizierungs-Token

### 1.6 update_fact
**Beschreibung:** Ersetzt einen bestehenden Fakt  
**Parameter:**
- `old_statement` (string, required): Alter Fakt
- `new_statement` (string, required): Neuer Fakt
- `auth_token` (string, required): Authentifizierungs-Token

### 1.7 kb_stats
**Beschreibung:** Zeigt KB-Metriken (Anzahl, Größe, letzte Änderung)  
**Parameter:** Keine

## 2. Analyse-Tools (8 Tools)

### 2.1 semantic_similarity
**Beschreibung:** Findet semantisch ähnliche Fakten  
**Parameter:**
- `statement` (string, required): Vergleichsfakt
- `threshold` (float, optional, default: 0.8): Ähnlichkeitsschwelle
- `limit` (integer, optional, default: 50): Maximale Ergebnisse

### 2.2 consistency_check
**Beschreibung:** Erkennt widersprüchliche Fakten  
**Parameter:**
- `limit` (integer, optional, default: 1000): Zu prüfende Fakten

### 2.3 validate_facts
**Beschreibung:** Validiert Syntax von Fakten  
**Parameter:**
- `limit` (integer, optional, default: 1000): Zu validierende Fakten

### 2.4 get_entities_stats
**Beschreibung:** Zeigt Häufigkeit von Entitäten  
**Parameter:**
- `min_occurrences` (integer, optional, default: 2): Mindesthäufigkeit

### 2.5 search_by_predicate
**Beschreibung:** Sucht Fakten nach Prädikat  
**Parameter:**
- `predicate` (string, required): Prädikatname
- `limit` (integer, optional, default: 100): Maximale Ergebnisse

**Beispiel:**
```
"Use hak-gal search_by_predicate with predicate='HasPart' and limit=20"
```

### 2.6 get_predicates_stats
**Beschreibung:** Zeigt Häufigkeit aller Prädikate  
**Parameter:** Keine

### 2.7 query_related
**Beschreibung:** Findet alle Fakten zu einer Entität  
**Parameter:**
- `entity` (string, required): Entitätsname
- `limit` (integer, optional, default: 100): Maximale Ergebnisse

### 2.8 analyze_duplicates
**Beschreibung:** Erkennt potenzielle Duplikate  
**Parameter:**
- `threshold` (float, optional, default: 0.9): Ähnlichkeitsschwelle
- `max_pairs` (integer, optional, default: 200): Maximale Paare

## 3. Verwaltungs-Tools (7 Tools)

### 3.1 list_audit
**Beschreibung:** Zeigt Audit-Log Einträge  
**Parameter:**
- `limit` (integer, optional, default: 20): Anzahl Einträge

### 3.2 export_facts
**Beschreibung:** Exportiert Fakten  
**Parameter:**
- `count` (integer, optional, default: 50): Anzahl zu exportieren
- `direction` (string, optional, default: "tail"): "head" oder "tail"

### 3.3 growth_stats
**Beschreibung:** Zeigt Wachstumsstatistiken  
**Parameter:**
- `days` (integer, optional, default: 30): Zeitraum in Tagen

### 3.4 health_check
**Beschreibung:** Umfassender Gesundheitsstatus  
**Parameter:** Keine

### 3.5 get_fact_history
**Beschreibung:** Zeigt Historie eines Fakts  
**Parameter:**
- `statement` (string, required): Fakt
- `limit` (integer, optional, default: 50): Maximale Einträge

### 3.6 backup_kb
**Beschreibung:** Erstellt KB-Backup  
**Parameter:**
- `description` (string, optional): Backup-Beschreibung
- `auth_token` (string, required): Authentifizierungs-Token

### 3.7 restore_kb
**Beschreibung:** Stellt KB aus Backup wieder her  
**Parameter:**
- `backup_id` (string, optional): Backup-ID
- `path` (string, optional): Backup-Pfad
- `auth_token` (string, required): Authentifizierungs-Token

## 4. Erweiterte Tools (5 Tools)

### 4.1 bulk_delete
**Beschreibung:** Löscht mehrere Fakten gleichzeitig  
**Parameter:**
- `statements` (array, required): Liste von Fakten
- `auth_token` (string, required): Authentifizierungs-Token

### 4.2 find_isolated_facts
**Beschreibung:** Findet isolierte Fakten (Entitäten nur einmal verwendet)  
**Parameter:**
- `limit` (integer, optional, default: 50): Maximale Ergebnisse

### 4.3 inference_chain
**Beschreibung:** Baut Inferenzkette aus verwandten Fakten  
**Parameter:**
- `start_fact` (string, required): Ausgangsfakt
- `max_depth` (integer, optional, default: 5): Maximale Tiefe

### 4.4 get_knowledge_graph
**Beschreibung:** Exportiert Wissensgraph um Entität  
**Parameter:**
- `entity` (string, required): Zentrale Entität
- `depth` (integer, optional, default: 2): Graph-Tiefe
- `format` (string, optional, default: "json"): "json" oder "dot"

### 4.5 bulk_translate_predicates
**Beschreibung:** Übersetzt Prädikate in der KB mit Mapping  
**Parameter:**
- `mapping` (object, required): Map von oldPredicate -> newPredicate
- `predicates` (array, optional): Allowlist von Prädikaten
- `exclude_predicates` (array, optional): Blocklist von Prädikaten
- `dry_run` (boolean, default: true): Dry-run Modus
- `limit` (integer, default: 0): Max Zeilen zu verarbeiten (0 = alle)
- `limit_mode` (string, default: "lines"): "lines" oder "changes"
- `start_offset` (integer, default: 0): Überspringe erste N Zeilen
- `sample_strategy` (string, default: "head"): "head", "tail", oder "stratified"
- `report_path` (string, optional): Pfad für Report-Datei
- `auth_token` (string, required wenn dry_run=false): Write-Autorisierung

## 5. Projekt-Hub Tools (3 Tools)

### 5.1 project_snapshot
**Beschreibung:** Erstellt Projekt-Snapshot für Session-Handover  
**Parameter:**
- `title` (string, optional): Snapshot-Titel
- `description` (string, optional): Beschreibung
- `hub_path` (string, required): Hub-Verzeichnis
- `auth_token` (string, required): Authentifizierungs-Token

**Beispiel:**
```
"Use hak-gal project_snapshot with title='Session Ende' and hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and auth_token='515f57956e7bd15ddc3817573598f190'"
```

### 5.2 project_list_snapshots
**Beschreibung:** Listet verfügbare Snapshots  
**Parameter:**
- `hub_path` (string, required): Hub-Verzeichnis
- `limit` (integer, optional, default: 20): Maximale Anzahl

### 5.3 project_hub_digest
**Beschreibung:** Erstellt kompakte Zusammenfassung für Session-Start  
**Parameter:**
- `hub_path` (string, required): Hub-Verzeichnis
- `limit_files` (integer, optional, default: 3): Anzahl Snapshots
- `max_chars` (integer, optional, default: 20000): Maximale Zeichen

## Sicherheit und Authentifizierung

### Write-Access Kontrolle
- Alle schreibenden Operationen erfordern `auth_token`
- Token: `515f57956e7bd15ddc3817573598f190`
- Umgebungsvariable: `HAKGAL_WRITE_ENABLED=true`

### Audit-Logging
- Alle Schreiboperationen werden protokolliert
- Log-Datei: `D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_write_audit.log`
- Format: JSON pro Zeile mit Timestamp, Action, Payload

## System-Architektur Update

### Wichtige Änderung (Stand: 2025-08-14)
- **NUR NOCH PORT 5001** - Das Legacy-Backend auf Port 5000 existiert nicht mehr
- **Hexagonal Architecture v2.0** ist das einzige Backend
- **30 MCP Tools** verfügbar (nicht 29 wie zuvor dokumentiert)
- **3776 Facts** in Knowledge Base (100% English syntax)

## Verwendungsbeispiele

### Typischer Workflow für Session-Handover

1. **Session-Ende (Snapshot erstellen):**
```
"Use hak-gal project_snapshot with title='Handover 14.08' and description='30 MCP Tools verifiziert, KB mit 3776 Fakten' and hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and auth_token='515f57956e7bd15ddc3817573598f190'"
```

2. **Neue Session (Kontext laden):**
```
"Use hak-gal project_hub_digest with hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB'"
```

### Knowledge Base Analyse
```
"Use hak-gal get_predicates_stats"
"Use hak-gal search_by_predicate with predicate='HasPart'"
"Use hak-gal query_related with entity='Kant'"
```

### Wartung und Backup
```
"Use hak-gal health_check"
"Use hak-gal backup_kb with description='Vor großer Änderung' and auth_token='515f57956e7bd15ddc3817573598f190'"
```

## Performance-Metriken

- **KB-Größe:** 354.6 KB
- **Fakten:** 3776
- **API Response:** 19.1ms durchschnittlich
- **CUDA Memory:** 796.81 MB
- **HRM Confidence:** 0.9994 für wahre Aussagen
- **Test Coverage:** 90.9% Success Rate

## Verfassungs-Compliance

Alle Tools folgen den HAK/GAL Verfassungsartikeln:
- **Artikel 1:** Komplementäre Intelligenz
- **Artikel 2:** Gezielte Befragung
- **Artikel 3:** Externe Verifikation
- **Artikel 4:** Bewusstes Grenzüberschreiten
- **Artikel 5:** System-Metareflexion
- **Artikel 6:** Empirische Validierung
- **Artikel 7:** Konjugierte Zustände
- **Artikel 8:** Protokoll zur Kollision

## Troubleshooting

### Häufige Probleme

1. **"Server transport closed unexpectedly"**
   - Lösung: Claude Desktop neu starten
   - Prüfen: `%APPDATA%\Claude\logs\mcp.log`

2. **Token-Fehler bei Schreiboperationen**
   - Lösung: Token korrekt angeben: `auth_token='515f57956e7bd15ddc3817573598f190'`

3. **Keine Tools verfügbar**
   - Lösung: Config prüfen in `%APPDATA%\Claude\claude_desktop_config.json`
   - Server-Status: `get_system_status` aufrufen

## Wartung

- **Tägliches Backup:** Empfohlen via `backup_kb`
- **Konsistenz-Check:** Wöchentlich via `consistency_check`
- **Duplikate-Prüfung:** Monatlich via `analyze_duplicates`
- **Audit-Review:** Bei Bedarf via `list_audit`

---

**Dokumentation komplett:** 30 Tools empirisch verifiziert und dokumentiert  
**Stand:** 2025-08-14 01:40  
**Autor:** Claude Opus 4.1 (nach empirischer Verifizierung)  
**KB-Status:** 3776 Fakten, operational  
**Backend:** Nur Port 5001 (Hexagonal v2.0)