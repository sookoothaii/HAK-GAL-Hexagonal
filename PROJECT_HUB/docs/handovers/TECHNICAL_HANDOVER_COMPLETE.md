# HAK/GAL Hexagonal Suite – Technical Handover (Engineering Report)

This document is a thorough handover covering the Hexagonal Architecture backend (port 5001), the full MCP tool integration journey, operational guidance, and frontend modernization decisions. It records both strengths and pain points encountered, with reproducible steps and actionable next actions. It adheres to the HAK/GAL Constitution: strictly empirical, verifiable, honest errors over guesses, and transparent reasoning.

---

## 1. Executive Summary

- Architecture: Clean Hexagonal (Ports & Adapters), dual backends: 5001 (write) & 5002 (read-only, Mojo, Kill‑Switch).
- Knowledge Base: SQLite DB (SoT) with audited writes; JSONL file remains as fallback/export. File locks and gating enforced.
- Mojo: Native pybind11 module loaded (backend=mojo_kernels); Golden-Tests zuvor 0 Mismatches (Python vs. Mojo); Bench (1000): validate ~0–2.3 ms, duplicates ~117–191 ms @0.95.
- MCP: 30 tools (search/analysis/CRUD/backup/hub). Stability fixes applied to initialization, tools discovery, and write gating.
- Frontend: React/TS, shadcn/ui; hex-backend with scientific KB Quality & Top Predicates widgets; Backend-Switch 5001↔5002 vorhanden.
- Operations: Robust logs, explicit ENV gates, safe defaults, Project-Hub snapshots, and digest for session startup.

Delta v2.3:
- Neuer Endpoint `GET /api/analysis/similarity-top` (read‑only, Mojo beschleunigt)
- Health meldet Port dynamisch via `HAKGAL_PORT` und Mojo‑Status
- Mojo Adapter lädt `.pyd` robust aus zusätzlichen Build‑Pfaden; `MOJO_BACKEND_MODULE` unterstützt
- CMake: Ziel `hakgal_mojo_kernels` mit `OUTPUT_NAME mojo_kernels`; `find_package(Python3 ... Development.Module ...)`

---

## 2. System Overview (Hexagonal Architecture)

- Pattern: Ports & Adapters with a strict dependency rule inward to the Domain.
- Domain Core (entities, value objects): free of frameworks; focuses on semantics of facts, queries, and reasoning outcomes.
- Application Services: orchestrate use-cases (fact management, reasoning) using ports.
- Adapters: REST (Flask), WebSocket (Socket.IO), Reasoning engines, LLM providers, storage repositories (Legacy/SQLite), Governor strategy.
- Infrastructure: Monitoring (Sentry), engine providers, and operational utilities.

High-level goals:
- Reproducibility: Project-Hub snapshots (KB and Tech) + manifest/diff.
- Observability: Health endpoints, audits, quality metrics.
- Safety: Write operations behind ENV/Token, file locks, and a kill-switch.

---

## 3. Repository Map and Key Modules

- Backend core: `src_hexagonal/`
  - `core/` – Domain (entities, value objects, ports)
  - `application/` – Services and policies (e.g., FactManagementService, ReasoningService)
  - `adapters/` – REST/WebSocket, governor, LLM, repositories (Legacy/SQLite), fact extractor
  - `infrastructure/` – monitoring, engines, persistence glue
  - API entry: `src_hexagonal/hexagonal_api_enhanced.py`
- MCP server: `hak_gal_mcp_fixed.py` (STDIO, JSON-RPC) with 30 tools
- Project-Hub: `PROJECT_HUB/` for snapshots, manifests, and handover docs
- Data: SQLite `k_assistant.db` (Source of Truth) + JSONL `data/k_assistant.kb.jsonl` as Fallback/Export
- Native: `native/mojo_kernels/` (pybind11/CMake, module output `mojo_kernels`)

---

## 4. Backend: REST API (Flask) and WebSocket (Socket.IO)

Entry point: `src_hexagonal/hexagonal_api_enhanced.py`

### 4.1 REST Endpoints (selected) – 5001 (write) und 5002 (read‑only, Mojo)

- Health and status
  - `GET /health` – minimal health (status, architecture, port, repository, Mojo‑Flags)
  - `GET /api/status[?light=1]` – enhanced status; light mode vermeidet heavy work
