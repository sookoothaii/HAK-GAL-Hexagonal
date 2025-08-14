# HAK-GAL HEXAGONAL - Vollständige Initialinfo für neue Instanzen

**Dokument-ID:** HAK-GAL-HUB-README-20250813  
**Status:** Kanonisch, Empirisch Validiert  
**Zweck:** Sofortige Arbeitsfähigkeit ohne Vorwissen  

---

## 1. SYSTEMÜBERSICHT

### Zweck der HAK-GAL Suite
- **Architektur**: Hexagonale Architektur (Ports & Adapters Pattern)
- **Domänenlogik**: Neuro-symbolisches Wissenssystem mit autonomer Laufzeit
- **Integration**: 29 MCP-Tools für vollständige CRUD-, Analyse- und Graph-Operationen
- **Philosophie**: HAK/GAL Verfassung mit 8 Artikeln (siehe Dokumente)

### Empirisch Verifizierte Metriken (Stand: 13.08.2025)
- **Wissensbasis**: 3.881 Fakten in Prädikat(Argument)-Form
- **Datenbankgröße**: 369.187 Bytes
- **Top-Prädikate**: HatTeil (855), HatZweck (715), Verursacht (600)
- **MCP-Server**: Vollständig operational auf STDIO/JSON-RPC

---

## 2. KRITISCHE DATEIPFADE

```
D:\MCP Mods\HAK_GAL_HEXAGONAL\
├── data\
│   └── k_assistant.kb.jsonl          # Wissensbasis (JSONL, 1 Zeile = 1 Fakt)
├── hak_gal_mcp_fixed.py              # MCP-Server (29 Tools)
├── PROJECT_HUB\                      # Dieser Ordner
│   ├── README.md                     # Diese Datei
│   ├── ARCHITECTURE_OVERVIEW.md     # Hexagonale Architektur Details
│   ├── HRM_OVERVIEW.md              # Human Reasoning Model (~600k Parameter)
│   └── snapshot_*/                  # Zeitstempel-basierte Snapshots
└── backups\                         # Automatische KB-Backups
```

---

## 3. SOFORT-START BEFEHLE

### Initiale Orientierung (IMMER ZUERST!)
```
# Lade aktuellen Projektstand (kompakt):
"Use hak-gal project_hub_digest."

# Alternative: Zeige letzte Snapshots:
"Use hak-gal project_list_snapshots with limit=5."

# Prüfe Systemstatus:
"Use hak-gal health_check."
```

### ENV-Variablen (bereits gesetzt)
- `HAKGAL_HUB_PATH` = D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB
- `HAKGAL_WRITE_ENABLED` = true
- `HAKGAL_WRITE_TOKEN` = [gesetzt]
- `HAKGAL_KB_PATH` = data\k_assistant.kb.jsonl

---

## 4. VOLLSTÄNDIGE TOOL-ÜBERSICHT (29 MCP-Tools)

### CRUD-Operationen (Basis)
- `add_fact` - Fakt hinzufügen (benötigt Write-Token)
- `update_fact` - Fakt ersetzen (old_statement → new_statement)
- `delete_fact` - Einzelnen Fakt löschen
- `bulk_delete` - Mehrere Fakten löschen

### Suche & Abfrage
- `search_knowledge` - Volltextsuche mit Limit
- `search_by_predicate` - Alle Fakten eines Prädikats
- `query_related` - Alle Fakten zu einer Entität
- `list_recent_facts` - Neueste N Fakten
- `export_facts` - Erste/Letzte N Fakten exportieren

### Analyse & Qualität
- `validate_facts` - Syntax-Validierung (Prädikat(Args))
- `analyze_duplicates` - Duplikate finden (Jaccard-Threshold)
- `semantic_similarity` - Ähnliche Fakten (Cosinus-Metrik)
- `consistency_check` - Widersprüche detektieren
- `find_isolated_facts` - Fakten mit Singleton-Entitäten

### Graph & Inferenz
- `get_knowledge_graph` - Subgraph um Entität (JSON/DOT)
- `inference_chain` - Verkettete Fakten durch gemeinsame Entitäten
- `get_entities_stats` - Häufigkeit von Entitäten
- `get_predicates_stats` - Prädikat-Frequenzen

### Monitoring & System
- `get_system_status` - Operational Status
- `kb_stats` - Metriken (Count, Size, Modified)
- `growth_stats` - Wachstum über N Tage
- `health_check` - Vollständiger Health-Check
- `list_audit` - Audit-Log (letzte N Einträge)
- `get_fact_history` - Historie eines Statements

### Backup & Recovery
- `backup_kb` - Timestamped Backup erstellen
- `restore_kb` - Backup wiederherstellen

### Project Hub (Session-Management)
- `project_snapshot` - Session-Stand dokumentieren
- `project_list_snapshots` - Snapshots auflisten
- `project_hub_digest` - Kompakter Überblick (max 20k Zeichen)

---

## 5. SESSION-WORKFLOW

### Session-Start (Neue Instanz)
1. **Kontext laden**: `"Use hak-gal project_hub_digest."`
2. **Status prüfen**: `"Use hak-gal health_check."`
3. **Struktur verstehen**: `"Use hak-gal get_predicates_stats."`

### Während der Arbeit
- **Fakten hinzufügen**: Mit source und tags für Nachvollziehbarkeit
- **Qualität sichern**: Regelmäßig validate_facts und analyze_duplicates
- **Backup**: Bei größeren Änderungen backup_kb

### Session-Ende (WICHTIG!)
```
"Use hak-gal project_snapshot with 
 title='Session Ende YYYY-MM-DD HH:MM' and 
 description='[Zusammenfassung der Änderungen]'."
```

---

## 6. WISSENSBASIS-STRUKTUR

