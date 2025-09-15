---
title: "Technical Handover 20250817 Gpt5"
created: "2025-09-15T00:08:01.026810Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

## Technischer Handover – Lokale Umgebung (Proxy 8088) – Stand 2025-08-17

### Executive Summary
- System ist lauffähig und über Ein‑Origin `http://127.0.0.1:8088` erreichbar.
- Backends: 5001 (Hexagonal API, WS aus) und 5002 (Read‑only + Socket.IO) operativ.
- Frontend: Vite 5173 läuft und wird über 8088 sauber proxied (Assets/JS ok).
- Sicherheit: API‑Key erzwungen; zentral über axios‑Client hinterlegt.
- WebSocket: Verbindung über Proxy stabil; UI meldet „Connected“.
- End‑to‑End Latenz: p95 ~6.6 ms (Facts‑Count über 8088); großer Headroom.

### Verifizierte Fakten (Mess‑/Statusdaten)
- 5001 Health (über 8088):
  ```json
  {"architecture":"hexagonal_clean","port":5001,"repository":"SQLiteFactRepository","status":"operational"}
  ```
- Facts Count (über 8088):
  ```json
  {"cached":false,"count":4003,"ttl_sec":30}
  ```
- 5002 Health:
  ```json
  {"architecture":"hexagonal","mojo":{"available":true,"backend":"mojo_kernels","flag_enabled":true},"port":5002,"read_only":true,"repository":"SQLiteFactRepository","status":"operational"}
  ```
- Socket.IO Handshake über 8088 (Auszug):
  ```
  0{"sid":"<valid-sid>","upgrades":["websocket"],"pingTimeout":20000,...}
  ```
- p95 (50x) über 8088 `/api/facts/count`:
  ```json
  {"count":50,"p95_ms":6.6,"avg_ms":5.24}
  ```

### Architektur/Proxy – aktuelle Konfiguration
- Ein‑Origin Proxy (`:8088`) – `HAK_GAL_HEXAGONAL/Caddyfile`:
  - `/api/*`, `/health` → 5001
  - `/api/mojo/*` → 5002 (Mojo‑Status/Bench auf 5002 gemappt)
  - `/socket.io*`, `/ws*` → 5002 (WebSocket)
  - `/@vite/client`, `/@vite/*`, `/src/*` → 5173 (Content‑Type JS erzwungen)
  - `/` → 5173 (Frontend)

### Wichtige Änderungen (Frontend/Infra)
- Zentraler HTTP‑Client (`axios`): `frontend/src/services/api.ts`
  - `baseURL` aus `VITE_API_BASE_URL` (Fallback fix auf `http://localhost:8088`).
  - Header `X-API-Key` automatisch gesetzt.
- WebSocket‑Client via Proxy: `frontend/src/hooks/useGovernorSocket.ts`
  - Verbindet an `getApiBaseUrl()` + `path=/socket.io`, sendet API‑Key (Headers/auth), `transports: ['websocket','polling']`.
- Proxy‑Assets/MIME fix: Caddy‑Header für Vite‑Assets; `@vite/client` → 200/JS.
- Knowledge‑Graph Fix: `public/knowledge_graph.html` `API_BASE` geleert (verhindert doppeltes `/api/api/...`).
- Startskripte/Guides (Hub):
  - `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md` – ausführlicher Startguide mit Skizze.
  - `PROJECT_HUB/START_SEQUENCE_PS7.md` – kompakte Reihenfolge/Kommandos (PS7).
  - `scripts/start_caddy.ps1` – Foreground/Background‑Start mit Logs/Health‑Check.
  - `scripts/start_all_ps7_windows.ps1` – startet 5001, 5002, Frontend, Proxy in separaten PS‑Fenstern.

### Was funktioniert jetzt (End‑to‑End)
- Frontpage über `http://127.0.0.1:8088` (keine CORS/Port‑Probleme).
- API‑Aufrufe über 8088 (Health/Facts) liefern 200/JSON.
- WebSocket über 8088 ist verbunden, UI zeigt „Connected“ und empfängt KB‑Updates.
- Schreiben über Proxy mit API‑Key (Test‑Fakt) erfolgreich; Verifikation per Suche ok.

### Bekannte offene Punkte (Frontend)
- 405 (Method Not Allowed) bei Monitoring/Analyse‑Endpoints – Beispiele:
  - `/api/limits`, `/api/predicates/top`, `/api/quality/metrics`, `/api/graph/emergency-status`, `/api/facts/paginated`, `/api/facts/stats`.
  - Ursache: Diese Routen sind in 5001 aktuell nicht (GET) implementiert oder heißen abweichend; teils existieren nur POST oder gar nicht.
- UI reagiert darauf mit Fehlermeldungen/Console‑Warnungen.

### Empfohlene Maßnahmen (für nächste Instanz – Claude/Opus)
- Frontend‑Fallbacks/Graceful Degradation implementieren:
  - Bei 405/404: Kachel/Karte auf „n/a“ setzen statt Fehler zu loggen; alternative vorhandene Endpoints nutzen (`facts/count`/`facts/export`) oder Platzhalter.
  - `MonitoringPanel.tsx` und `ProKnowledgeStats.tsx`: try/catch mit Statushandling, optional Retry/Backoff.
- Optionales Proxy‑Routing ergänzen, falls 5002 passende Read‑only Endpoints anbietet:
  - Beispiel: `/api/predicates/top`, `/api/quality/metrics` → 5002 (nur wenn dort vorhanden/konform).
- Einheitliche Analyse‑API in 5001 definieren (GET/POST Semantik klarstellen) oder Feature‑Flags im UI (nur angezeigte Features pollen).

### Start/Bedienung – Referenzen
- Startanleitung ausführlich: `PROJECT_HUB/START_GUIDE_LOCAL_DEV_8088.md`
- Reihenfolge & Kommandos: `PROJECT_HUB/START_SEQUENCE_PS7.md`
- Orchestrierung (mehrere Fenster): `scripts/start_all_ps7_windows.ps1`
- Caddy Start/Logs: `scripts/start_caddy.ps1`
- Proxy‑Konfiguration: `Caddyfile`
- Zentrale Clients: `frontend/src/services/api.ts`, `frontend/src/hooks/useGovernorSocket.ts`

### Kurz‑Checkliste (soll‑Zustand)
- 5001/5002: Health 200 ✅
- Proxy 8088: Health 200, `/@vite/client` 200 ✅
- Frontend über 8088 lädt, WS connected ✅
- API‑Key aktiv, POST funktioniert ✅
- p95 < 10 ms lokal ✅

Vielen Dank – System ist online; verbleibende UI‑Kleinigkeiten sind isoliert und können von der nächsten Instanz (Claude Opus) mit geringem Aufwand gehärtet werden.