- Knowledge Base
  - `GET /api/facts?limit=N` – list facts
  - `POST /api/facts` – add fact (strict validation, dot‑terminated predicate format) [5001]
  - `GET /api/facts/count` – count mit TTL cache
  - `POST /api/search` – semantic/textual search (query, limit, confidence)
- Reasoning
  - `POST /api/reason` – neural reasoning (timed, emits WS events, Sentry metrics if enabled)
  - `POST /api/llm/get-explanation` – explanation proxy with original backend fallback and hex-native provider fallback; fact suggestions extracted
  - `POST /api/command` – compatibility endpoint (explain/add_fact) to bridge legacy frontend contracts
  - `POST /api/logicalize` – extract predicate-style statements from free text
- Safety & Policy
  - `GET /api/safety/kill-switch` – kill-switch state
  - `POST /api/safety/kill-switch/activate|deactivate` – control safe mode
- Architecture metadata
  - `GET /api/architecture` – describes layers and features
- New metrics for the frontend (added)
  - `GET /api/predicates/top?limit=10&sample_limit=5000` – top-N predicates by frequency
  - `GET /api/quality/metrics?sample_limit=5000` – sample-based KB quality metrics: invalid, duplicates, contradictions, isolated, predicate counts
  - `GET /api/analysis/similarity-top?sample_limit=2000&threshold=0.95&top_k=50` – Top‑K semantische Paare (Mojo beschleunigt, read‑only)

- Mojo Admin (5002)
  - `GET /api/mojo/status` – Flags, Backendname, Availability
  - `GET /api/mojo/golden` – Golden‑Test Parität Mojo vs. Python
  - `GET /api/mojo/bench?limit=1000&threshold=0.95` – Benchmarks der Kernfunktionen
  - Geplant (read‑only)
    - `GET /api/analysis/dupes-ppjoin?sample_limit=2000&threshold=0.9&top_k=100` – PPJoin(+)-basierte Duplikat‑Paare inkl. Filter‑Stats

Notes:
- CORS permissive (local dev) and automatic OPTIONS handling.
- TTL caching used for selected endpoints to reduce repeated I/O.

### 4.2 WebSocket Events

- `connection_status`, `kb_update`, `kb_metrics`, `governor_update`, `reasoning_complete`, etc.
- Backpressure: keep events minimal and composable; the frontend can compute deltas.

### 4.3 Governor & Engines

- Governor adapter instantiated but not auto-started; controlled via frontend actions.
- Engines (Aethelred, Thesis) integrated through ports; used for fact generation and pattern/meta-analysis.
- HRM (Human Reasoning Model): ~600k parameters, provides fast, interpretable heuristics for sequencing/checks; no side-effects by itself.

### 4.4 Safety & Policy Guard

- Kill-switch: disables writes system-wide in SAFE mode (503 on write paths).
- PolicyGuard: blocks sensitive operations that violate configured constraints; metadata returned via headers (X-Policy-Version, X-Decision-Id).

---

## 5. Data Model and KB Format

- KB file: `data/k_assistant.kb.jsonl` (UTF-8)
- Each line: JSON object with at least `statement` (string). Optional fields: `source`, `tags`, etc.
- Statement format: `Predicate(Entity1, Entity2).` – enforced on write endpoints; validated by MCP tools and REST.
- Auditing: `mcp_write_audit.log` stores JSON entries for all write operations (action, payload, timestamp).
- Locking: `*.lock` file ensures atomic writes (append, replace, bulk operations) with timeouts and cleanup.

---

## 6. MCP Integration (Full Tooling and Stability Journey)

MCP server: `hak_gal_mcp_fixed.py` (STDIO JSON-RPC). Primary responsibilities:
- Advertise tool capabilities during `initialize`.
- Provide a consistent `tools/list` with proper JSON Schema for arguments.
- Handle `tools/call` with robust validation, write gating, and informative errors.
- Respond to optional `resources/list` and `prompts/list` with empty lists (to avoid client errors).

### 6.1 Tool Catalogue (30 tools)

Categories and selected examples (complete list is implemented in the server):

- Information
  - `search_knowledge`, `get_system_status`, `health_check`, `kb_stats`
- Fact management (write-gated)
  - `add_fact`, `delete_fact`, `update_fact`, `bulk_delete`
