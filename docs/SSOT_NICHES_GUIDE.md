# HAK_GAL SSoT + Nischen + MCP – Kanonischer Leitfaden (für LLMs)

Ziel
- Einheitliche, reproduzierbare Anleitung für neue LLM‑Instanzen (Claude, DeepSeek, Gemini, GPT5).
- SSoT‑first, Nischen‑fokussiert, MCP‑gestützt, ASCII‑only, keine Schreibaktionen ohne Freigabe.

1) Architektur
- SSoT Daten: hexagonal_kb.db (SQLite; Fakten im Prädikat‑Format; WAL/FULL; Backups/Rotation/VACUUM)
- SSoT Kontext: ssot.md (Projektkompass + Snapshots), *_context.md (Agent‑Leitplanken)
- Nischen (Layer‑2): niches\*.db (kuratiert, Keyword+Token‑Relevanz; read‑only über MCP)
- MCP‑Server: ultimate_mcp\hakgal_mcp_ultimate.py (66 Tools, JSON‑RPC stdin/stdout)
- Sentry: DSN URL + REST/API (Org samui-science-lab; Projekt hak-gal-backend)

2) Goldene Regeln
- ASCII‑only; kurz, präzise; kein Flooding
- MCP: method:"tools/call" (nicht Direktmethoden)
- Read‑only by default; Schreibaktionen nur mit Freigabe
- SSoT_ID: SHA256(ssot.md)[:12] – immer im Prompt‑Header verwenden

3) Standard‑Start (read‑only Vorschlag)
- Operator führt aus: tools/list; get_system_status; health_check_json; niche_list
- LLM liest: ssot.md + eigene *_context.md → berechnet SSoT_ID
- READY‑Block:
  - Tools=<n> (Soll: 66), Facts≈<n>, Niches=<n>/<summe>, Sentry=<status>
  - Empfohlene Checks: kb_stats, get_predicates_stats, semantic_similarity, consistency_check, validate_facts
  - Nischen: niche_stats(<kernnische>), niche_query(<kernnische>,"<begriff>",5)

4) Nischen (read‑only)
- niche_list → Übersicht (Anzahl, Summe, Schwellen/Keywords)
- niche_stats(name) → Facts, Relevanz min/avg/max, Telemetrie, Top‑Fakten
- niche_query(name,q,limit) → Treffer nach Relevanz

5) Faktenpflege (nur mit Freigabe)
- add_fact/update_fact/delete/bulk_delete – mit Gates/Domain‑Guard, Punkt am Satzende
- Backups: db_backup_now; Rotation db_backup_rotate; db_vacuum wöchentlich
- Audit: mcp_write_audit.log; get_fact_history

6) Sentry (optional)
- SENTRY_DSN=https://<publicKey>@de.sentry.io/<projectId>
- Tests: sentry_test_connection; sentry_find_projects(org); sentry_search_issues(query,limit)

7) Delegation (Prefix‑Modelle)
- DeepSeek: "DeepSeek:chat"
- Gemini: "Gemini:2.5-flash" (keine JSON‑RPC‑Payloads an Gemini direkt senden)
- Claude: "Claude:sonnet"
- Prompt‑Header: SSoT_ID + Agent + Guidelines

8) Persistenz – Snapshots
- ssot.md: Snapshot (UTC, SSoT_ID, Tools, Facts, Niches, Sentry)
- DB: kompakte Statusfakten (ToolCount/FactCount/NicheCount/…)

9) Fehlerbilder
- 400 INVALID_ARGUMENT (Gemini): keine MCP‑JSON‑RPC Payload an Gemini senden
- Toolzahl 59/63/66: maßgeblich tools/list/get_system_status (Server neu initialisieren)
- whoami 404: Token‑Scope; Projekte/Issues reichen

10) Phase‑2 Vorschläge
- Embeddings (SentenceTransformers) hinter Keyword‑Gate
- Auto‑Tuning für Nischen‑Thresholds; Drift‑Detection
- Prometheus‑Exporter; Konsens‑Pipelines; Admin‑API mit Auth
