# Technisches Übergabeprotokoll – Nächste Instanz (Stand: 2025-08-14)

Dieses Dokument befähigt die nächste Instanz, die HAK‑GAL Hexagonal Suite sicher und reproduzierbar fortzuführen. Es deckt Architektur, aktuelle Änderungen, Betriebsabläufe, Validierungsergebnisse, Risiken und Roadmap ab. Alle hier dokumentierten Schritte sind standardmäßig read‑only bzw. flag‑gesteuert und gefährden den laufenden Betrieb nicht, solange Schreibpfade nicht explizit aktiviert werden.

## 1) Executive Summary
- Aktive Backends:
  - 5001: Hexagonal Standard (schreibend), SQLite SoT
  - 5002: Hexagonal mit Mojo‑Kernels (read‑only via Kill‑Switch), identischer Datenbestand
- Neuer Code‑Schalter (sicher): SQLite‑Adapter unterstützt nun ENV‑Overrides für DB‑Pfad und Read‑Only‑URI
  - `HAKGAL_SQLITE_DB_PATH` bzw. `SQLITE_DB_PATH`
  - `HAKGAL_SQLITE_READONLY=true` → automatische `file:...?...mode=ro` Nutzung
- Validierung 5002: Golden‑Tests 0 Mismatches; Benchmarks bestätigen massive Beschleunigung auf Mojo‑Pfad
- Monitoring/Snapshots: regelmäßige Status‑Artefakte im `PROJECT_HUB`, Golden‑Reports, Benchmarks
- Frontend: Backend‑Switcher (persistiert in `localStorage`); Umschalten zwischen 5001/5002

## 2) Architektur/Topologie (Hexagonal)
- Muster: Ports & Adapters; Domäne entkoppelt von Transport/Frameworks
- Inbound: REST (Flask), optional WebSocket
- Application: `FactManagementService`, `ReasoningService`, Policy Guards, Kill‑Switch
- Outbound:
  - `SQLiteFactRepository` (SoT; `k_assistant.db`)
  - Mojo‑Kernels Adapter (flag‑gesteuert, Stub/Native)
  - Optional Monitoring/Governor
- Ports
  - 5001 (Standard): `http://127.0.0.1:5001`
  - 5002 (Mojo): `http://127.0.0.1:5002` (Kill‑Switch aktiv)

Wesentliche Dateien:
- `src_hexagonal/hexagonal_api_enhanced.py` – zentraler API‑Layer
- `src_hexagonal/adapters/sqlite_adapter.py` – SQLite‑Repository (neu: ENV‑ReadOnly/URI)
- `scripts/extensions/*` – Snapshots, Golden, Bench
- `PROJECT_HUB/*` – Handover-/Status‑Artefakte

## 3) Jüngste Änderungen (2025‑08‑14)
**SQLite‑Adapter (Read‑Only/URI‑Support):**
- Neu: Der Adapter akzeptiert ENV‑Variablen, um pro Instanz einen alternativen Pfad bzw. eine Read‑Only‑URI zu setzen.
  - `HAKGAL_SQLITE_DB_PATH` oder `SQLITE_DB_PATH` – absoluter Pfad oder `file:`‑URI
  - `HAKGAL_SQLITE_READONLY=true` – wandelt Dateipfade automatisch in `file:/...?...mode=ro&cache=shared` um
- Intern: Verbindungsaufbau nutzt bei `file:`‑URIs `sqlite3.connect(..., uri=True)`
- Ziel: 5002 (und optionale Test‑Instanzen) können strikt im Read‑Only‑Modus laufen, ohne 5001 zu beeinflussen.

Betroffene Datei:
- `src_hexagonal/adapters/sqlite_adapter.py` (sicher, rückwärtskompatibel; keine Änderung für 5001 ohne ENV)

## 4) Laufzeit/Start (strikt venv)
Die Python‑Aufrufe müssen strikt innerhalb der Projekt‑venv erfolgen (`.venv_hexa`) – außerhalb funktioniert Python nicht zuverlässig [[venv‑Vorgabe]].

Start 5002 (read‑only, Mojo Validate an):
```powershell
cd "D:\MCP Mods\HAK_GAL_HEXAGONAL"
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release;$env:PYTHONPATH"
$env:HAKGAL_SQLITE_DB_PATH="file:D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db?mode=ro&cache=shared"
$env:HAKGAL_SQLITE_READONLY="true"
$env:MOJO_ENABLED="true"
$env:MOJO_VALIDATE_ENABLED="true"
$env:MOJO_DUPES_ENABLED="false"
.\.venv_hexa\Scripts\python.exe -c "import sys; sys.path.insert(0, r'D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal'); import hexagonal_api_enhanced as m; m.create_app(use_legacy=False, enable_all=True).run(host='127.0.0.1', port=5002, debug=False)"
# Absicherung: Read-Only Kill-Switch aktivieren
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:5002/api/safety/kill-switch/activate -Body (@{} | ConvertTo-Json) -ContentType application/json
```

Hinweise:
- 5001 bleibt unverändert; ENV wirkt nur auf die Instanz, in der der Prozess gestartet wurde.
- Optional: 5002 gegen eine periodische SQLite‑Kopie hängen (`.../k_assistant_ro.db`), um Schreib‑Locks vollständig auszuschließen.