- Analysis
  - `semantic_similarity`, `consistency_check`, `validate_facts`, `analyze_duplicates`, `find_isolated_facts`, `inference_chain`
- Query & Graph
  - `search_by_predicate`, `query_related`, `get_knowledge_graph`
- Statistics
  - `get_entities_stats`, `get_predicates_stats`, `growth_stats`
- Audit & Export
  - `list_audit`, `get_fact_history`, `export_facts`
- Backup & Maintenance (write-gated)
  - `backup_kb`, `restore_kb`, `bulk_translate_predicates` (currently disabled by design)
- Project-Hub
  - `project_snapshot`, `project_list_snapshots`, `project_hub_digest`

Notes:
- `bulk_translate_predicates` currently returns a disabled notice to avoid risky large-scale changes until fully validated.
- Project-Hub tools support snapshot creation (SNAPSHOT_TECH.md, SNAPSHOT_KB.md, snapshot_kb.json, manifest.json + diffs) and listing/digest of recent snapshots.

### 6.2 Write Gating & Token Handling

- ENV flags (read at server init):
  - `HAKGAL_WRITE_ENABLED=true` – enables any write operations
  - `HAKGAL_WRITE_TOKEN=<token>` – optional extra guard
- `_is_write_allowed(provided_token)` rules (current behavior):
  - If `HAKGAL_WRITE_ENABLED` is false → deny.
  - If `HAKGAL_WRITE_TOKEN` is set:
    - Accept matching explicit token, OR
    - Accept empty `auth_token` (implicit local convenience for the configured desktop environment).
  - If no token configured → allow when enabled.
- All write calls audit to `mcp_write_audit.log` with timestamps and payloads.

### 6.3 Initialization and Discovery Fixes (Odyssey)

Observed issues and resolutions during MCP client integration:

- Problem: Server disconnected after `initialize`.
  - Root causes:
    - Missing `protocolVersion` in `initialize` result.
    - `capabilities.tools` advertised incorrectly (empty object vs. boolean vs. object with `listChanged`).
    - Missing handlers for `resources/list` and `prompts/list` leading to client errors.
  - Fixes:
    - Added `protocolVersion: "2025-06-18"` in `initialize`.
    - Stabilized capabilities to `{ tools: { listChanged: true }, resources: {}, prompts: {} }` (or simple booleans where required by client version).
    - Implemented empty responses for `resources/list` and `prompts/list`.

- Problem: Tools not visible in client UI despite “running”.
  - Root causes:
    - Misaligned `capabilities` schema; client ignored tool listing.
    - Inconsistent tool schemas (e.g., boolean default values as `true` vs. Python `True`).
  - Fixes:
    - Unified tool schemas; corrected Python booleans.
    - Ensured `tools/list` returns a complete array with `inputSchema` per tool.

- Problem: NameError `true is not defined` caused server crash.
  - Root cause: Using JavaScript-style `true` instead of Python `True` in a tool schema.
  - Fix: Replaced with `True` and reviewed all schemas for Python correctness.

- Problem: Frequent transport closures.
  - Root causes: combination of the above and client retries.
  - Fix: After applying all protocol/schema fixes, stability returned; logs confirm steady `tools/list` and `tools/call` cycles.

### 6.4 Project-Hub Integration via MCP

- `project_snapshot` creates a timestamped folder `snapshot_YYYYMMDD_HHMMSS` with:
  - `SNAPSHOT_TECH.md`: trees (selected dirs), manifest and diffs (added/removed/changed files)
  - `SNAPSHOT_KB.md`: KB health, counts, predicates, latest audit entries
  - `snapshot_kb.json`: structured metrics
  - `manifest.json`: hashes and metadata for reproducible diffs
- `project_list_snapshots`: lists only folders starting with `snapshot_`, sorted by modification time.
- `project_hub_digest`: composes recent snapshot files (SNAPSHOT.md/TECH/KB/json) into a compact context string (char-capped).

---

## 7. Frontend Modernization

Framework: React 18 + TypeScript, Zustand, Tailwind + shadcn/ui (Radix), Recharts, Socket.IO.

### 7.1 Changes Implemented

- Hex-only backend configuration:
  - Removed original (5000) backend and switching UI; fixed to 5001.
  - Unified API base/WS URL reading from a single config module.
