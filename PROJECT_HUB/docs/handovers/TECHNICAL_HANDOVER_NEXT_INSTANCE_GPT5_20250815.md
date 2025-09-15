---
title: "Technical Handover Next Instance Gpt5 20250815"
created: "2025-09-15T00:08:01.033084Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technisches Übergabeprotokoll – Nächste Instanz (Stand: 2025-08-15)

Dieses Dokument befähigt die nächste Instanz, das Hexagonal‑System mit Mojo sicher weiterzuführen. Alle beschriebenen Schritte sind standardmäßig read‑only bzw. flag‑gesteuert und gefährden den laufenden Betrieb nicht.

## 1) Executive Summary
- Backends parallel:
  - 5001: Hexagonal Standard, schreibend (SQLite SoT)
  - 5002: Hexagonal + Mojo, read‑only (Kill‑Switch), identischer Datenbestand
- Qualität/Leistung (Mojo geprüft): Golden (5k) 0 Mismatches; Duplikate Python=104, Mojo=104. Bench: validate ~1.2 ms; duplicates ~0.5 s (Sample 2000).
- Frontend: Backend‑Switcher (localStorage) – schnelles Umschalten 5001/5002.
- Automation: stündliche Statusläufe und Golden in `PROJECT_HUB` aktiv.

## 2) Architektur/Topologie (Hexagonal)
- Inbound: REST (Flask), optional WebSocket.
- Application: Fact‑ und Reasoning‑Services, Policy Guard, Kill‑Switch.
- Outbound: `SQLiteFactRepository` (SoT), optional Mojo‑Kernels (flag‑gesteuert, read‑only Pfade).
- Ports: 5001 Standard, 5002 Mojo (read‑only), optional 5003 Testinstanz.

Wesentliche Dateien:
- `src_hexagonal/hexagonal_api_enhanced.py` – REST/WS, Qualität/Analyse/Flags.
- `src_hexagonal/adapters/sqlite_adapter.py` – SQLite‑Repo mit ENV‑Overrides, Read‑Only‑URI.
- `scripts/launch_5002_mojo.py` – sichtbarer Start (Logs im PS‑Fenster).
- `scripts/extensions/restart_5002.ps1` – komfortabler Neustart (Health/Kill‑Switch/Logs).
- `scripts/extensions/rollback_5002.ps1` – Rollback baseline read‑only (ohne Mojo).
- `scripts/extensions/hourly_status_all.ps1` / `hourly_loop.ps1` – Automation.
- `PROJECT_HUB/SERVER_START_GUIDE_HEXAGONAL_5001_5002_20250815.md` – Startanleitung.

## 3) Status & Kennzahlen (zuletzt gemessen)
- Facts: 3877 (beide Backends).
- Top‑Prädikate (Top 10): HasPart 768, HasPurpose 714, Causes 601, HasProperty 584, IsDefinedAs 388/389, IsSimilarTo 203, IsTypeOf 203, HasLocation 106, ConsistsOf 88, WasDevelopedBy 66.
- Qualität (Sample 5k): invalid 5, duplicates 0, isolated ~1815, contradictions 0.
- Mojo 5002: available=true, flag_enabled=true.

## 4) Laufzeit/Start (strikt `.venv_hexa`)
- venv aktivieren:
```powershell
& "D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv_hexa/Scripts/Activate.ps1"
```
- 5002 komfortabel (read‑only + Mojo Validate + Dupes):
```powershell
.\n scripts\extensions\restart_5002.ps1 -Mojo -Validate -Dupes -DbUri 'file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared' -Port 5002 -HealthTimeoutSec 120
```
- Sichtbar (Logs im Fenster):
```powershell
$env:HAKGAL_PORT='5002'
powershell -NoProfile -NoExit -Command "& 'D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe' 'D:\MCP Mods\HAK_GAL_HEXAGONAL\scripts\launch_5002_mojo.py'"
```
- Rollback 5002 (baseline, ohne Mojo):
```powershell
.
 scripts\extensions\rollback_5002.ps1 -Port 5002
```

