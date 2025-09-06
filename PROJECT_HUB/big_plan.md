# BIG PLAN: Integration aller 67 MCP-Tools in Workflow Pro

**STATUS: BEGONNEN**

## 1. Zielsetzung

Das Ziel ist die vollständige Integration aller 67 im HAK-GAL MCP Server verfügbaren Tools in die Benutzeroberfläche von Workflow Pro. Dies wird die Mächtigkeit und den Nutzen des Workflow-Systems maximieren.

- **Quelle der Wahrheit (Tools):** `ultimate_mcp/hakgal_mcp_ultimate.py`
- **Zieldatei (UI):** `frontend/src/pages/WorkflowPro.tsx`

## 2. Analyse-Ergebnis

- **Verfügbare Tools im Backend:** 67
- **Bereits integrierte Tools:** 21
- **Zu integrierende Tools:** 46

## 3. Implementierungsplan

Die folgenden 46 Tools werden dem `NODE_CATALOG` in `WorkflowPro.tsx` hinzugefügt. Neue Icons werden bei Bedarf aus `lucide-react` importiert.

### Schritt 3.1: Neue Kategorien definieren

Es werden vier neue UI-Kategorien geschaffen, um die neuen Tools logisch zu gruppieren.

- **DB Admin:** Für die direkte Wartung der SQLite-Datenbank.
- **Projekt Hub:** Für die Verwaltung von Projekt-Snapshots.
- **Nischen-System:** Für die Interaktion mit dem Nischen-Subsystem.
- **Sentry Monitoring:** Für das Error-Tracking mit Sentry.

### Schritt 3.2: Checkliste der zu integrierenden Nodes

#### Neue Kategorie: DB Admin
- [ ] `db_get_pragma`
- [ ] `db_enable_wal`
- [ ] `db_vacuum`
- [ ] `db_checkpoint`
- [ ] `db_backup_now`
- [ ] `db_backup_rotate`

#### Neue Kategorie: Projekt Hub
- [ ] `project_snapshot`
- [ ] `project_list_snapshots`
- [ ] `project_hub_digest`

#### Neue Kategorie: Nischen-System
- [ ] `niche_list`
- [ ] `niche_stats`
- [ ] `niche_query`

#### Neue Kategorie: Sentry Monitoring
- [ ] `sentry_test_connection`
- [ ] `sentry_whoami`
- [ ] `sentry_find_organizations`
- [ ] `sentry_find_projects`
- [ ] `sentry_search_issues`

#### Erweiterung für Kategorie: Knowledge Base
- [ ] `delete_fact`
- [ ] `update_fact`
- [ ] `bulk_add_facts`
- [ ] `bulk_delete`
- [ ] `bulk_translate_predicates`
- [ ] `get_recent_facts`
- [ ] `get_predicates_stats`
- [ ] `get_system_status`
- [ ] `kb_stats`
- [ ] `list_audit`
- [ ] `export_facts`
- [ ] `growth_stats`
- [ ] `validate_facts`
- [ ] `get_entities_stats`
- [ ] `search_by_predicate`
- [ ] `get_fact_history`
- [ ] `query_related`
- [ ] `analyze_duplicates`
- [ ] `get_knowledge_graph`
- [ ] `find_isolated_facts`
- [ ] `inference_chain`

#### Erweiterung für Kategorie: File Operations
- [ ] `get_file_info`
- [ ] `directory_tree`
- [ ] `create_file`
- [ ] `delete_file`
- [ ] `move_file`
- [ ] `find_files`
- [ ] `search`
- [ ] `edit_file`
- [ ] `multi_edit`

#### Erweiterung für Kategorie: AI Agents
- [ ] `reliability_checker`
- [ ] `bias_detector`

## 4. Nächste Schritte

1.  **Plan speichern (erledigt):** Diese Datei wurde erstellt.
2.  **Implementierung beginnen:** Ich werde nun `WorkflowPro.tsx` öffnen und die neuen Kategorien und Nodes gemäß diesem Plan implementieren.