- Unified Query page:
  - Removed legacy fallbacks; uses only `POST /api/reason`, `POST /api/search`, `POST /api/llm/get-explanation` (5001).
  - Suggested facts are normalized and presented with “Add Fact” (human-in-the-loop) and consistent trust scoring.
- Dashboard:
  - Replaced gamified “Achievements” with scientific KB Quality widget (invalid, duplicates, contradictions, isolated). Data from new REST metrics.
  - Added “Top Predicates” widget (compact, non-overloaded; monospaced labels; accessible contrast).
- Socket hook:
  - Reads WS URL from backend config; cleans up delay logic and logs.

### 7.2 Recommended Next Steps

- Data fetching & caching
  - TanStack Query for SWR, cache per endpoint, retry/backoff, offline support.
  - Central API error boundary with toast + durable fallback to last-known-good.
- Analytics page
  - Trend charts for KB quality metrics (time series), audit density over time, predicate distribution.
  - Drilldowns from each metric to a filtered list of facts.
- Snapshots page
  - List view with sort by mtime; details with tabs (SNAPSHOT_TECH.md, SNAPSHOT_KB.md, manifest.json diff viewer).
  - Copy/download controls.
- Accessibility and performance
  - Ensure WCAG contrast in dark mode; keyboard navigation; ARIA roles.
  - Lazy-load heavy charts; granular Zustand selectors.
- Testing
  - Vitest/RTL unit tests for pages/stores; Cypress E2E for query→fact add→audit flow.

---

## 8. Operations & Runbooks

### 8.1 Environment Variables

- `HAKGAL_WRITE_ENABLED` (true|false): enable writes for MCP and relevant REST operations
- `HAKGAL_WRITE_TOKEN`: optional token gating for writes; implicit acceptance when empty token is provided locally
- `HAKGAL_HUB_PATH`: Project-Hub path for snapshots/digest
- `PYTHONIOENCODING=utf-8`: ensure clean UTF-8 for STDIO and logs
- `HAKGAL_PORT`: Laufzeitport (z. B. 5001 oder 5002; Health nutzt diesen Wert)
- `MOJO_ENABLED` (true|false): globaler Schalter für Mojo Nutzung
- `MOJO_VALIDATE_ENABLED` (true|false): Mojo Validator aktiv
- `MOJO_DUPES_ENABLED` (true|false): Mojo Duplicate/Semantik aktiv
- `MOJO_BACKEND_MODULE` (optional): alternativer Modulname/Pfad für das native Backend (Default `mojo_kernels`)
 - `MOJO_PPJOIN_ENABLED` (true|false): aktiviert PPJoin(+)-Pfad für Duplicate/Similarity (read-only, 5002)

### 8.2 Startup & Health

- Backend 5001 (write): `python src_hexagonal/hexagonal_api_enhanced.py` (Standard)
- Backend 5002 (read‑only, Mojo): `scripts/launch_5002_mojo.py` oder `scripts/extensions/restart_5002.ps1 -Mojo -Validate -Dupes -Port 5002`
- Health check: `GET /health` → `{ status: 'operational', architecture: 'hexagonal', port: <env HAKGAL_PORT>, mojo: {...} }`
- Status: `GET /api/status?light=1` für schnelle Checks; ohne `light` für Extended Info
- WebSocket: Frontend kann 5001 oder 5002 nutzen; Standard `ws://localhost:5001` (Socket.IO)

### 8.3 MCP Server (hak-gal)

- Launch via Claude Desktop MCP config; command: Python with the `hak_gal_mcp_fixed.py` script; ensure ENV set.
- Expected initialize result: `protocolVersion: "2025-06-18"`, `capabilities: { tools: { listChanged: true }, resources: {}, prompts: {} }`
- Tools discovery: `tools/list` returns ~30 entries with `inputSchema`.
- Typical write gating response when disabled: `Write disabled. Set HAKGAL_WRITE_ENABLED=true ...`

### 8.4 Logs

- MCP server logs: `mcp_server.log` (file) and STDERR console
- Client logs: `~\AppData\Roaming\Claude\logs\mcp.log` and `mcp-server-hak-gal.log`
- Write audit: `mcp_write_audit.log` (JSONL, one entry per line)

### 8.5 Snapshots

