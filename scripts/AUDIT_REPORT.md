# HAK-GAL SCRIPTS AUDIT REPORT

Datum: 2025-09-22 00:14
Analysierte Dateien: 411

## ZUSAMMENFASSUNG
- Kritische Systemdateien: 37
- Zu konsolidierende Gruppen: 23
- Zu archivierende Tests: 11
- Zu lÃ¶schende Dateien: 1

## KRITISCHE SYSTEMDATEIEN (BEHALTEN)
- api_sync_endpoints.py
- backup_server.py
- claude_api_watcher.py
- discover_api_endpoints.py
- find_api_format.py
- force_start_generator.py
- force_start_governor.py
- hak_gal_mcp_broken.py
- hak_gal_mcp_fixed.py
- hak_gal_mcp_sqlite.py
- hak_gal_mcp_sqlite_full.py
- hak_gal_mcp_v2.py
- lightweight_api.py
- minimal_test_server.py
- monitor_api_completeness.py
- niche_flask_api.py
- optimized_flask_server.py
- production_server.py
- prometheus_server.py
- quick_api_test.py

## ZU KONSOLIDIERENDE DUPLIKATE

### advanced_growth_engine.py
  - advanced_growth_engine_fixed.py

### count_facts.py
  - count_facts_real.py

### direct_monitor.py
  - direct_monitor_improved.py

### enable_llm.py
  - enable_llm_v6.py

### extract_node_catalog.py
  - extract_node_catalog_improved.py

### focused_growth_engine.py
  - focused_growth_engine_v2.py

### hakgal_mcp_REPAIRED.py
  - hakgal_mcp_v31_REPAIRED.py

### integrate_governance.py
  - integrate_governance_v3.py

### intelligent_predicate_explorer.py
  - intelligent_predicate_explorer_v2.py

### kb_visualizer.py
  - kb_visualizer_fixed.py

## EMPFOHLENE NEUE STRUKTUR

    scripts/
    â”œâ”€â”€ core/              # Systemkern (MCP-Server, API, Governance)
    â”œâ”€â”€ engines/           # Fact-Generierung (Aethelred, Thesis)
    â”œâ”€â”€ analysis/          # Analyse-Tools
    â”œâ”€â”€ maintenance/       # Wartungs-Skripte
    â”œâ”€â”€ tests/             # Aktive Tests (<7 Tage)
    â””â”€â”€ _archive/          # Alte Versionen (Referenz)
    

## POTENZIELLE REDUKTION
Von 411 auf ~60 Dateien (85% Reduktion)