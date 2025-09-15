---
title: "Security Maturity Plan Stage5"
created: "2025-09-15T00:08:01.088012Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Security Maturity – Plan zu Stufe 5 (Production‑Grade)

Stand jetzt: Stufe 2/5 („gehärtete Dev/Pre‑Prod Basis“)
- Ein‑Origin‑Proxy (8088), zentrale HTTP/WS‑Clients, API‑Key erzwungen
- 5002 (WRITE) als Standard‑API, 5001 als Admin/Fallback
- Messbar: p95 < 10 ms, WS stabil, Schreibtest erfolgreich

Ziel (Stufe 5):
- HTTPS/TLS überall (inkl. WS), HSTS
- AuthN/AuthZ (JWT/RBAC/Scopes), Secret‑Management & Rotation
- Input/Schema‑Hardening, Rate‑Limiting, WAF, Least‑Privilege
- CI/CD‑Security (SAST/DAST, SBOM, Pinning, Signaturen)
- Observability & Audit (strukturierte Logs, Alerts, tamper‑evident Audits)
- Backup/Restore automatisiert verifiziert, DR/HA‑Runbooks

---

## Iterativer Plan (Sprints à 1 Woche)

### Sprint 1 – Transport & Boundary Security
- Aufgaben
  - TLS in Caddy aktivieren (lokal mkcert, prod ACME), HTTP→HTTPS Redirect, HSTS
  - Socket.IO über WSS, Frontend ENV auf https umstellen
  - Proxy‑Header hardenen (X‑Forwarded‑Proto, Security Headers)
- Deliverables
  - `Caddyfile` (tls, hsts, redirects), `START_GUIDE_LOCAL_DEV_8088.md` Update
- Akzeptanzkriterien
  - `https://127.0.0.1:8088` liefert gültiges Zertifikat, HSTS aktiv
  - Alle WS/HTTP Aufrufe über TLS (Dev: Selbstsigniert), keine Mixed‑Content‑Warnungen

### Sprint 2 – AuthN/AuthZ & API‑Boundary
- Aufgaben
  - JWT‑Validierung (RS256), Rollen/RBAC (reader, writer, admin), Scopes
  - `/api` nur für legitime Scopes; `/api-admin` nur admin; 5001 optional „localhost only“ im Proxy
  - API‑Key nur als Service‑Key (Scope‑limitiert) mit Rotation
- Deliverables
  - Middleware in `hexagonal_api_enhanced.py` (JWT/Scopes), Proxy‑Regeln für `/api-admin`
  - Frontend: Token‑Flow (nur Dev), axios‑Interceptors für 401/403
- Akzeptanzkriterien
  - Unautorisierte Zugriffe werden 401/403 geblockt; Logs ohne Secrets

### Sprint 3 – Secrets & Konfiguration
- Aufgaben
  - Secrets aus Repo entfernen; Windows Credential Manager/KeyVault (prod) für Keys
  - Rotations‑Prozess (API‑Key/JWT‑Keys), `.env` Policy/Template
  - Config‑Sanitizing: keine Secrets in Logs/Fehlermeldungen
- Deliverables
  - `SECURITY_SECRETS_POLICY.md`, Rotations‑Script, masked logging
- Akzeptanzkriterien
  - Erfolgreiche Rotation ohne Downtime; keine Secrets in Repos/Logs

### Sprint 4 – Input Hardening & Throttling
- Aufgaben
  - JSON‑Schema‑Validierung/Type‑Checks (Server), Payload‑Limits (Caddy/Flask)
  - Rate‑Limiting pro IP/Route (Caddy), Basic‑WAF (Rule‑Set), CORS strikt
  - Fehlerantworten sanitizen (keine Stacktraces/Interna)
- Deliverables
  - Validierungsmodule, Caddy‑Rate‑Limits/WAF‑Regeln, CORS‑Policy
- Akzeptanzkriterien
  - Bösartige/zu große Anfragen werden gedrosselt/geblockt; saubere Fehlerseiten

### Sprint 5 – Observability & Audit
- Aufgaben
  - Strukturierte JSON‑Logs, Correlation‑IDs, zentraler Logger
  - Audit‑Logs (append‑only) für Writes, Windows ACLs/hardening
  - Alerts (HTTP 4xx/5xx Raten, WS Drop, Spike), Dashboards (Latenz/RPS)
- Deliverables
  - `OBSERVABILITY_SETUP.md`, Audit‑Log‑Pfad/Policy, Alert‑Rules
- Akzeptanzkriterien
  - Vorfälle lösen Alerts aus, Audits sind nachvollziehbar und unveränderbar

### Sprint 6 – CI/CD‑Security
- Aufgaben
  - SAST (Bandit/ESLint‑security), DAST (OWASP ZAP), SBOM (CycloneDX), Dependency‑Pinning (lockfiles)
  - Signierte Artefakte, pre‑commit Hooks (Lint/Test/SAST)
- Deliverables
  - CI‑Pipelines (GitHub/GitLab), `SECURITY_PIPELINE.md`
- Akzeptanzkriterien
  - Builds schlagen fehl bei kritischen Findings; SBOM verfügbar; Artefakte signiert

### Sprint 7 – Data Safety & DR/HA
- Aufgaben
  - Automatisierte Backups & Restore‑Tests (Task Scheduler), WAL/PRAGMA‑Tuning
  - DR‑Runbook, HA‑Plan (Replikation/Failover Roadmap)
- Deliverables
  - Backupscripte, `DR_RUNBOOK.md`, Wiederherstellungstest‑Report
- Akzeptanzkriterien
  - Restore‑Test bestanden; Recovery‑Zeit im Rahmen; WAL/PRAGMA dokumentiert

---

## Frontend‑Spezifisch (laufend in Sprints integrieren)
- Proxy‑First: nur relative Pfade (`/api`, `/socket.io`), kein Host/Port‑Switch
- UI‑Fallbacks: Bei 405/404 „n/a“ rendern statt Fehler (Monitoring/Stats)
- Dev‑Toggle (nur Dev): optional `/api-admin` (5001) für Diagnose
- Token‑Handling: axios‑Interceptors, 401/403 UX, keine Token in Logs

---

## Governance & Prozesse
- Change‑Control: Staging→Prod Gates, Rollback‑Plan, Migrations‑Checklisten
- Secrets: Rotationskalender, Zugriff nur für Rollen, 4‑Augen‑Prinzip
- Incident‑Response: Runbooks, Kontakte, Eskalation, Post‑Mortems

---

## Quick Wins (48h)
- TLS/HSTS im Proxy aktivieren; HTTP→HTTPS redirect
- `/api-admin` im Proxy auf `localhost` beschränken (Dev) oder JWT „admin only“
- UI‑Fallbacks für 405 (Monitoring/Stats) einbauen

---

## Referenzen
- Start/Orchestrierung: `scripts/restart_all_ps7_orchestratedONLY.ps1`, `scripts/start_all_ps7_windows.ps1`
- Proxy/TLS: `Caddyfile`, `scripts/start_caddy.ps1`
- Frontend Clients: `frontend/src/services/api.ts`, `frontend/src/hooks/useGovernorSocket.ts`
- Guides/Handover: `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md`, `PROJECT_HUB/START_SEQUENCE_PS7.md`, `PROJECT_HUB/TECHNICAL_HANDOVER_20250817_GPT5.md`

