---
title: "Technical Handover Next Instance Mojo 20250814"
created: "2025-09-15T00:08:01.033084Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technisches Übergabeprotokoll – Mojo Rollout (Stand: 2025-08-14)

Dieses Dokument befähigt die nächste Instanz, nahtlos am Mojo‑Projekt weiterzuarbeiten. Alle Schritte sind standardmäßig sicher (read‑only oder flag‑gesteuert) und verändern das laufende System nicht, außer wenn explizit aktiviert.

## 1) Executive Summary
- Zwei parallele Backend‑Instanzen:
  - 5001: Hexagonal Standard (schreibend), SQLite SoT
  - 5002: Hexagonal mit Mojo‑Kernels (read‑only via Kill‑Switch), identischer Datenbestand
- Mojo‑Pfad:
  - Stub + Native gebaut, über Flags/PYTHONPATH aktivierbar
  - Golden‑Tests: 0 Mismatches (Mojo vs. Python)
  - Benchmarks (N≈3.8k): Dedupe ~0.45 s, Validate im ms‑Bereich
- Frontend: Backend‑Switcher im Header (persistiert in localStorage), Umschalten 5001/5002 mit App‑Reload

## 2) Architektur/Topologie
- Ports
  - 5001 (Standard): http://127.0.0.1:5001
  - 5002 (Mojo): http://127.0.0.1:5002 (Kill‑Switch aktiv)
- Datenbank
  - Standard: `k_assistant.db` (SQLite); 5002 liest denselben Bestand (read‑only empfohlen)
- GPU/Modelle
  - 5001 lädt Modelle auf GPU (RTX 3080 Ti Laptop 16 GB), 5002 kann ebenfalls (ausreichend VRAM vorhanden)

## 3) Aktueller Status (letzte Messungen)
- 5002 Quality (sample_limit=5000):
  - total 3877, checked 3877, invalid 5, duplicates 0, isolated ~1815, contradictions 0
  - Top Prädikate: HasPart 768, HasPurpose 714, Causes 601, HasProperty 584, IsDefinedAs 388, IsSimilarTo 203, …
- Facts 5002: count 3877 (uncached)
- Health/Status 5002: operational
- Mojo‑Status 5002: available=true, backend=mojo_kernels, flag_enabled=true
- Golden (5002, Limit 5k): validate_mismatches=0; dupes_python=104, dupes_mojo=104
- Benchmark (5002, N≈3877): validate ~1.26 ms; dupes ~0.44–0.47 s

## 4) Mojo – Build & Artefakte (native)
- Quelle: `native/mojo_kernels/src/mojo_kernels.cpp` (pybind11)
- CMake: `native/mojo_kernels/CMakeLists.txt` (FindPython3 + pybind11)
- Artefakt: `native/mojo_kernels/build/Release/mojo_kernels.cp311-win_amd64.pyd`
- Build‑Skripte:
  - PowerShell: `scripts/build_mojo_native.ps1`
  - Batch: `scripts/build_mojo_native.bat`
  - Bash: `scripts/build_mojo_native.sh`

## 5) Aktivierung/Flags (feingranular)
- Allgemein:
  - `MOJO_ENABLED` (true|false)
  - `PYTHONPATH` muss den Ordner mit der `.pyd` enthalten (z. B. `...\native\mojo_kernels\build\Release`)
- Teilpfade (default: aus):
  - `MOJO_VALIDATE_ENABLED` – nutzt Mojo für validate_facts_batch
  - `MOJO_DUPES_ENABLED` – nutzt Mojo für find_duplicates
- Beispiel (Server 5002):
```
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release;$env:PYTHONPATH"
$env:MOJO_ENABLED="true"
$env:MOJO_VALIDATE_ENABLED="true"
$env:MOJO_DUPES_ENABLED="false"
.\start_native.bat  # Standard-Port 5001 (frei halten)
# Alternative 5002: Direktstart über create_app, z. B. in PS:
$py = ".\..venv_hexa\Scripts\python.exe"
$code = "import sys; sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal'); import hexagonal_api_enhanced as m; api=m.create_app(use_legacy=False, enable_all=True); api.run(host='127.0.0.1', port=5002, debug=True)"
& $py -c $code
```
- Kill‑Switch (read‑only):
```
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5002/api/safety/kill-switch/activate -Body (@{} | ConvertTo-Json) -ContentType application/json
```

