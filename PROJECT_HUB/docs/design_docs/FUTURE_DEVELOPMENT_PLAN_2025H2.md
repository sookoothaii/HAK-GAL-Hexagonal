---
title: "Future Development Plan 2025H2"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Future Development Plan (2025 H2 → 2026 H1)

Ziel: Von stabiler, gehärteter Dev/Pre‑Prod zu production‑grade, skalierbarer und beobachtbarer Plattform – ohne Brüche mit der bestehenden Hex‑Architektur.

## 0) Ausgangsbasis (Status)
- Standard‑API: 5002 (WRITE) über Proxy `/api`, Admin/Fallback 5001 über `/api-admin`
- WS: `/socket.io` → 5002
- Orchestrierung/Guides vorhanden; p95 < 10 ms über 8088; API‑Key Pflicht

---

## 1) Roadmap – Prioritäten & Zeitplan

### Phase A (0–3 Monate) – Stabilität, Sichtbarkeit, sichere Transporte
1. TLS/HSTS & HTTP/3 (QUIC)
   - Aufgaben: TLS‑Terminierung in Caddy, HSTS, HTTP→HTTPS Redirect, H3 aktivieren
   - Abhängigkeiten: Zertifikate (dev: mkcert, prod: ACME)
   - Akzeptanz: Alle Routen/WS über HTTPS/WSS; keine Mixed‑Content‑Warnungen
   - Risiken: Selbstsigniert in Dev → Browser‑Trust, Dokumentation nötig

2. OpenTelemetry (Tracing/Metrics/Logs)
   - Aufgaben: OTel SDK in 5001/5002/Frontend‑XHR, OTLP Export → lokaler Collector, Standard‑Tags
   - Akzeptanz: End‑to‑End Trace über Proxy→Backend→DB; Dashboards bestehen
   - Risiken: Overhead; Sampling setzen

3. UI‑Fallbacks (405→n/a) & Capability Detection
   - Aufgaben: `MonitoringPanel`, `ProKnowledgeStats`, `ProKnowledgeList` – bei 405/404 „n/a“ rendern
   - Akzeptanz: Keine 405‑Floods; visuelle Degradation statt Fehler

4. SQLite Scaling Lite – WAL, Litestream/LiteFS (Read Replicas)
   - Aufgaben: WAL/PRAGMA Tuning, Litestream Setup (S3/dir), Restore‑Test
   - Akzeptanz: Snapshots & Restore funktionieren; dokumentiert

### Phase B (3–6 Monate) – Auth/RBAC, Policies, Pipeline‑Security
1. AuthN/AuthZ – JWT (RS256) & RBAC/Scopes
   - Aufgaben: Middleware in 5001/5002, Rollen (reader/writer/admin), Scopes; `/api-admin` admin‑only
   - Frontend: Token‑Interceptors, 401/403‑UX
   - Akzeptanz: Unautorisierter Zugriff → 401/403, Logs ohne Secrets

2. Rate‑Limits & Basic‑WAF (Caddy) + CORS strikt
   - Aufgaben: pro Route Limit, einfache Filter, CORS nur Ein‑Origin
   - Akzeptanz: Bösartige/zu große Anfragen werden gedrosselt/geblockt

3. Supply‑Chain Security: SBOM, SAST/DAST, Pinning
   - Aufgaben: SBOM (CycloneDX), Bandit/ESLint‑security, OWASP ZAP (Dev), Dependency‑Pinning
   - Akzeptanz: CI bricht bei kritischen Findings; SBOM exportierbar

### Phase C (6–9 Monate) – Data & Search, Orchestrierung, Secrets
1. Outbox→Search/Vector (Qdrant/Milvus/pgvector)
   - Aufgaben: Outbox Worker für Search/Embeddings; Index Pipeline; Idempotenz
   - Akzeptanz: Suche skaliert unabhängig vom Core; Replay sicher

2. Workflow Orchestrator (Temporal.io)
   - Aufgaben: Reasoning/ETL/Backups als Workflows mit Retry/Timeouts
   - Akzeptanz: Wiederanlaufbar, Sichtbarkeit über Temporal UI

3. Secret‑Management & Rotation
   - Aufgaben: Secrets in CredMgr/KeyVault, Rotations‑Playbook, Masking
   - Akzeptanz: Erfolgreiche Rotation ohne Downtime; keine Secrets im Repo

### Phase D (9–12 Monate) – Advanced Operability & Performance
1. eBPF Observability/Security (gVisor/Falco optional)
   - Aufgaben: Flows/Latenzen ohne Code‑Änderung; Anomalie‑Regeln light
   - Akzeptanz: Basis‑Dashboards; niedriger Overhead

2. Hot‑Paths in Rust/C++ (pyo3/maturin/FFI) & Mojo‑Kerne
   - Aufgaben: Parser/Dedupe/Similarity in Rust/C++; klare ABI/FFI‑Contracts; Mojo‑Pilot
   - Akzeptanz: >2x Speedup in Hot‑Paths; stabile Schnittstellen

3. Realtime‑Upgrade (WebTransport Pilot)
   - Aufgaben: Feature‑Gate; Fallback auf Socket.IO; Metriken/Latenzvergleich
   - Akzeptanz: Kein Regress; optional aktivierbar

---

## 2) Querschnitt: Prozesse & Governance
- Change‑Control: Staging→Prod Gates, Rollback‑Plan
- Incident‑Response: Runbooks, Eskalation, Post‑Mortems
- DR/HA: Backups + Restore‑Tests; DR‑Runbook
- Policy as Code: OPA/Gatekeeper perspektivisch (K8s‑Pfad)

---

## 3) Meilensteine & Akzeptanzkriterien (Auszug)
- MS‑A: HTTPS/H3 aktiv, WS über WSS, OTel Traces sichtbar, UI ohne 405‑Floods
- MS‑B: JWT/RBAC aktiv; Rate‑Limits/WAF; SBOM+SAST/DAST in CI
- MS‑C: Outbox‑Indexer live; Temporal Workflows in Betrieb; Secrets rotiert
- MS‑D: eBPF Dashboards; Hot‑path Speedups; WebTransport‑Pilot grün

---

## 4) Risiken & Mitigation
- Zertifikate in Dev (Trust): Nutzung `mkcert`, klare Guides
- Overhead durch OTel/eBPF: Sampling/Scope kontrollieren
- Orchestrator/Outbox: Idempotenz strikt, Dead‑letter Queues
- FFI‑Grenzen: Stable ABI, Tests, Fallbacks auf Python‑Pfad

---

## 5) Implementierungsleitfaden (praktisch)
- Beginne mit Phase A (TLS/H3, OTel, UI‑Fallbacks, Litestream)
- Nutze vorhandene Skripte/Guides:
  - `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md`
  - `PROJECT_HUB/START_SEQUENCE_PS7.md`
  - `PROJECT_HUB/MASTER_SECURITY_OPERABILITY_PLAN.md`
  - `PROJECT_HUB/SECURITY_MATURITY_PLAN_STAGE5.md`
- PR‑Checklisten: Security‑Review, Logs ohne Secrets, Rollback‑Plan

---

## 6) Erfolgsmessung
- SLOs: p95 < 50 ms (Prod), Fehlerquote < 0.1%, WS‑Uptime > 99.9%
- Security KPIs: 0 kritische SAST/DAST Findings; Secrets‑Leak 0; Audit‑Abdeckung > 95%
- Operability: MTTR < 30 min; Restore‑Test < 15 min

---

Stand: 2025‑08‑17 – Verantwortlich: GPT‑5 (Vorschlag); Umsetzung mit Claude Opus in iterativen Sprints.

