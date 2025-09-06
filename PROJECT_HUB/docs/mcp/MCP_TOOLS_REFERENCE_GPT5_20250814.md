### MCP Tools Reference (Cursor)

Stand: 2025-08-14

- Read (operativ)
  - `health_check`, `kb_stats`, `get_system_status`
  - `get_predicates_stats`, `search_knowledge`, `search_by_predicate`
  - `list_recent_facts`, `list_audit`, `export_facts`
  - `growth_stats`, `get_knowledge_graph`, `find_isolated_facts`, `inference_chain`
  - `project_list_snapshots`, `project_hub_digest`

- Write (gated)
  - `add_fact`, `update_fact`, `delete_fact`, `bulk_delete`
  - `backup_kb`, `restore_kb`, `project_snapshot`, `bulk_translate_predicates` (dry-run by default)

Hinweise
- Write‑Gate: `.cursor/mcp.json` → `HAKGAL_WRITE_ENABLED` + Token. Nach Nutzung wieder schließen.
- SQLite ist Source of Truth; MCP‑Write trifft SQLite über die Hexagonal‑API.
- Audit: `mcp_write_audit.log` nachschauen.