- Manual snapshot via MCP tool `project_snapshot` (optionally with `title`, `description`)
- Output folder: `PROJECT_HUB/snapshot_YYYYMMDD_HHMMSS`
- Use `project_list_snapshots` to confirm and navigate; `project_hub_digest` for quick context on recent snapshots

---

## 9. KB Quality: Definitions & Interpretation

- Invalid: statements that do not match `Predicate(Entity1, Entity2).` format
- Duplicates: repeated exact statements across the sample
- Contradictions: pairs like `NotX(A,B)` or `NichtX(A,B)` coexisting with `X(A,B)` in the sample
- Isolated: facts whose both entities appear only once in the sample
- Top Predicates: frequency-based top-N listing

Interpretation:
- Target zero invalid; duplicates should trend down with consolidation; contradictions should be investigated; isolated facts might indicate outliers needing linkage.

---

## 10. Security Model

- Write gating via ENV + optional token; implicit local convenience is allowed but audited.
- File locking for all writes; atomic temp file replacement for update operations.
- Policy guard and kill-switch to protect during investigations or degraded states.
- CORS relaxed in dev; tighten for production as needed (origin allowlist).

---

## 11. Known Limitations & Backlog

- Predicate translator (`bulk_translate_predicates`) bleibt deaktiviert bis Dry‑Run/Rollback‑Pipeline steht.
- Reasoning Explain Proxy: auf hex‑native Provider migrieren; 5000‑Fallback endgültig entfernen.
- Parser/Grammatik ausbauen (verschachtelte Formen) zur Reduktion invalid/Erhöhung Analyse‑Tiefe.
- Widerspruchsprüfung erweitern (temporal, multi‑argumentativ).
- Frontend: Analytics & Snapshots Seiten fehlen noch; Backend‑Switcher 5001↔5002 stabilisieren.
- Mojo: Ähnlichkeit/Cluster weitere Hotspots evaluieren; SIMD/Threading‑Tuning; Wheel‑Publishing automatisieren.

---

## 12. Test & Validation Strategy

- Unit tests: domain/application services (ports mocked), adapters stubbed.
- Integration tests: REST endpoints, MCP tool calls (non-destructive first, destructive under gated suite).
- E2E: Frontend flows (query → suggested facts → add → audit), snapshot workflows, governor toggles.
- Benchmarks: HRM Latenz <10 ms, Search Throughput, KB Append/Replace unter Lock‑Contention.
- Golden‑Tests (5002): Parität Mojo vs Python (Erwartung 0 Mismatches) für `validate_facts_batch`, identische Duplicate‑Paare für `find_duplicates`.
- Bench (5002, Beispiel 1000/0.95): validate ~0–2.3 ms; duplicates ~117–191 ms.

---

## 13. Incident Log (MCP Odyssey Fixes)

- Initialize failures due to missing `protocolVersion` → fixed.
- Capabilities advertised as `{ tools: {} }` or booleans in wrong contexts → normalized to `{ tools: { listChanged: true }, resources: {}, prompts: {} }`.
- `resources/list` and `prompts/list` not implemented → now return empty arrays.
- Python boolean typo `true` → `True` fixed; audited all schemas.
- `hak_gal_mcp_v2.py` vs `hak_gal_mcp_fixed.py`: config toggled back to fixed for reliability; v2 hardening ongoing but not default.
- Write gating: relaxed implicit local acceptance when ENV token is set, still fully audited; documented clearly.

---

## 14. Frontend – Current State and Next Actions

Implemented:
- Backend‑Switcher 5001↔5002; 5000 entfernt.
- Query Page nutzt 5001; Admin/Analyse‑Panels können 5002 lesen (read‑only Mojo Paths).
- Dashboard: KB Quality & Top Predicates (neue REST‑Metriken).
- Socket Hook vereinheitlicht; Backend Config zentral.

Planned:
- TanStack Query for data fetching.
- Analytics page (quality, predicates, audit density) with drilldowns.
- Snapshots page (list + details tabs with diff viewer).
- Accessibility polish, lazy-loading charts, and granular state selectors.
- Test suites (Vitest/RTL, Cypress).

---

## 15. Operational Checklists

