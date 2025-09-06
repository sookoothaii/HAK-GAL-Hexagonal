# Technical Handover – Mojo Adapter (Safe Hybrid Preparation)

Datum: 2025-08-14
Autor: GPT-5

## 1) Executive Summary
- Ziel: Risikoarme Hybrid-Integration für Performance-Hotspots (Parser/Validator, Similarity/Dedupe), ohne bestehendes Verhalten zu verändern.
- Umsetzung: Feature-Flag-Adapter lädt optional Mojo-Kernels (Stub vorhanden); Standard: aus; sichere Python-Fallbacks aktiv.
- Impact: 0% Breaking Changes; neue Statussicht via `/api/mojo/status` und Health-Mojo-Block; Produktionspfade unverändert.

## 2) Architektur-Kontext (Hexagonal)
- Inbound: REST (Flask, Port 5001), optional WebSocket.
- Application: `FactManagementService`, `ReasoningService`.
- Outbound: `SQLiteFactRepository` (SoT), ggf. JSONL-Export, Monitoring/Governor optional.
- Governance: Kill-Switch/Policy-Guard bleiben unverändert.

## 3) Änderungen im Code (Scope & Files)
Neu:
- `src_hexagonal/adapters/mojo_kernels_adapter.py`
  - Feature-Flag `MOJO_ENABLED` (default off)
  - Best-effort-Load: `mojo_kernels` (pybind11) ODER `src_hexagonal.mojo_kernels` (Stub)
  - Fallbacks: Python-Regex-Validierung, Token-Jaccard-Dedupe
  - Öffentliche Methoden:
    - `is_flag_enabled()`, `is_available()`, `backend_name()`
    - `validate_facts_batch(List[str]) -> List[bool]`
    - `find_duplicates(List[str], threshold: float) -> List[Tuple[int,int,float]]`
- `src_hexagonal/mojo_kernels.py`
  - Stub mit identischer Signatur:
    - `validate_facts_batch` – Regex-Validierung identisch zum Server
    - `find_duplicates` – einfache Token-Jaccard-Heuristik

Editiert:
- `src_hexagonal/hexagonal_api_enhanced.py`
  - Initialisiert optional `MojoKernelsAdapter`
  - Health erweitert: `mojo.flag_enabled`, `mojo.available`, `mojo.backend`
  - Neuer Read-Only-Endpoint: `GET /api/mojo/status`
  - Optionaler Vorab-Call in `POST /api/facts/bulk` (nur Validierung; keine Logik-/Policy-Änderung)

## 4) Laufzeitverhalten & Kompatibilität
- Keine Änderungen an bestehenden API-Signaturen, CRUD-/Search-/Reasoning-Pfaden.
- Datenhaltung unverändert (SQLite SoT, JSONL Export).
- Frontend unverändert; neue Statusroute optional.
- Flag off: System exakt wie vorher; Flag on ohne Kernel: Python-Fallback; Flag on mit Stub: available=true, weiterhin gleiche Ergebnisse.

## 5) Aktivierung / Deaktivierung
Aktivierung (Session-basiert):
```powershell
$env:MOJO_ENABLED="true"
$env:PYTHONPATH="D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal;$env:PYTHONPATH"
.\start_native.bat
```
Deaktivierung:
```powershell
$env:MOJO_ENABLED="false"
.\start_native.bat
```
Hinweis: Flag wird beim Start gelesen; Änderungen erfordern Neustart.

## 6) Verifikation (Live-Endpunkte)
Health (Beispiel):
```json
{"status":"operational","architecture":"hexagonal","port":5001,"repository":"SQLiteFactRepository","mojo":{"flag_enabled":false,"available":false,"backend":"python_fallback"}}
```
Mojo-Status (Beispiel bei Stub):
```json
{"mojo":{"present":true,"flag_enabled":true,"available":true,"backend":"src_hexagonal.mojo_kernels"}}
```

## 7) Sicherheit & Risiken
- Feature-Flag-Gate schützt vor unbeabsichtigten Verhaltensänderungen.
- Fallbacks sichern Verfügbarkeit, selbst wenn kein natives Modul vorhanden ist.
- Kill-Switch/Policy-Guard unverändert (Write bleibt geschützt).
- Risiken: Keine zur Laufzeit bei Flag off; bei Flag on weiterhin deterministische Fallbacks.

## 8) Benchmarks & Abnahmekriterien (geplant)
- Parser/Validator: 1k/10k/100k Facts; Ziel: 5–15× Speedup (mit nativen Kernels).
- Similarity/Dedupe: Ziel: 3–10× auf 10k–100k Facts; Ergebnisgleichheit ±Toleranz.
- Golden-Tests: Mojo vs. Python; Property-Based-Tests (Random Inputs, Grenzfälle).
- Abnahme: Keine API-/Schema-Änderungen; Health/Status stabil; Benchmarks ≥ Zielwerte.

## 9) Operativer Leitfaden (Admin)
Start & Status:
```powershell
.\start_native.bat
Invoke-RestMethod -Uri http://127.0.0.1:5001/health | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri http://127.0.0.1:5001/api/mojo/status | ConvertTo-Json -Depth 5
```
Qualität/Metriken:
- `GET /api/facts/count`
- `GET /api/quality/metrics`
- `GET /api/predicates/top`
Kill-Switch:
- `GET /api/safety/kill-switch`

## 10) Rollback-Plan
- Flag auf `false` → Neustart → Verhalten exakt wie vor Integration.
- Stub entfernen ohne Auswirkungen, solange Flag off.
- Der Adapter deaktiviert sich automatisch bei Importfehlern (best-effort load).

## 11) Umgebungsvariablen
- `MOJO_ENABLED` (true|false) – aktiviert Mojo-Pfad, wenn verfügbar.
- `PYTHONPATH` – optional, um `src_hexagonal.mojo_kernels` sicher aufzulösen.
- Bestehende Variablen (z. B. SENTRY_DSN) bleiben unberührt.

## 12) Referenzen (Hub)
- `PROJECT_HUB/ABHANDLUNG_AUTOMATISCHE_WISSENSGENERIERUNG_GPT5_20250814.md`
- `PROJECT_HUB/ARCHITECTURE_OVERVIEW.md`
- `PROJECT_HUB/FRONTEND_FIX_SNAPSHOT_20250814_1315.md`
- `PROJECT_HUB/MOJO_HYBRID_REALISTIC_APPROACH_20250814_1345.md`
- `PROJECT_HUB/MOJO_INTEGRATION_IMPACT_20250814_1340.md`

## 13) Changelog (diese Änderung)
- Add: `src_hexagonal/adapters/mojo_kernels_adapter.py`
- Add: `src_hexagonal/mojo_kernels.py`
- Edit: `src_hexagonal/hexagonal_api_enhanced.py` (Health-Mojo-Block, `GET /api/mojo/status`, optionaler Bulk-Precheck)

## 14) Anhang
Regex für Fakt-Validierung (Server & Stub):
```
^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.\s*$
```
PowerShell-Beispiele:
```powershell
# Status prüfen
Invoke-RestMethod -Uri http://127.0.0.1:5001/health | ConvertTo-Json -Depth 5
Invoke-RestMethod -Uri http://127.0.0.1:5001/api/mojo/status | ConvertTo-Json -Depth 5
# Flag setzen + Neustart
$env:MOJO_ENABLED="true"
$env:PYTHONPATH="D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal;$env:PYTHONPATH"
.\start_native.bat
```
