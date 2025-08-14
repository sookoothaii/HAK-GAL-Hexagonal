# HAK/GAL Hexagonal Suite – Technical Handover (Engineering Report)

This document is a thorough handover covering the Hexagonal Architecture backend (port 5001), the full MCP tool integration journey, operational guidance, and frontend modernization decisions. It records both strengths and pain points encountered, with reproducible steps and actionable next actions. It adheres to the HAK/GAL Constitution: strictly empirical, verifiable, honest errors over guesses, and transparent reasoning.

---

## 1. Executive Summary

- Architecture: Clean Hexagonal (Ports & Adapters), backend on port 5001 only.
- Knowledge Base: JSONL file (one fact per line) with predicate-style statements, audited writes, file lock for atomicity.
- MCP: 30 tools (search/analysis/CRUD/backup/hub). Stability fixes applied to initialization, tools discovery, and write gating.
- Frontend: React/TS, shadcn/ui; simplified to hex-only, added scientific KB Quality and Top Predicates widgets; more upgrades planned.
- Operations: Robust logs, explicit ENV gates, safe defaults, Project-Hub snapshots, and digest for session startup.

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
- Data: `data/k_assistant.kb.jsonl` – the canonical KB file

---

## 4. Backend: REST API (Flask) and WebSocket (Socket.IO)

Entry point: `src_hexagonal/hexagonal_api_enhanced.py`

### 4.1 REST Endpoints (selected)

- Health and status
  - `GET /health` – minimal health (status, architecture, port, repository)
  - `GET /api/status[?light=1]` – enhanced status; light mode avoids heavy work
- Knowledge Base
  - `GET /api/facts?limit=N` – list facts
  - `POST /api/facts` – add fact (strict validation, dot-terminated predicate format)
  - `GET /api/facts/count` – count with TTL cache
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

Framework: React 18 + TypeScript, Zustand, shadcn/ui (Radix), Recharts, Socket.IO.

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

### 8.2 Startup & Health

- Backend: `python src_hexagonal/hexagonal_api_enhanced.py`
- Health check: `GET /health` → expect `{ status: 'operational', architecture: 'hexagonal', port: 5001 }`
- Status: `GET /api/status?light=1` for quick checks; without `light` for extended info
- WebSocket: client connects to `ws://localhost:5001` (Socket.IO)

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

- Predicate translator (`bulk_translate_predicates`) remains disabled to avoid sweeping changes without a full dry-run pipeline and rollback strategy.
- Reasoning explain proxy still attempts 5000 first if present; migrate to hex-native LLM providers entirely when stable.
- Better parser/grammar for statements (nested/advanced forms) would reduce invalid rates and increase analysis depth.
- Formal contradiction checking is heuristic; extend to temporal and multi-argument logic.
- Frontend lacks full Analytics and Snapshots pages; planned.

---

## 12. Test & Validation Strategy

- Unit tests: domain/application services (ports mocked), adapters stubbed.
- Integration tests: REST endpoints, MCP tool calls (non-destructive first, destructive under gated suite).
- E2E: Frontend flows (query → suggested facts → add → audit), snapshot workflows, governor toggles.
- Benchmarks: Reasoning latency targets (<10 ms HRM), search throughput, KB append/replace under lock contention.

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
- Hex-only configuration; removed backend switch and 5000 fallbacks.
- Query page uses only 5001 endpoints and shows suggested facts clearly with add flow.
- Dashboard shows KB Quality (new REST metrics) and Top Predicates widgets.
- Socket hook unified to backend config.

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
- [ ] MCP fixed server configured in client and started (initialize OK)
- [ ] ENV set: `HAKGAL_WRITE_ENABLED`, `HAKGAL_HUB_PATH`, optional `HAKGAL_WRITE_TOKEN`

Pre-change Safety
- [ ] Create snapshot (`project_snapshot`) or backup (`backup_kb`) before bulk operations
- [ ] Kill-switch state reviewed (`/api/safety/kill-switch`)

Write Operations
- [ ] Confirm gating and audit requirement
- [ ] Monitor `mcp_write_audit.log` during the change

Post-change Validation
- [ ] Run `validate_facts`, `analyze_duplicates`, `consistency_check`
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

The Hexagonal Suite on port 5001 provides a clean, reproducible, and observable platform for knowledge-centric work with strict safety properties. The MCP integration is stable and comprehensive after addressing protocol and schema pitfalls. The frontend has begun converging on an evidence-first, scientific presentation and will further benefit from analytics, snapshots UX, and a robust data-fetching layer. All critical write operations remain gated, audited, and reversible via backups/snapshots.

> Principle: Prefer honest errors, deterministic behavior, and reproducible context over convenience. Every change should be explainable via logs, audits, or snapshots.