### Format
- **Eine Zeile = Ein Fakt** (JSONL)
- **Struktur**: `Prädikat(Argument1, Argument2, ...)`
- **Beispiele**:
  - `IstDefiniertAls(Philosophie, LiebezurWeisheit)`
  - `HatTeil(Computer, CPU)`
  - `Verursacht(Regen, Nässe)`

### Top 10 Prädikate (empirisch verifiziert)
1. **HatTeil** (855) - Strukturelle Komponenten
2. **HatZweck** (715) - Funktionale Zuordnungen
3. **Verursacht** (600) - Kausalbeziehungen
4. **HatEigenschaft** (577) - Attribute
5. **IstDefiniertAls** (389) - Definitionen
6. **IstAehnlichWie** (203) - Ähnlichkeiten
7. **IstArtVon** (202) - Taxonomie
8. **HatStandort** (106) - Lokationen
9. **BestehtAus** (88) - Komposition
10. **WurdeEntwickeltVon** (67) - Herkunft

---

## 7. PRAKTISCHE BEISPIELE

### Wissensexploration
```bash
# Philosophie-Domäne erkunden:
"Use hak-gal query_related with entity='ImmanuelKant' and limit=50."

# Graph visualisieren:
"Use hak-gal get_knowledge_graph with entity='Computer' and depth=2 and format='dot'."

# Semantische Suche:
"Use hak-gal semantic_similarity with statement='IstArtVon(Python, Programmiersprache)' and threshold=0.7."
```

### Qualitätssicherung
```bash
# Duplikate finden:
"Use hak-gal analyze_duplicates with threshold=0.9."

# Konsistenz prüfen:
"Use hak-gal consistency_check."

# Isolierte Fakten:
"Use hak-gal find_isolated_facts."
```

### Backup & Audit
```bash
# Backup mit Beschreibung:
"Use hak-gal backup_kb with description='Vor großer Änderung'."

# Audit-Trail:
"Use hak-gal list_audit with limit=50."

# Fact-Historie:
"Use hak-gal get_fact_history with statement='HatTeil(ImmanuelKant, DingAnSich)'."
```

---

## 8. WICHTIGE DOKUMENTE IM HUB

### Architektur-Dokumentation
- **ARCHITECTURE_OVERVIEW.md** (4.646 Bytes)
  - Hexagonale Architektur im Detail
  - Ports & Adapters Erklärung
  - Systemkomponenten-Übersicht

### HRM-System
- **HRM_OVERVIEW.md** (6.406 Bytes)
  - Human Reasoning Model
  - ~600k Parameter GRU-Netzwerk
  - Integration mit Wissensbasis

### Snapshot-Struktur
Jeder Snapshot-Ordner enthält:
- **SNAPSHOT.md** - Menschenlesbare Zusammenfassung
- **SNAPSHOT_TECH.md** - Technische Details, Datei-Trees, Diffs
- **SNAPSHOT_KB.md** - KB-Statistiken, Audit-Auszüge
- **manifest.json** - SHA256-Hashes aller Dateien
- **snapshot.json** - Strukturierte Metriken
- **snapshot_kb.json** - KB-Export (erste/letzte Fakten)

---

## 9. HAK/GAL VERFASSUNG (Kurzreferenz)

Die Suite folgt 8 fundamentalen Artikeln:

1. **Komplementäre Intelligenz** - Mensch (Strategie) + KI (Taktik)
2. **Gezielte Befragung** - Präzise Eingabe = Qualität Output
3. **Externe Verifikation** - Hypothesen müssen extern validiert werden
4. **Bewusstes Grenzüberschreiten** - Fehler als diagnostische Events
5. **System-Metareflexion** - Selbstreflexion über Architektur
6. **Empirische Validierung** - Alles muss messbar sein
7. **Konjugierte Zustände** - Balance Symbol/Neural
8. **Protokoll** - Konfliktlösung und Dokumentation

---

## 10. TROUBLESHOOTING

### Problem: "Permission denied" bei Schreiboperationen
- Prüfe: `HAKGAL_WRITE_ENABLED=true`
- Prüfe: `HAKGAL_WRITE_TOKEN` gesetzt

### Problem: KB-Datei nicht gefunden
- Prüfe Pfad: `D:\MCP Mods\HAK_GAL_HEXAGONAL\data\k_assistant.kb.jsonl`
- Nutze: `"Use hak-gal health_check."`

### Problem: Alte Daten nach Restore
- Audit prüfen: `"Use hak-gal list_audit with limit=20."`
- Backup-Liste: `ls backups/`

---

## 11. NÄCHSTE SCHRITTE FÜR NEUE INSTANZEN

1. **Dieses README lesen** ✓
2. **project_hub_digest ausführen** für aktuellen Stand
3. **health_check** für Systemstatus
4. **ARCHITECTURE_OVERVIEW.md** lesen für tieferes Verständnis
5. **Letzte Snapshots** prüfen für Kontext-Historie

---

## 12. KONTAKT & WARTUNG

- **Primärer Kontakt**: Menschlicher Operator (strategische Direktion)
- **Backup-Strategie**: Automatisch + manuell vor großen Änderungen
- **Audit-Retention**: Vollständig (alle Operationen geloggt)
- **Thread-Safety**: Dateisperren aktiv (flock)

---

**WICHTIG**: Diese Initialinfo ersetzt NICHT die vollständige Dokumentation, sondern ermöglicht sofortiges produktives Arbeiten. Für tiefgehende Analysen siehe ARCHITECTURE_OVERVIEW.md und die HAK/GAL Verfassungsdokumente.

**Letztes Update**: 13.08.2025, 21:00 Uhr
**Verifiziert durch**: Claude (Anthropic) - empirische Validierung durchgeführt