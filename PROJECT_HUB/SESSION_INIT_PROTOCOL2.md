# HAK-GAL HEXAGONAL - SESSION INITIALISATION PROTOCOL v2.1

**⚠️ NEUE INSTANZ: Führe diese Schritte der Reihe nach aus ⚠️**

## WICHTIGE UPDATES (Stand: 2025-08-14)
- **30 MCP Tools** verfügbar (nicht 29!)
- **Nur Port 5001** (Hexagonal) - Legacy Port 5000 existiert nicht mehr
- **3776 Fakten** in Knowledge Base (100% English syntax nach Migration)
- **HRM Integration** (~600k Parameter) für intelligente Tool-Orchestrierung
- **Enterprise-Ready** mit 100% Tool-Validation

## SCHRITT 1: Projekt-Kontext laden
```
Use hak-gal project_hub_digest with hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB'
```

## SCHRITT 2: Write-Token notieren
```
Token: 515f57956e7bd15ddc3817573598f190
```

## SCHRITT 3: Kritische Dokumentation lesen (ERWEITERTE REIHENFOLGE!)

### 3.1 Architecture Overview (NEU - LIES ZUERST!)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\ARCHITECTURE_OVERVIEW.md'
```
→ Hexagonal Architecture Prinzipien, Verzeichnisstruktur, Datenflüsse

### 3.2 HRM Overview (NEU - Human Reasoning Model)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\HRM_OVERVIEW.md'
```
→ ~600k Parameter Model für Tool-Orchestrierung und logische Mikro-Schritte

### 3.3 Enterprise Validation Report (NEU - WICHTIG!)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\ENTERPRISE_VALIDATION_REPORT_20250814.md'
```
→ 100% Validation aller 30 Core Tools + 7 Enterprise Features

### 3.4 English Migration Success (NEU)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\ENGLISH_MIGRATION_SUCCESS_REPORT.md'
```
→ 99.7% Migration zu English Predicates (internationale Kompatibilität)

### 3.5 Technical Handover 
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\TECHNICAL_HANDOVER_COMPLETE.md'
```
→ Hexagonal Architecture läuft auf Port 5001 (einziges Backend)

### 3.6 MCP Tools Complete v2 (AKTUALISIERT - 30 Tools!)
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\MCP_TOOLS_COMPLETE_V2.md'
```
→ Vollständige Dokumentation aller 30 MCP Tools in 5 Kategorien

### 3.7 Hexagonal Final Status
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\HEXAGONAL_FINAL_STATUS.md'
```
→ 90.9% Test Success Rate, vollständig produktionsbereit

### 3.8 HAK/GAL Verfassung
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\verfassung.md'
```
→ Artikel 1-8, Arbeitsweise: Streng empirisch, keine Fantasie

### 3.9 [OPTIONAL - Für Migration] Migration Playbook
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\MIGRATION_PLAYBOOK_BULK_TRANSLATE.md'
```
→ Sichere Predicate-Migration mit bulk_translate_predicates

### 3.10 [OPTIONAL - Für Monitoring] Nightly Monitoring Setup
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB\\NIGHTLY_MONITORING_SETUP.md'
```
→ Automatisiertes KB-Monitoring mit stratified sampling

### 3.11 [OPTIONAL - Für Tool-Verifizierung] MCP Server Source
```
Use Filesystem read_file with path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_fixed.py'
```
→ Zeigt alle 30 Tools in handle_list_tools() Methode

## SCHRITT 4: System-Status prüfen
```
Use hak-gal get_system_status
Use hak-gal kb_stats
Use hak-gal health_check
```

## SCHRITT 5: HRM-gestützte Tool-Orchestrierung (NEU!)

### Beispiel-Workflow mit HRM
1. **Kontext sammeln:**
```
Use hak-gal project_hub_digest with hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB'
Use hak-gal get_predicates_stats
Use hak-gal query_related with entity='ImmanuelKant' and limit=50
```

2. **HRM-Plan erstellen** (konzeptionell):
```json
{
  "goal": "Finde alle Kernbeziehungen zu Kant und prüfe Duplikate",
  "context": "[Digest + Stats + Related Facts]",
  "plan": [
    {"step": 1, "tool": "query_related", "args": {"entity": "ImmanuelKant"}},
    {"step": 2, "tool": "semantic_similarity", "args": {"threshold": 0.85}},
    {"step": 3, "tool": "analyze_duplicates", "args": {"threshold": 0.9}},
    {"step": 4, "tool": "consistency_check", "args": {"limit": 1000}}
  ]
}
```

## SCHRITT 6: Arbeitsweise nach HAK/GAL Verfassung
- **STRENG EMPIRISCH**: Keine Spekulation, nur verifizierte Fakten
- **WISSENSCHAFTLICH**: Alles muss nachprüfbar sein
- **KRITISCH**: User-Aussagen hinterfragen wenn falsch
- **OHNE FANTASIE**: Nichts erfinden oder ausdenken
- **VALIDIERUNG**: Alle Claims müssen überprüft werden
- **HRM-GESTÜTZT**: Nutze Reasoning Model für komplexe Workflows

