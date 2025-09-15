---
title: "Tech Report Hakgal Mcp 20250815"
created: "2025-09-15T00:08:01.133143Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technical Report - HAK-GAL MCP Server (2025-08-15)

## Überblick
Der HAK-GAL MCP-Server stellt 30 Tools per MCP/STDIO für Cursor/Claude bereit. Der Server bedient die HEXAGONAL Knowledge Base und ermöglicht Read/Write-Operationen inklusive Projekt-Snapshots.

- Server: HAK_GAL MCP v1.0
- KB: `D:\MCP Mods\HAK_GAL_HEXAGONAL\data\k_assistant.kb.jsonl`
- Facts: 3776 (ca. 354 KB)
- Letzte Änderung: 2025-08-14 01:17:16
- Integration: `.cursor/mcp.json` (Profile für readonly/write vorhanden)

## Tools (Auszug, 30 gesamt)
- search_knowledge, get_system_status, list_recent_facts, add_fact, delete_fact, update_fact, kb_stats, list_audit, export_facts, growth_stats
- health_check, semantic_similarity, consistency_check, validate_facts, get_entities_stats, search_by_predicate, get_fact_history
- backup_kb, restore_kb, bulk_delete, get_predicates_stats, query_related, analyze_duplicates, get_knowledge_graph, find_isolated_facts, inference_chain, bulk_translate_predicates
- project_snapshot (auth), project_list_snapshots, project_hub_digest

## Funktionsprüfung (Smoke-Test)
- tools/list -> 30 Tools erkannt
- health_check -> OK; KB vorhanden; write_enabled konfigurierbar
- kb_stats -> Count=3776; Size=354607; LastModified=2025-08-14 01:17:16
- get_system_status -> operational; Pfade ok
- search_knowledge("system", 3) -> 3 Treffer

## Snapshot-Erstellung (MCP)
- Vorgang: `project_snapshot(title, description, hub_path, auth_token)`
- Hub: `D:\MCP Mods\HAK_GAL_HEXAGONAL\PROJECT_HUB`
- Ergebnis: `snapshot_20250815_213625` erzeugt
- Inhalte: `SNAPSHOT_KB.md`, `snapshot_kb.json`, `SNAPSHOT_TECH.md`, `SNAPSHOT.md`
- Nachweis: `project_list_snapshots` listet neuesten Snapshot; `project_hub_digest` fasst Inhalte zusammen

## Architektur (Kurz)
- Start: `python -m hak_gal_mcp` -> STDIO JSON-RPC (`initialize`, `tools/list`, `tools/call`)
- Datei: `hak_gal_mcp_fixed.py` implementiert Tool-Routen und Sicherheit (`_is_write_allowed`)
- ENV-Steuerung:
  - `HAKGAL_WRITE_ENABLED=true|false`
  - `HAKGAL_WRITE_TOKEN` (optional, für Auth)
  - `HAKGAL_HUB_PATH` (Snapshots/Reports)
  - `HAKGAL_API_BASE_URL` (Backend-Interaktion)

## Sicherheitsempfehlungen
- Default auf Readonly: `.cursor/mcp.json` per `scripts/switch_mcp_profile.ps1 -Profile readonly` setzen
- Token nicht fest im Default-Profil speichern; über Env `HAKGAL_WRITE_TOKEN` injizieren
- Write nur temporär aktivieren; Audit-Log (`mcp_write_audit.log`) regelmäßig prüfen

## Operationelle Hinweise
- Smoke-Test: `.\.venv_hexa\Scripts\python.exe scripts\smoke_mcp.py`
- Snapshot: per MCP `project_snapshot` oder über bestehenden Automation-Flow
- Profile umschalten: `scripts/switch_mcp_profile.ps1 -Profile readonly|write`

## Status
- MCP-Server funktionsfähig, 30 Tools aktiv
- Snapshot erfolgreich erzeugt und abgelegt
- Sicherer Read/Write-Betrieb über Profilumschaltung gewährleistet
