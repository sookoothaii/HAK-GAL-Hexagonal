---
title: "Technical Handover Gpt5 Extended 20250814"
created: "2025-09-15T00:08:01.030085Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technischer Handover — HAK_GAL_HEXAGONAL (GPT‑5, Extended)

Datum: 2025‑08‑14
Autor: GPT‑5
Zielgruppe: Technische Leitung, Entwickler, DevOps

## 1. Executive Summary
- System ist vollständig auf **Hexagonal‑Architektur** umgestellt und läuft ausschließlich auf **Port 5001**.
- **SQLite** ist jetzt die **Source of Truth (SoT)**; **JSONL** dient nur noch als Export/Archiv.
- **Legacy‑Proxys** (Port 5000) wurden entfernt; LLM‑Erklärungen laufen nur über interne Provider oder liefern 503 (klare Meldung).
- Die Wissensbasis enthält aktuell ~3.8k Fakten (Import + neue Inserts). Delete/Update funktionieren (SQLite aktiv).
- Neue, risikoarme Produktiv‑Werkzeuge: GUI‑Backup, Integritätsreport, kuratierte Kandidaten‑Pipeline.
- **Enhanced API** implementiert: Pagination, Bulk, Stats, Export.

## 2. Architekturüberblick (Ist‑Stand)
- **Inbound (Flask)**: REST API (Option: Flask‑SocketIO). CORS in Dev permissiv; Prod‑Whitelist möglich.
- **Application‑Layer**: `FactManagementService`, `ReasoningService` — Formatvalidierung, idempotente Adds, Reasoning‑Konfidenz.
- **Outbound (Adapter)**:
  - `SQLiteFactRepository` (Primär): `facts(statement TEXT PRIMARY KEY, context TEXT, fact_metadata TEXT)`
  - `JsonlFactRepository` (Fallback/Export): Append‑only, kein Delete/Update.
  - Monitoring/Sentry (optional), Governor (optional), WebSocket‑Adapter (optional).

## 3. Wesentliche Änderungen dieser Migration
- Backend: Nur Port 5001; Legacy‑Proxy 5000 entfernt (`/api/llm/get-explanation` nutzt interne Provider oder 503‑Fehler).
- Repository: Reihenfolge invertiert (SQLite→JSONL Fallback) in `src_hexagonal/hexagonal_api_enhanced.py`.
- Import: **JSONL → SQLite** via `scripts/import_jsonl_to_sqlite.py` (Ergebnis: Added 3776, Bad 0).
- **Enhanced API** (neu):
  - `GET /api/facts/paginated?page=1&per_page=50` — Pagination.
  - `POST /api/facts/bulk` — Bulk‑Insert transaktional.
  - `GET /api/facts/stats` — total + Top‑Prädikate (Sample).
  - `GET /api/facts/export?limit=100&format=json|jsonl` — Export.
- Engines (Aethelred): Durchsatz erhöht, ENV‑Schalter hinzugefügt; optionaler Reasoning‑Gating.
- Tools:
  - `scripts/Backup-HAK_GAL_HEXAGONAL.ps1` (GUI, Full/Incremental, Manifest, Scheduling)
  - `scripts/generate_integrity_report.py` (Read‑only KB‑Integritätsreport)
  - `scripts/auto_topics_from_kb.py` / `scripts/curated_candidate_pipeline.ps1` (Themen→Kandidaten→Review, read‑only)
  - `scripts/optimize_database.py` (ANALYZE/PRAGMA optimize/VACUUM)
  - `scripts/system_status_check.py` (Status‑Schnellcheck)
- Repo‑Vorbereitung: `.gitignore`, `.gitattributes`, `env.example`, `README.md`; Aufräum‑Archiv `ARCHIVE_20250814_cleanup/`.

## 4. Endpunkte (Kern & Enhanced)
- Core:
  - `GET /health` — Light Health.
  - `GET /api/status` — Vollstatus (inkl. `repository_type`, Governor, WebSocket etc.).
  - `GET /api/facts?limit=N` — Liste (kleinere N).
  - `POST /api/facts` — Insert (Format: `Predicate(A,B).`).
  - `POST /api/search` — Suche.
  - `POST /api/reason` — Reasoning (Konfidenz + Terms).
  - `PUT /api/facts/update` — Update (nur SQLite wirksam).
  - `POST /api/facts/delete` — Delete (nur SQLite wirksam).
  - `GET /api/facts/count` — Zähler (TTL Cache 30s).
- Enhanced (neu):
  - `GET /api/facts/paginated?page=1&per_page=50` — Pagination.
  - `POST /api/facts/bulk` — `{ "statements": ["HasPart(A,B).", ...] }`.
  - `GET /api/facts/stats?sample_limit=5000` — `total`, `top_predicates`.
  - `GET /api/facts/export?limit=100&format=json|jsonl` — Export.

## 5. Betrieb (Runbook)
### Start Backend (Port 5001)
```powershell
cd HAK_GAL_HEXAGONAL
.\.venv_hexa\Scripts\activate
python src_hexagonal\hexagonal_api_enhanced.py
# oder
.\start_native.bat
```
### Governor
- Im Frontend „Start Governor“ klicken; Status via `GET /api/governor/status`.