## 5) Validierungsergebnisse (5002)
- Health/Status: operational
- Facts: 3877
- Top‑Prädikate (Auszug): HasPart 768, HasPurpose 714, Causes 601, HasProperty 584, IsDefinedAs 388–389, IsSimilarTo 203, IsTypeOf 203, HasLocation 106, ConsistsOf 88, WasDevelopedBy 66
- Qualität: invalid 5, duplicates 0, isolated ~1815, contradictions 0
- Golden (Limit 5k): `validate_mismatches=0`, `dupes_python=104`, `dupes_mojo=104`
- Benchmark: validate ~1.19 ms; duplicates ~500.9 ms (Sample 2000; threshold 0.95)

Referenzartefakte (im `PROJECT_HUB`):
- `REPORT_MOJO_GOLDEN_5002_20250814_232256.md`
- `REPORT_MOJO_BENCHMARK.md`
- `SNAPSHOT_5001_20250814_232534.md`, `SNAPSHOT_5002_20250814_232534.md`

## 6) Frontend – Backend‑Switcher
- Komponenten:
  - `frontend/src/components/BackendSwitcher.tsx`
  - `frontend/src/components/ProHeader.tsx`
  - `frontend/src/config/backends.ts` – enthält `hexagonal` (5001) und `mojo_native_5002` (5002)
- Verhalten: Auswahl persistiert in `localStorage('active_backend')`; App reloadet; WebSocket verbindet zum neuen `WS_URL`.
- Empfehlung: Für A/B‑Vergleiche nur Lesepfade gegen 5002 nutzen; alle Schreibaktionen weiterhin auf 5001.

## 7) Monitoring & Automation (read‑only)
- Snapshots (manuell):
```powershell
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\auto_snapshot_status.py --api http://127.0.0.1:5001 --out PROJECT_HUB\SNAPSHOT_5001_<ts>.md
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\auto_snapshot_status.py --api http://127.0.0.1:5002 --out PROJECT_HUB\SNAPSHOT_5002_<ts>.md
```
- Stündlicher Runner:
```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\extensions\hourly_status_runner.ps1 -GoldenLimit 5000
```
- Golden/Bench (read‑only):
```powershell
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\native\mojo_kernels\build\Release;$env:PYTHONPATH"
.\.venv_hexa\Scripts\python.exe .\scripts\extensions\golden_mojo_vs_python.py --api http://127.0.0.1:5002 --limit 5000 --out PROJECT_HUB\REPORT_MOJO_GOLDEN_5002_<ts>.md
.\n+scripts\extensions\run_mojo_bench.ps1 -Api http://127.0.0.1:5002 -Limit 5000 -EnableMojo
```

## 8) Sicherheitsmechanismen
- **Kill‑Switch**: `/api/safety/kill-switch/activate` sperrt Schreibpfade (Server 5002 read‑only halten)
- **PolicyGuard**: Strenge Prüfung bei Schreiboperationen; Audit/Locking vorgesehen
- **ENV‑Gates für Writes** (MCP‑Tools): `HAKGAL_WRITE_ENABLED`, optional `HAKGAL_WRITE_TOKEN`

## 9) Risiken & Mitigation
- Parallelbetrieb: 5001 (write) und 5002 (read‑only) auf getrennten Ports – kein Risiko bei strikter Trennung
- SQLite‑Locks: Bei direkter Nutzung derselben Datei Read‑Only‑URI (`mode=ro`) verwenden oder Kopie (`*_ro.db`)
- Dedupe‑Skalierung: O(n²) – serverseitig `limit`/`threshold`/Sampling nutzen
- Flags schrittweise aktivieren, Golden muss 0 Mismatches halten

## 10) Nächste Schritte (Roadmap)
1) Golden zyklisch (5k/10k), Abweichungen alarmieren; Bench‑Serien (5k/10k/50k) für Trendanalyse
2) Packaging vorbereiten (wheel via `scikit‑build‑core`), ohne Deploy‑Änderungen an 5001
3) Selektiver Bulk‑Pfad über Mojo‑Validate (nur Validierung, keine Schreibdurchleitung)
4) Optionale separate SQLite‑DB nur für 5002 konfigurieren; CI‑Healthcheck für Read‑Only Start
5) Frontend‑UX verbessern (saubere Fehlermeldungen bei 503/Read‑Only, klarer Schreibschutzindikator)

## 11) Referenz – API/Tools
- REST: `/health`, `/api/status`, `/api/facts` (GET/POST), `/api/facts/count`, `/api/predicates/top`, `/api/quality/metrics`, `/api/facts/export`, `/openapi.json`
- MCP‑Tools (Auszug): `search_knowledge`, `kb_stats`, `semantic_similarity`, `analyze_duplicates`, `consistency_check`, `project_snapshot` u. a.

## 12) Anhänge
- „Screenshot“/Statusauszug: `PROJECT_HUB/SCREENSHOT_STATUS_5001_5002_20250814_2359.md`
- Golden/Bench/Snapshots: siehe Abschnitt 5

---
Dieses Protokoll ist live pflegbar und sollte bei Architektur‑/Betriebs‑ oder Sicherheitsänderungen aktualisiert werden. Alle Startbefehle setzen die Nutzung der Projekt‑venv `.venv_hexa` voraus.

Hinweis [[venv‑Vorgabe]]: Der Betrieb außerhalb der Projekt‑venv ist nicht unterstützt und führt zu Inkonsistenzen.