## 6) Frontend – Backend‑Switcher
- Komponenten:
  - `frontend/src/components/BackendSwitcher.tsx`
  - `frontend/src/components/ProHeader.tsx` (Switcher eingebunden)
  - `frontend/src/config/backends.ts` – enthält `hexagonal` (5001) und `mojo_native_5002` (5002)
- Verhalten: Auswahl persistiert in `localStorage('active_backend')`; App reloadet, WebSocket verbindet zum neuen `WS_URL`

## 7) Tools/Automation (read‑only)
- Snapshots:
  - `scripts/extensions/auto_snapshot_status.py` – erzeugt Markdown mit Health/Status/Count/Quality/Mojo
  - `scripts/extensions/hourly_status_runner.ps1` – schreibt Snapshots 5001/5002 + Golden(5002)
- Golden:
  - `scripts/extensions/golden_mojo_vs_python.py` – Mojo vs. Python, Ergebnisgleichheit
- Benchmarks:
  - `scripts/extensions/run_mojo_bench.ps1` – Read‑only Benchmarks gegen exportierte Daten

## 8) MCP‑Snapshots (optional, write‑gate)
- Schreibzugriff via MCP erfordert:
  - `HAKGAL_WRITE_ENABLED=true`
  - ggf. `HAKGAL_WRITE_TOKEN=<token>`
- Danach `project_snapshot` Tool benutzen (legt Snapshot im `PROJECT_HUB` an)

## 9) Risiken & Empfehlungen
- Parallelbetrieb: ok bei getrennten Ports; 5002 read‑only oder separate SQLite‑Datei; GPU‑Last im Blick behalten
- Dedupe‑Skalierung: O(n²); für große Batches serverseitig batchen/threshold beachten
- Flags: schrittweise aktivieren; Golden‑Test auf 0 Mismatches halten

## 10) Nächste Schritte (priorisiert)
1) Golden‑Tests (5k/10k) zyklisch – Regulärbericht in den Hub
2) Bench‑Serie (5k/10k/50k) für Validate/Dedupe – Trends im Hub
3) Packaging (wheel via scikit‑build‑core) – kein Install nötig, nur vorbereiten
4) Optional: Server‑Bulk‑Pfad selektiv via Mojo‑Validate (Flag‑gesteuert)
5) ggf. separate SQLite‑DB für 5002 konfigurieren (Write entkoppeln)

## 11) Befehlsreferenz (Schnellzugriff)
- Snapshots (manuell):
```
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\auto_snapshot_status.py --api http://127.0.0.1:5001 --out PROJECT_HUB\SNAPSHOT_5001_<ts>.md
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\auto_snapshot_status.py --api http://127.0.0.1:5002 --out PROJECT_HUB\SNAPSHOT_5002_<ts>.md
```
- Golden/Bench (Read‑Only):
```
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release;$env:PYTHONPATH"
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\golden_mojo_vs_python.py --api http://127.0.0.1:5002 --limit 5000 --out PROJECT_HUB\REPORT_MOJO_GOLDEN_5002_<ts>.md
.\scripts\extensions\run_mojo_bench.ps1 -Api http://127.0.0.1:5002 -Limit 5000 -EnableMojo
```
- Frontend‑Switch: Header‑Switcher verwenden (persistiert in localStorage)

---

Dieses Protokoll wird fortgeschrieben (Bench/Golden/Snapshots, Packaging, Teilpfad‑Rollout). Für Fragen zu Build/Flags/Ports siehe die genannten Skripte und Configs. Alles hier bleibt ohne Risiko, solange Schreibpfade nicht explizit aktiviert werden.