### Smoke‑Tests (CRUD)
```powershell
$BASE="http://127.0.0.1:5001"
# Add
Invoke-RestMethod -Method Post -Uri "$BASE/api/facts" -ContentType 'application/json' -Body (@{statement='HasPart(A,B).'}|ConvertTo-Json)
# Update
Invoke-RestMethod -Method Put  -Uri "$BASE/api/facts/update" -ContentType 'application/json' -Body (@{old_statement='HasPart(A,B).';new_statement='HasPart(A,C).'}|ConvertTo-Json)
# Delete
Invoke-RestMethod -Method Post -Uri "$BASE/api/facts/delete" -ContentType 'application/json' -Body (@{statement='HasPart(A,C).'}|ConvertTo-Json)
```

### Enhanced API Quick‑Tests
```bash
curl "http://127.0.0.1:5001/api/facts/paginated?page=1&per_page=10"
curl "http://127.0.0.1:5001/api/facts/stats"
curl "http://127.0.0.1:5001/api/facts/export?limit=100"
```

## 6. Datenmodell & Repository
- SQLite‑Schema: `facts(statement TEXT PRIMARY KEY, context TEXT DEFAULT '{}', fact_metadata TEXT DEFAULT '{}')`.
- Delete/Update: nur mit SQLite vorhanden/effektiv.
- JSONL: Append‑only, bleibt Exportformat; Importer für One‑way‑Migration.

## 7. Engines (Aethelred) — Tuning & Sicherheit
- Durchsatz (ENV):
  - `AETHELRED_PARALLEL=8`
  - `AETHELRED_FACTS_PER_TOPIC=50`
  - `AETHELRED_ADD_DELAY_MS=20`
  - `AETHELRED_ADD_WORKERS=8`
- Optionales Qualitätstor:
  - `AETHELRED_STRICT_CONFIDENCE=0.80` — Insert nur bei Konfidenz ≥ 0.8 (via `/api/reason`).
- Metadatenfakten: `AETHELRED_INCLUDE_META=1` (deaktivierbar).

## 8. Sicherheit & Policies
- Kill‑Switch: SAFE blockt Writes (503). Deaktivierbar über Safety‑Endpoints.
- PolicyGuard: Observe‑Mode setzt Policy‑Header im Add‑Response; kann gehärtet werden.
- CORS: Dev permissiv; Prod Whitelist empfehlenswert.
- OpenAPI: Nur in Dev anzeigen (optional Flag).
- Control‑Routen (Governor/Safety): Optionaler Header‑Token empfehlenswert (ENV‑Gate).

## 9. Monitoring & Qualität
- Integritätsreport (read‑only): `scripts/generate_integrity_report.py` → `PROJECT_HUB/reports/knowledge_integrity_<ts>.md`.
- System‑Schnellcheck: `scripts/system_status_check.py`.
- Nightly Trends: `PROJECT_HUB/reports/nightly_trend_YYYYMMDD.md` (erweiterbar).
- Kandidaten‑Pipeline (read‑only bis Review):
  - `scripts/auto_topics_from_kb.py` → `PROJECT_HUB/topics.txt`.
  - `scripts/curated_candidate_pipeline.ps1` → `PROJECT_HUB/reports/candidates_<ts>.md`.

## 10. Backup & Wiederherstellung
- GUI‑Backup: `scripts/Backup-HAK_GAL_HEXAGONAL.ps1` (Full/Incremental, Manifest, Scheduler). Unterstützt Locked‑File‑Handling (SQLite‑Backup via Python `con.backup`).
- Export: `GET /api/facts/export` (JSON/JSONL) — schnelle Datenportabilität.

## 11. Risiken & Gegenmaßnahmen
- Falsches Repo aktiv: `/api/status` regelmäßig prüfen (`repository_type=SQLiteFactRepository`).
- Silent No‑Ops (JSONL): JSONL nicht mehr als Backend einsetzen; bei fehlenden Methoden 501 (optional ergänzbar).
- LLM nicht konfiguriert: `/api/llm/get-explanation` liefert 503 mit klarer Meldung; FE zeigt Nutzerhinweis.

## 12. Roadmap (Q3/Q4 2025)
- Frontend‑Pagination/Virtualization (react‑window vorhanden) + Stats‑Widgets.
- Graph‑Visualisierung (D3.js; Templates liegen bereit) & Subgraph‑Export.
- Local LLM Support (Ollama) als optionaler Provider.
- Advanced Governor (Multi‑Engine Orchestrierung, Policies verfeinern).
- Docker‑Deployment (Compose), CI (Actions), OpenAPI/Swagger‑Doku.

## 13. To‑Do (Kurzfristige Quick Wins)
- `scripts/optimize_database.py` regelmäßig ausführen (Wartung).
- Frontend auf `/api/facts/paginated` umstellen.
- Optional: Token‑Gate für Safety/Governor in Prod.

## 14. Anhang — Implementierungsorte
- Enhanced API: `src_hexagonal/hexagonal_api_enhanced.py` (neue Routen)
- SQLite‑Repo‑Erweiterungen: `src_hexagonal/adapters/sqlite_adapter.py`
- Backup GUI: `scripts/Backup-HAK_GAL_HEXAGONAL.ps1`
- Reports/Tools: `scripts/generate_integrity_report.py`, `scripts/system_status_check.py`
- Kandidaten‑Pipeline: `scripts/auto_topics_from_kb.py`, `scripts/curated_candidate_pipeline.ps1`
- Migration: `scripts/import_jsonl_to_sqlite.py`, `PROJECT_HUB/SQLITE_MIGRATION_PLAN_GPT5_20250814.md`

— Ende —
