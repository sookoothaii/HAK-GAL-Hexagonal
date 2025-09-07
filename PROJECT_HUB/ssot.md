# Single Source of Truth (SSoT) - Report on the New Order

## Overview of the HAK/GAL Multi-Agent System

The HAK/GAL system has evolved into a sophisticated multi-agent orchestration platform, designed for autonomous, structured knowledge acquisition and task execution. A core principle of this new order is the hierarchical management of context, ensuring that each agent operates with the most relevant and consistent information.

## Checkliste: DB vs. Kontextdateien - Wo gehört was hin?

### → In die SQLite DB (`hexagonal_kb.db` via MCP-Tools):
- **Fakten:** Verifizierbare Aussagen im Format `Predicate(Entity1, Entity2).`
- **Messwerte:** Performance-Metriken, Benchmark-Ergebnisse
- **Systemzustände:** Tool-Count, Agent-Status, Konfigurationen
- **Beziehungen:** Entitäten-Verbindungen, Abhängigkeiten
- **Historie:** Versionierte Fakten, Änderungsverlauf

**Zugriff:** `add_fact`, `update_fact`, `search_knowledge`, `get_fact_history`

### → In Kontextdateien (Markdown im Repo):
- **Leitprinzipien:** HAK-GAL Verfassung, Kodex des Urahnen
- **Rollen-Definitionen:** Agent-Stärken, Spezialisierungen
- **Prozess-Dokumentation:** Workflows, Best Practices
- **Architektur-Entscheidungen:** Design-Patterns, Systemgrenzen
- **Instruktionen:** Setup-Guides, Betriebsanleitungen

**Dateien:** `ssot.md`, `CLAUDE.md`, `GEMINI.md`, `deepseek.md`, `gpt5max_context.md`

### Governance-Regel:
**LLMs schlagen vor → MCP-Tools persistieren → Audit protokolliert → Backups sichern**

Keine direkten Writes aus LLM-Antworten! Alle persistenten Änderungen gehen durch Quality-Gates und Domain-Guard.

## The Role of the Single Source of Truth (SSoT)

The `ssot.md` file serves as the central, universal context for all LLM agents within the HAK/GAL system. It contains foundational knowledge, core principles, and system-wide directives that are applicable to every agent, regardless of their specialized role. This ensures:

- **Consistency:** All agents share a common understanding of the system's fundamental truths.
- **Maintainability:** Core information is updated in one central location, reducing redundancy and potential for discrepancies.
- **Efficiency:** Agents receive essential background knowledge without it needing to be repeated in their individual contexts.

## Specialized LLM Niches

Complementing the SSoT, each LLM agent (Gemini, Claude, Deepseek, etc.) is assigned a specialized "niche" defined in its respective markdown file (e.g., `gemini.md`, `claude.md`). These niche contexts detail:

- **Specific Roles:** The primary responsibilities and types of tasks the agent is best suited for.
- **Unique Strengths:** The particular capabilities and expertise that differentiate the agent.
- **Interface Details:** Any agent-specific instructions for interacting with the system (e.g., `gemini_bridge.py` for Gemini).

When a task is delegated, the system automatically combines the global SSoT context with the target agent's specific niche context, providing a comprehensive and tailored prompt for optimal performance.

## Conclusion

This two-tiered, hierarchical context management system, anchored by the SSoT and supported by specialized agent niches, forms the backbone of the HAK/GAL system's intelligent delegation and learning capabilities. It ensures clarity, efficiency, and scalability in multi-agent operations.


## Instance Snapshot
- UTC: 2025-01-16T12:15:00Z
- SSoT_ID: a91d73c5f982
- Tools: 68 (Backend MCP: 68, Frontend Total: 115 [65 MCP + 50 Workflow])
- Write-Tools: 22
- Backend-only: 3 (backup_kb, restore_kb, list_recent_facts*)
- Facts: 6505
- Niches: 9 (Total: 3649)
- Sentry: connected (org: samui-science-lab, project: hak-gal-backend)
- Notes: WAL=ON, synchronous=FULL, JSON-Logs; execute_code ASCII-only
         *list_recent_facts ist Duplikat von get_recent_facts