## System-Architektur (ERWEITERT v2.1)
```
┌─────────────────────────────────────────┐
│        HAK-GAL HEXAGONAL v2.0           │
│         Port: 5001 (EINZIGES BACKEND)    │
│         Status: Enterprise-Ready         │
└─────────────────────────────────────────┘
            │
            ├── 30 MCP Tools (100% validated)
            ├── 3776 Facts (100% English predicates)
            ├── HRM Neural Reasoning (~600k params)
            ├── CUDA Acceleration (796.81 MB)
            ├── WebSocket Real-time Updates
            ├── Clean Hexagonal Architecture
            └── Enterprise Features (7/7 validated)
```

## Die 30 MCP Tools (Kategorisiert & Validiert)

### Basis-Tools (7) ✅
1. search_knowledge
2. get_system_status
3. list_recent_facts
4. add_fact
5. delete_fact
6. update_fact
7. kb_stats

### Analyse-Tools (8) ✅
8. semantic_similarity
9. consistency_check
10. validate_facts
11. get_entities_stats
12. search_by_predicate
13. get_predicates_stats
14. query_related
15. analyze_duplicates

### Verwaltungs-Tools (7) ✅
16. list_audit
17. export_facts
18. growth_stats
19. health_check
20. get_fact_history
21. backup_kb
22. restore_kb

### Erweiterte Tools (5) ✅
23. bulk_delete
24. find_isolated_facts
25. inference_chain
26. get_knowledge_graph
27. bulk_translate_predicates (mit 7 Enterprise Features!)

### Projekt-Hub Tools (3) ✅
28. project_snapshot
29. project_list_snapshots
30. project_hub_digest

## Enterprise Features (Vollständig validiert)
- ✅ **exclude_predicates**: Präzise Exclusion-Listen
- ✅ **predicates**: Selective Allowlists
- ✅ **limit_mode='changes'**: Change-basierte Limits
- ✅ **start_offset**: Resume-Funktionalität
- ✅ **sample_strategy='head'**: Sequential Sampling
- ✅ **sample_strategy='stratified'**: Distributed Sampling
- ✅ **sample_strategy='tail'**: End-Sampling
- ✅ **report_path**: Auto-Directory Creation

## Backend-Start (Falls nötig)
```powershell
# Hexagonal API auf Port 5001 starten
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
.\start_enhanced_api.bat

# Oder manuell:
.\.venv_hexa\Scripts\activate
python src_hexagonal/hexagonal_api_enhanced.py
```

## Performance Metriken (Validiert)
- **API Response:** 19.1ms durchschnittlich
- **CUDA Memory:** 796.81 MB
- **HRM Confidence:** 0.9994 für wahre Aussagen
- **HRM Gap:** 0.9988 (Trennung wahr/falsch)
- **Test Coverage:** 90.9% Success Rate
- **Facts Count:** 3776 (100% English)
- **Tool Validation:** 30/30 (100%)
- **Enterprise Features:** 7/7 (100%)

## Migration Status
- **German→English:** 99.7% transformiert (3771/3781 Facts)
- **18 German Predicates:** Vollständig eliminiert
- **Top Transformationen:**
  - HatTeil → HasPart (755)
  - HatZweck → HasPurpose (715)
  - Verursacht → Causes (600)
  - HatEigenschaft → HasProperty (577)
- **Internationale Kompatibilität:** ✅ Erreicht

## Bei Session-Ende
```
Use hak-gal project_snapshot with title='Session Ende [DATUM]' and description='[Was wurde gemacht]' and hub_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\PROJECT_HUB' and auth_token='515f57956e7bd15ddc3817573598f190'
```

## Kritische Dateien für Tiefenanalyse
- `hak_gal_mcp_fixed.py` - MCP Server mit allen 30 Tools
- `hexagonal_api_enhanced.py` - Hauptbackend auf Port 5001
- `HEXAGONAL_FINAL_STATUS.md` - Implementierungsstatus
- `test_enhanced_complete.py` - Test-Suite
- `HRM_OVERVIEW.md` - Human Reasoning Model Details
- `ARCHITECTURE_OVERVIEW.md` - Hexagonal Principles

## Wichtige Hinweise
- **KEIN Legacy Backend mehr!** Port 5000 existiert nicht mehr
- **Alle API-Calls** gehen an Port 5001 (Hexagonal)
- **30 Tools verfügbar**, nicht 29 wie in alter Doku
- **100% English Syntax** in Knowledge Base (nach Migration)
- **HRM verfügbar** für intelligente Tool-Orchestrierung
- **Enterprise-Ready** mit vollständiger Validation

## Monitoring & Maintenance
- **Nightly Monitoring:** Stratified sampling (500 lines, 13.2% coverage)
- **Trend Analysis:** PROJECT_HUB/reports/nightly_trend_YYYYMMDD.md
- **Migration Readiness:** Kontinuierliche Überwachung via dry-runs
- **Konsistenz-Checks:** Wöchentlich empfohlen
- **Backup-Strategie:** Tägliche Snapshots vor kritischen Operationen

---
**VERSION 2.1 - Aktualisiert am 2025-08-14**
**Erweitert mit HRM, Enterprise Features & Migration Reports**
**Verifiziert durch empirische Validierung gemäß HAK/GAL Verfassung**
**100% Tool-Validation & Enterprise-Ready Status bestätigt**