Startup
- [ ] Backend 5001 running (`/health` operational)
- [ ] Backend 5002 running (read‑only, Mojo), Flags geprüft (`/api/mojo/status`)
- [ ] MCP fixed server configured in client and started (initialize OK)
- [ ] ENV set: `HAKGAL_WRITE_ENABLED`, `HAKGAL_HUB_PATH`, optional `HAKGAL_WRITE_TOKEN`, `HAKGAL_PORT`, Mojo‑Flags

Pre-change Safety
- [ ] Create snapshot (`project_snapshot`) or backup (`backup_kb`) before bulk operations
- [ ] Kill-switch state reviewed (`/api/safety/kill-switch`)

Write Operations
- [ ] Confirm gating and audit requirement
- [ ] Monitor `mcp_write_audit.log` during the change

Post-change Validation
- [ ] Run `validate_facts`, `analyze_duplicates`, `consistency_check`
- [ ] Auf 5002: `api/mojo/golden` und `api/mojo/bench` prüfen
- [ ] Update Project-Hub snapshot for handover

---

## 16. Appendices

### 16.1 REST Endpoints Index (selected)

- `GET /health`
- `GET /api/status[?light=1]`
- `GET /api/facts`
- `POST /api/facts`
- `GET /api/facts/count`
- `POST /api/search`
- `POST /api/reason`
- `POST /api/llm/get-explanation`
- `POST /api/command` (explain/add_fact compatibility)
- `POST /api/logicalize`
- `GET /api/predicates/top`
- `GET /api/quality/metrics`
- `GET /api/analysis/similarity-top`
- `GET /api/mojo/status`
- `GET /api/mojo/golden`
- `GET /api/mojo/bench`
- `GET /api/safety/kill-switch`
- `POST /api/safety/kill-switch/activate|deactivate`
- `GET /api/architecture`

### 16.2 MCP Tools (by category)

Information
- `search_knowledge`, `get_system_status`, `health_check`, `kb_stats`

Fact Management (write)
- `add_fact`, `delete_fact`, `update_fact`, `bulk_delete`

Analysis
- `semantic_similarity`, `consistency_check`, `validate_facts`, `analyze_duplicates`, `find_isolated_facts`, `inference_chain`

Query & Graph
- `search_by_predicate`, `query_related`, `get_knowledge_graph`

Statistics
- `get_entities_stats`, `get_predicates_stats`, `growth_stats`

Audit & Export
- `list_audit`, `get_fact_history`, `export_facts`

Backup & Maintenance (write)
- `backup_kb`, `restore_kb`, `bulk_translate_predicates` (disabled)

Project-Hub
- `project_snapshot`, `project_list_snapshots`, `project_hub_digest`

### 16.4 Packaging & Build (Mojo Native Module)

- Projekt: `native/mojo_kernels`
- Tooling: `pybind11`, `CMake`, `scikit-build-core`
- CMake Target: `hakgal_mojo_kernels` mit `OUTPUT_NAME mojo_kernels` (Python Modulname)
- Python Discovery: `find_package(Python3 COMPONENTS Interpreter Development.Module Development.Embed REQUIRED)`
- Build (Windows, venv aktiv):
  - `python -m pip install "pybind11[global]" scikit-build-core ninja`
  - `cmake -S native\mojo_kernels -B native\mojo_kernels\build -DCMAKE_BUILD_TYPE=Release -Dpybind11_DIR="%PYB%"`
  - `cmake --build native\mojo_kernels\build --config Release --target hakgal_mojo_kernels --parallel 8`
- Ausgabe: `mojo_kernels.cp311-win_amd64.pyd` in `native/mojo_kernels/build/(x64/)?Release/`
- Adapter‑Suche: `src_hexagonal/adapters/mojo_kernels_adapter.py` prüft zusätzliche Pfade und respektiert `MOJO_BACKEND_MODULE`

### 16.5 Forschungsleitfaden: Verfahren für kurze Texte (Mojo‑Fokus)

- Korrekturen (Essenz)
  - Jaccard/PPJoin(+): skaliert mit Inverted‑Index und Prefix/Längen‑Filtern weit >10k; Index ≈ O(∑Tokens), Kandidaten sub‑quadratisch.
  - MinHash/LSH: Build ≈ O(N·L·k), Query ≈ O(L·k + |Kandidaten|); Speicher hängt stark von (L,k) ab.
  - „Semantik“: TF‑IDF ist lexikalisch; für Semantik Embeddings (z. B. SBERT) + HNSW. HNSW: Build ≈ O(N log N), Query ≈ sub‑log.
  - Schwellen (≤10k/≥100k) sind Heuristiken, keine harten Grenzen; Zahlen nur mit Quelle.

