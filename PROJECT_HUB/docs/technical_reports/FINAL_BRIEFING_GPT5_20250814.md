---
title: "Final Briefing Gpt5 20250814"
created: "2025-09-15T00:08:01.103665Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

### Abschluss-Briefing — Wichtige Punkte für den Betrieb (GPT‑5)

Datum: 2025‑08‑14

---

- Sicherheit/Schreiben
  - Write‑Gate standardmäßig geschlossen halten; nur kurz für geplante Aktionen öffnen; Token nie ins Repo; Audit über `mcp_write_audit.log` prüfen.
  - Kill‑Switch im Backend respektieren; nach Bulk‑Ops wieder auf „safe“.

- Operativer Betrieb
  - MCP‑Tools in Cursor nutzen (Health, Stats, Snapshots lesen) statt direkter HTTP‑Calls.
  - Nur Port 5001 (Hexagonal); keine 5000‑Reste reaktivieren.
  - `.cursor/mcp.json` ist die Schaltzentrale (ENV, Write‑Gate).

- Datenquelle
  - SQLite ist Source of Truth; JSONL nur lesen/exportieren.
  - Regelmäßig `scripts/optimize_database.py` ausführen (ANALYZE/PRAGMA optimize/VACUUM).
  - Migrationen: `scripts/import_jsonl_to_sqlite.py` und anschließend Konsistenzprüfungen.

- Backups
  - PowerShell‑Backup mit SQLite‑native Backup verwenden; gesperrte Dateien überspringen.
  - Backups versionieren; Restore testweise verifizieren.

- Qualität/Knowledge Growth
  - Aethelred parallelisieren, aber Growth‑Metriken beobachten (keine Junk‑Inflation).
  - Optionales Confidence‑Gate beibehalten; menschliche Reviews für sensible Domänen.

- Monitoring/Slack
  - Slack‑Webhook als Secret behandeln; tägliche Status‑Posts (Health/Stats/Top‑Predicates/Growth).
  - Bei Fehlern: Webhook neu erzeugen oder Netzwerk/Proxy prüfen (443).

- Entwicklung/IDE
  - Immer im Projekt‑venv arbeiten (ansonsten Python/Deps problematisch).
  - Frontend: Pagination/Virtualization nutzen; große Payloads vermeiden.

- Sicherheit/Compliance
  - Keine Secrets im Repo; Token rotieren; perspektivisch Auth/RBAC/Rate‑Limit.
  - Input‑Validierung & Audit trail pflegen.

- Git/Repo‑Hygiene
  - `.gitignore` sauber halten; große Artefakte/Backups nicht committen.
  - Hub‑Doku & Snapshots fortführen (Handover, Auto‑Status).

- Don’ts
  - Kein PowerShell‑`curl` für API‑Tests (Alias‑Fallen) — stattdessen MCP‑Tools nutzen.
  - Keine LLM‑Proxy‑Rückfälle auf Port 5000.


