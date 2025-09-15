---
title: "Mojo Rollout Status 20250814 2215"
created: "2025-09-15T00:08:01.057313Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# MOJO Rollout Status – Readiness & Fakten (2025-08-14 22:15)

Diese Notiz konsolidiert alle relevanten Informationen zum Mojo‑Vorhaben. Sie ist read‑only und ändert keinerlei Laufzeitverhalten.

## 1) Architektur- und Systemstatus (Read-Only)
- Backend: Hexagonal (Port 5001), SQLite SoT, WebSocket optional
- Health (aktuell): operational; repository: SQLite; mojo.flag=false (Server), true/false je nach Client‑Flag
- KB‑Volumen: zuletzt ~3.8k Fakten
- Top Prädikate (Sample): HasPart, HasPurpose, Causes, HasProperty, IsDefinedAs, …
- Qualität (Sample): invalid ~5, duplicates 0, isolated ~1.8k, contradictions 0

Verweise (Hub):
- `PROJECT_HUB/SNAPSHOT_STATUS_20250814_1409.md`
- `PROJECT_HUB/AUTO_READONLY_STATUS_CHECK_20250814_1415.md`

## 2) Implementierte Mojo‑Vorbereitung (keine Verhaltensänderung)
- Adapter (Feature‑Flag, Fallbacks)
  - `src_hexagonal/adapters/mojo_kernels_adapter.py`
    - Flag: `MOJO_ENABLED` (default: aus)
    - Best‑effort Load: `mojo_kernels` (nativ) ODER `src_hexagonal.mojo_kernels` (Stub)
    - Public APIs: `validate_facts_batch`, `find_duplicates`
  - Health/Endpoint‑Sichtbarkeit
    - `GET /api/mojo/status`: zeigt `present`, `flag_enabled`, `available`, `backend`
    - Health enthält Mojo‑Block
- Stub (keine Beschleunigung, identische Signaturen)
  - `src_hexagonal/mojo_kernels.py`
- Native Skeleton (inaktiv, nur Build‑Zeit)
  - `native/mojo_kernels/src/mojo_kernels.cpp` (pybind11)
  - `native/mojo_kernels/CMakeLists.txt` (FindPython3 + pybind11)

Doku (Hub):
- `PROJECT_HUB/TECHNICAL_HANDOVER_MOJO_ADAPTER_GPT5_20250814.md`
- `PROJECT_HUB/BUILD_GUIDE_MOJO_NATIVE_20250814.md`
- `PROJECT_HUB/MOJO_BENCHMARK_PLAN_20250814.md`

## 3) Build‑Pfade & Artefakte (nativ)
- Generator: Visual Studio 17 2022 (Clang/GCC/Ninja optional möglich)
- Artefakt erzeugt:
  - `native/mojo_kernels/build/Release/mojo_kernels.cp311-win_amd64.pyd`
  - Timestamp: 2025‑08‑14 22:10
- Build‑Skripte (nicht invasiv):
  - `scripts/build_mojo_native.ps1` (PowerShell)
  - `scripts/build_mojo_native.bat` (Batch)
  - `scripts/build_mojo_native.sh` (Bash)

## 4) Benchmarks (Read‑Only, via Client‑Script)
- Script: `scripts/extensions/benchmark_mojo_adapter.py`
- Runner: `scripts/extensions/run_mojo_bench.ps1`
- Messpunkte (N ≈ 2000):
  - Ohne Mojo (Fallback): validate ~1.02 ms; dupes ~0.80 s
  - Mit Mojo‑Stub: validate ~0.71–1.17 ms; dupes ~0.45–0.49 s
  - Mit Mojo‑Native (pyd geladen, Client‑seitig): verfügbar; Zeiten abhängig von IO/Batchgrößen (erste Läufe im ~0.45 s Bereich bei Dedupe)
- Report: `PROJECT_HUB/REPORT_MOJO_BENCHMARK.md`

Hinweis: Die größten Effekte werden bei größeren Batches (10k/50k) und serverseitigem Bulk‑Pfad sichtbar. Das Script begrenzt Dedupe‑Sample auf 2000 (O(n²)).

## 5) Aktivierung (sicher, kontrolliert)
- Client‑seitig (Script/Tests):
  - `PYTHONPATH` um native Release ergänzen: `native/mojo_kernels/build/Release`
  - Flag setzen: `MOJO_ENABLED=true`
- Server‑seitig (später, falls gewünscht):
  - Vor Start: `PYTHONPATH` + `MOJO_ENABLED=true`
  - Verifikation: `GET /api/mojo/status` ⇒ `available=true`, `backend=mojo_kernels`

Beispiel (PowerShell, Server):
```
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release;$env:PYTHONPATH"
$env:MOJO_ENABLED="true"
.\start_native.bat
# dann:
Invoke-RestMethod -Uri http://127.0.0.1:5001/api/mojo/status | ConvertTo-Json -Depth 5
```

## 6) Sicherheit & Governance
- Feature‑Flag‑Gate verhindert unbeabsichtigte Aktivierung.
- Fallbacks: Bei Fehlern/Fehlen des nativen Moduls automatisch Python‑Pfad.
- Keine API‑/Schema‑Änderungen, keine schreibenden Pfade angepasst.
- Kill‑Switch/Policy‑Guard unverändert.

## 7) Nächste Schritte (rollierend, risikoarm)
- Golden‑Tests: Ergebnisgleichheit Mojo vs. Python (Validator/Similarity) + Property‑Tests.
- Benchmarks skaliert (10k/50k) inkl. Auswertung in Hub‑Report (Delta/CPU/Memory).
- Optionaler Server‑Bulk‑Pfad: Vorvalidierung via Adapter (Flag‑gesteuert), Log‑Sampling.
- Packaging: wheel/scikit‑build für einfache Verteilung; SemVer/ABI‑Version.
- Rollout‑Plan: Canary (zuerst Validierung, dann Similarity), schnelle Rückrolle über Flag.

## 8) Troubleshooting (Build/Runtime)
- Build: Bei Generator‑Konflikt `build/` löschen, neu konfigurieren.
- Python‑Libs: Mit `FindPython3` + `PYBIND11_FINDPYTHON=ON` konfigurieren; `Python3_EXECUTABLE` auf venv‑Python setzen.
- PATH/Quotes: Pfade mit Leerzeichen immer in Anführungszeichen; `PYTHONPATH` explizit setzen.

## 9) Schnellreferenz – Kommandos
- Benchmark (Client): `scripts\extensions\run_mojo_bench.ps1 -Limit 2000 -EnableMojo`
- Server‑Aktivierung (testweise): `PYTHONPATH` + `MOJO_ENABLED=true` + `start_native.bat`
- Status:
  - `GET /health`
  - `GET /api/mojo/status`
  - `GET /api/facts/count`
  - `GET /api/quality/metrics`

---

Diese Notiz wird bei weiteren Schritten (Tests, größere Benchmarks, Packaging) fortgeschrieben. Alle hier beschriebenen Handlungen sind sicher (read‑only oder durch Flag geschützt) und verändern das laufende System nicht.