## 5) Read‑Only/Flags (Mojo)
- ENV (Beispiel 5002):
```powershell
$env:HAKGAL_SQLITE_DB_PATH='file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared'
$env:HAKGAL_SQLITE_READONLY='true'
$env:MOJO_ENABLED='true'
$env:MOJO_VALIDATE_ENABLED='true'
$env:MOJO_DUPES_ENABLED='true'
```
- Admin‑Routen (falls verfügbar):
  - GET `/api/mojo/flags` – Adapterstatus/ENV.
  - POST `/api/mojo/flags` Body `{"enabled":true,"validate":true,"dupes":true}` – Flags setzen.

## 6) Analyse (read‑only)
- Qualität: `GET /api/quality/metrics?sample_limit=5000&sem_threshold=0.95` – inkl. Top‑Prädikate, optional `semantic_duplicates`.
- Duplikate: `GET /api/analysis/duplicates?sample_limit=2000&threshold=0.95` – Mojo/Fallback.
- Golden: `GET /api/mojo/golden?limit=5000&threshold=0.95` – 0 Mismatches erwartet.
- Bench: `GET /api/mojo/bench?limit=3877&threshold=0.95` – Zeitmessungen validate/duplicates.

## 7) Frontend
- Backend‑Switcher (persistiert in `localStorage`), Umschalten 5001/5002 mit Reload.
- Für 5002 ausschließlich Lesepfade verwenden (read‑only); Writes weiterhin 5001.

## 8) Monitoring & Artefakte
- Stündliche Runner schreiben:
  - `SNAPSHOT_5001_*.md`, `SNAPSHOT_5002_*.md`, optional `SNAPSHOT_5003_*.md`.
  - `REPORT_MOJO_GOLDEN_5002_*.md` (und optional `*_5003_.md`).
  - `AUTO_HOURLY_STATUS[_ALL]_*.md`.

## 9) Betriebssicherheit, Port & Prozesskontrolle
- Portkonflikt (`WinError 10048`): Prozess auf Port beenden:
```powershell
$pid = (Get-NetTCPConnection -LocalPort 5002 -State Listen | Select-Object -First 1 -ExpandProperty OwningProcess)
if ($pid) { Stop-Process -Id $pid -Force }
```
- Prozess nicht unnötig beenden (Modelle bleiben nur im RAM dieses Prozesses geladen).

## 10) Performance/Modelle
- Modelle (SentenceTransformer, NLI, HRM) laden pro Prozess. Startkosten vermeiden, indem der Prozess weiterläuft.
- Optional (Roadmap):
  - Legacy‑Reasoning für 5002 per Flag deaktivieren (nur Mojo‑Analysen).
  - Separater Shared‑Model‑Dienst (persistenter Prozess) für schnelle Starts.

## 11) Nächste Schritte (priorisiert)
1) Mojo‑Pfad in weiteren Read‑Only‑Analysen ausbauen (Golden=0 halten).
2) Tägliche Trendberichte (invalid/isolated, Dupe‑Trends) automatisieren.
3) Packaging vorbereiten (wheel, scikit‑build‑core) – keine 5001‑Änderungen.
4) Optional: Shared‑Model‑Dienst (persistenter Prozess), Reasoning‑Flag‑Gate in 5002.

## 12) Referenz‑Links (Direkttests 5002)
- Health/Status: `http://localhost:5002/health`, `http://localhost:5002/api/status?light=1`.
- Count/Qualität: `http://localhost:5002/api/facts/count`, `http://localhost:5002/api/quality/metrics?sample_limit=5000&sem_threshold=0.95`.
- Analyse: `http://localhost:5002/api/analysis/duplicates?sample_limit=2000&threshold=0.95`.
- Admin/Golden/Bench (falls verfügbar): `/api/mojo/flags`, `/api/mojo/golden`, `/api/mojo/bench`.

---
Siehe zusätzlich: `PROJECT_HUB/SERVER_START_GUIDE_HEXAGONAL_5001_5002_20250815.md` (copy‑paste‑fähige Startbefehle).
