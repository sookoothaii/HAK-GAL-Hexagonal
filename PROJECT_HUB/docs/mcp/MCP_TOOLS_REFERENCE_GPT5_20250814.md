---
title: "Mcp Tools Reference Gpt5 20250814"
created: "2025-09-15T00:08:01.041612Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

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


