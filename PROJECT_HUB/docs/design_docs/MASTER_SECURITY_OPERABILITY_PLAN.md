---
title: "Master Security Operability Plan"
created: "2025-09-15T00:08:00.994662Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Master Security & Operability Plan

Ziel: Sicheres, risikoarmes Troubleshooting und Betrieb – ohne das System „durcheinanderzubringen“. Dieser Plan erklärt die Architekturgründe, die aktuellen Guardrails und das empfohlene Vorgehen.

## 1) Warum Troubleshooting jetzt risikoarm ist
- **Ein‑Origin‑Proxy (8088)**: Das Frontend spricht nur `http(s)://127.0.0.1:8088`. Host/Port‑Wechsel im Code entfallen; der Proxy kapselt Wechsel der Backends.
- **Pfad‑basierte Trennung**: 
  - Standard‑API: `/api/*` → 5002 (WRITE, performant)
  - Admin/Fallback: `/api-admin/*` → 5001 (Diagnose, WS aus)
  - WS: `/socket.io` → 5002
  - Effekt: Wechsel zwischen Backends erfordert nur Proxy‑(Pfad‑)Anpassung, nicht Frontend‑Code.
- **Zentrale Clients**: 
  - HTTP (axios): `frontend/src/services/api.ts` (BaseURL 8088, `X-API-Key` automatisch)
  - WS: `frontend/src/hooks/useGovernorSocket.ts` (Proxy‑Pfad, Key‑Headers)
  - Effekt: Keine verstreuten Fetches/Ports; einheitliches Fehler‑/Auth‑Handling.
- **Prozess‑Isolation**: 5001, 5002, Vite, Caddy laufen in getrennten Fenstern/Prozessen.
- **Idempotente Orchestrierung**: Skripte stoppen Listener/Prozesse deterministisch und starten alles in definierter Reihenfolge.

Diese Prinzipien reduzieren den „Blast Radius“ von Änderungen: Man debuggt an genau einer Stelle (Proxy, ein Client, ein Backend) und kann jederzeit sauber neu starten.

## 2) Standard Operating Procedures (SOP) – Troubleshooting

### 2.1 Health & Basics
- API/Health (Standard):
  ```powershell
  Invoke-RestMethod http://127.0.0.1:8088/health | ConvertTo-Json -Compress
  Invoke-RestMethod http://127.0.0.1:8088/api/facts/count | ConvertTo-Json -Compress
  ```
- WS‑Handshake:
  ```powershell
  (Invoke-WebRequest "http://127.0.0.1:8088/socket.io/?EIO=4&transport=polling&t=1").Content
  ```

### 2.2 Proxy sichtbar starten
- Foreground (Logs sichtbar, Strg+C beendet):
  ```powershell
  cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
  .\caddy.exe run --config .\Caddyfile --watch
  ```
- Mit Health‑Check/Logs: `scripts/start_caddy.ps1`

### 2.3 Sauberer Neustart (idempotent)
- Vollautomatisch: 
  ```powershell
  pwsh -NoProfile -File "D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\restart_all_ps7_orchestratedONLY.ps1"
  ```
  Stoppt 5001/5002/5004/5173/8088, startet 5001 (NO_WS), 5002 (WRITE), Frontend und 10s später Caddy.

### 2.4 Backend‑spezifisch
- Standard‑API (WRITE): 5002
- Admin/Fallback: 5001 via `/api-admin/*`
- Keine Host/Port‑Wechsel im Frontend – nur Pfade über Proxy.

### 2.5 Frontend‑Fehler (405/404) – Verhalten
- Monitoring/Analyse‑Karten sollen bei 405 „n/a“ anzeigen (statt Konsole zu fluten). 
- Falls Admin‑Daten benötigt werden: Pfad `/api-admin/...` nutzen (Diagnose), niemals Host/Port.

## 3) Sicherheits‑Guardrails (aktuell)
- **API‑Key Pflicht** (Header `X-API-Key`) – zentral im axios‑Client gesetzt.
- **Ein‑Origin** – keine CORS‑Exposition; WS nur über Proxy.
- **Write‑Guards** – 5002 WRITE standardisiert, 5001 Admin; zukünftige Tokens/Scopes kompatibel.

## 4) Empfohlene Eingriffsstellen (Change‑Control)
- **Proxy**: `Caddyfile` (Routing, TLS/HSTS später, Rate‑Limits). Fehler sind sofort sichtbar im Foreground‑Log.
- **HTTP‑Client**: `frontend/src/services/api.ts` (BaseURL, Header/Interceptors).
- **WS‑Client**: `frontend/src/hooks/useGovernorSocket.ts` (Pfad, Auth, Fallback `polling`).
- **UI‑Fallbacks**: `MonitoringPanel.tsx`, `ProKnowledgeStats.tsx`, `ProKnowledgeList.tsx` – 405/404 → „n/a“.

## 5) Operative Checklisten
- Start/Sequenz: `PROJECT_HUB/START_SEQUENCE_PS7.md`
- Ausführlicher Guide (Routing/Skizze): `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md`
- Handover (Erfolge, offene Punkte): `PROJECT_HUB/TECHNICAL_HANDOVER_20250817_GPT5.md`
- Orchestrierungsskripte:
  - `scripts/restart_all_ps7_orchestratedONLY.ps1`
  - `scripts/start_all_ps7_windows.ps1`
  - `scripts/start_caddy.ps1`

## 6) Warum das so sicher funktioniert (Architektur‑Begründung)
- **Separation of Concerns**: Routing (Proxy), Transport (Clients), Logik (Backends) sind klar getrennt.
- **Path Routing statt Host‑Wechsel**: Keine Änderung am Frontend‑Origin nötig, keine CORS‑Nebenwirkungen.
- **Zentrale Clients**: Auth/Fehlerbehandlung an einer Stelle, geringe Fehleranfälligkeit.
- **Prozess‑Isolation**: Jeder Dienst in eigenem Fenster – sichtbare Logs, einfache Beendigung.
- **Deterministische Orchestrierung**: Skripte beenden Listener zuerst und starten in definierter Reihenfolge.

## 7) Roadmap zu Stufe 5 (Kurz)
- TLS/HSTS → JWT/RBAC → Secrets/Rotation → Input/WAF/Rate‑Limits → Observability/Audit → CI/CD‑Security → DR/HA
- Details: `PROJECT_HUB/SECURITY_MATURITY_PLAN_STAGE5.md`

## 8) Quick‑Actions (Operator)
- Status prüfen: `Invoke-RestMethod http://127.0.0.1:8088/health`
- WS prüfen: Handshake wie oben
- p95 messen: `scripts/p95_proxy_health.ps1`
- Voller Neustart: `scripts/restart_all_ps7_orchestratedONLY.ps1`

---
Stand: 2025‑08‑17 – Verantwortlich: GPT‑5 (Handover an Claude Opus für UI‑Fallbacks & Security‑Sprints)