- Verfahren je Datenregime (präzise)
  - ≤10k–50k: Token‑Jaccard + Inverted‑Index/PPJoin(+)
    - Komplexität: Index ≈ O(∑|tokens|); Kandidatenfilter sub‑quadratisch; exakte Scores
    - Speicher: indexabhängig (Anzahl Tokens, DF‑Verteilung)
    - Einsatz: ideal für 5002‑Hotpaths; deterministisch, Schwellen klar steuerbar
  - 50k–1M: MinHash/LSH (Jaccard‑ähnlich)
    - Komplexität: Build ≈ O(N·L·k); Query ≈ O(L·k + |Kandidaten|)
    - Speicher: Signaturen (L·k) pro Objekt; Parameter steuern Recall/Speed
    - Einsatz: wenn All‑Pairs/PPJoin zu teuer wird; schneller Kandidaten‑Cut
  - ≥100k–10M (Semantikbedarf): Embeddings (z. B. SBERT) + HNSW
    - Komplexität: Build ≈ O(N log N); Query sub‑logarithmisch bis O(N^α)
    - Speicher: hoch (Vektoren + Graph‑Overhead)
    - Einsatz: semantische Ähnlichkeit statt reiner Lexik; sehr skalierbar

- Minimal‑Golden‑Suite (10–15 Fälle)
  - Unicode‑Normalisierung (NFC/NFD), Homoglyphen, Emojis/Sonderzeichen
  - Leer/Null, extrem lange Strings/Tokens, defekte UTF‑8 Sequenzen
  - identische Duplikate, Near‑Duplicates (±1 Token), 0‑Overlap‑Paare
  - Grenzschwelle (score == thr), stabile Sortierung bei Ties

- Bench‑Methodik (knapp)
  - Warmup (5–10 Läufe), P50/P95, fixierter Seed, Input‑Mix (kurz/lang, sparse/dicht)
  - CPU‑Pinning, I/O vermeiden, kalte vs. warme Caches getrennt messen; Pipeline‑Ende messen

- Referenzen (belastbar)
  - PPJoin/PPJoin+: Xiao, Wang, Lin. SIGMOD’08 – https://dl.acm.org/doi/10.1145/1376616.1376725
  - MinHash/LSH: Broder (1997/1998); Indyk & Motwani (1998) – https://dl.acm.org/doi/10.1145/276304.276317
  - HNSW: Malkov & Yashunin (2018) – https://arxiv.org/abs/1603.09320

### 16.3 Sample Payloads

- Add fact (REST):
```json
POST /api/facts
{ "statement": "HasPart(Computer, CPU).", "context": { "source": "human_verified" } }
```

- Search:
```json
POST /api/search
{ "query": "ImmanuelKant", "limit": 10 }
```

- Reason:
```json
POST /api/reason
{ "query": "IsA(Socrates, Philosopher)." }
```

- MCP add_fact:
```json
{
  "method": "tools/call",
  "params": {
    "name": "add_fact",
    "arguments": { "statement": "HasPurpose(Education, Knowledge)." }
  },
  "id": 1,
  "jsonrpc": "2.0"
}
```

---

## 17. Conclusion

Die Hexagonal Suite fährt nun dual: 5001 (write) stabil als SoT‑Backend mit SQLite; 5002 (read‑only) als Mojo‑beschleunigtes Analyse‑Backend mit Golden‑Parität und soliden Bench‑Werten. MCP ist stabilisiert (30 Tools), Frontend zeigt wissenschaftliche Metriken und kann 5002 für Analysen nutzen. Schreibpfade bleiben strikt gated/audited; Operationen sind reproduzierbar via Hub‑Snapshots. Nächste Schritte: Analytics/Snapshots im Frontend, Parser‑Ausbau, Mojo‑Tuning und Wheel‑Packaging automatisieren.

> Prinzip: Ehrliche Fehler, deterministisches Verhalten und reproduzierbarer Kontext vor Convenience. Jede Änderung muss über Logs, Audits oder Snapshots erklärbar sein.




