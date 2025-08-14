# SQLite Migration Plan — HAK_GAL_HEXAGONAL (GPT‑5)

Datum: 2025‑08‑14
Autor: GPT‑5
Ziel: Saubere Portierung der laufenden Faktengenerierung von JSONL auf SQLite als „Source of Truth“ (SoT), bei gleichzeitiger Wahrung von Datenintegrität, Reproduzierbarkeit und Ausfallsicherheit.

---

## 1. Ausgangslage und Zielbild
- Status quo:
  - Neue Fakten werden aktuell sehr wahrscheinlich in `data/k_assistant.kb.jsonl` geschrieben.
  - SQLite (`k_assistant.db`) existiert, wird aber nicht als primäre Schreibquelle verwendet.
- Zielbild:
  - SQLite ist alleinige SoT (Schreiben/Lesen).
  - JSONL wird nur noch als Export/Archiv genutzt.
  - Alle Endpunkte (`/api/facts*`) arbeiten gegen SQLite und unterstützen Delete/Update robust.

---

## 2. Sicherheitsnetz (Backups & Snapshots)
1) Full Backup mit GUI/CLI (empfohlen vor jeder Änderung):
```powershell
# GUI
powershell -ExecutionPolicy Bypass -File .\scripts\Backup-HAK_GAL_HEXAGONAL.ps1

# Headless (Beispiel)
powershell -ExecutionPolicy Bypass -File .\scripts\Backup-HAK_GAL_HEXAGONAL.ps1 -Destination "D:\Backups" -Mode Full -Compression Optimal -Silent
```
2) Project Hub Snapshot (für reproducible state):
- Erzeuge aktuellen Snapshot über MCP (`project_snapshot`) oder manuell.

---

## 3. Verifikation des aktuellen Repository‑Typs
- Voller Status (zeigt `repository_type`):
```powershell
Invoke-WebRequest -UseBasicParsing http://127.0.0.1:5001/api/status | Select -Expand Content
```
- Delete/Update‑Tests (wirksam nur mit SQLite):
```powershell
# Add
$body = @{ statement = 'TestFact(MigrationProbe, Hexa).' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5001/api/facts -ContentType 'application/json' -Body $body
# Update
$body = @{ old_statement='TestFact(MigrationProbe, Hexa).'; new_statement='TestFact(MigrationProbeNeu, Hexa).' } | ConvertTo-Json
Invoke-RestMethod -Method Put -Uri http://127.0.0.1:5001/api/facts/update -ContentType 'application/json' -Body $body
# Delete
$body = @{ statement = 'TestFact(MigrationProbeNeu, Hexa).' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5001/api/facts/delete -ContentType 'application/json' -Body $body
```
- Interpretation:
  - `repository_type = SQLiteFactRepository` und `removed/updated > 0` → SQLite aktiv.
  - `repository_type = JsonlFactRepository` oder `removed/updated = 0` → JSONL aktiv.

---

## 4. Umschalten der API auf SQLite (Minimal‑invasiv)
- Datei: `src_hexagonal/hexagonal_api_enhanced.py`
- Aktuell: Bei `use_legacy=False` wird zuerst `JsonlFactRepository()` gewählt, Fallback SQLite.
- Ziel: Reihenfolge umdrehen → zuerst `SQLiteFactRepository()` als primäres Repo. JSONL nur optional als Exportpfad.

Vorgeschlagene Änderung (semantisch):
- Im `__init__`‑Zweig `use_legacy=False`:
  1) Versuche `SQLiteFactRepository()`
  2) Optional: Wenn SQLite nicht verfügbar, fallback auf `JsonlFactRepository()` (nur Lesemodus/Übergang)
- Sicherstellen, dass `/api/status` das korrekte `repository_type` ausgibt (bereits durch `FactManagementService.get_system_status()` gegeben).

Rollout‑Schritte:
1) Backend stoppen
2) Änderung einspielen
3) Backend starten
4) Verifikation (Kapitel 3)

---

## 5. Migration bestehender JSONL‑Fakten nach SQLite
- Quelle: `data/k_assistant.kb.jsonl`
- Ziel: `k_assistant.db` (Tabelle `facts`)
- Vorgehen:
  1) Read‑only dry‑run: Zähle Zeilen in JSONL und entscheide Umfang.
  2) Import‑Script (falls vorhanden: `import_jsonl_to_sqlite.py`) oder ad‑hoc Python: Jede Zeile parsen → `statement` + `context` → Insert in SQLite (mit `INSERT OR IGNORE`).
  3) Deduplizieren: SQLite hält `statement` als PRIMARY KEY; Duplikate werden automatisch ignoriert.
  4) Validieren: Counts & Stichproben (siehe Kapitel 7).

Beispiel (ad‑hoc Python‑Skizze):
```python
import json, sqlite3
from pathlib import Path
root = Path('HAK_GAL_HEXAGONAL')
jsonl = root/'data/k_assistant.kb.jsonl'
db = root/'k_assistant.db'
con = sqlite3.connect(db)
con.execute("CREATE TABLE IF NOT EXISTS facts (statement TEXT PRIMARY KEY, context TEXT DEFAULT '{}', fact_metadata TEXT DEFAULT '{}')")
added=0
with open(jsonl, 'r', encoding='utf-8') as f:
    for line in f:
        line=line.strip()
        if not line: continue
        try:
            obj=json.loads(line)
        except: continue
        st=obj.get('statement'); ctx=obj.get('context') or {}
        if not st: continue
        try:
            con.execute('INSERT OR IGNORE INTO facts(statement, context, fact_metadata) VALUES (?, ?, ?)', (st, json.dumps(ctx, ensure_ascii=False), '{}'))
            added+=con.total_changes
        except: pass
con.commit(); con.close(); print('added', added)
```

---

## 6. Guardrails & Policies (Qualität sichern)
- Write‑Gate optional aktivieren:
  - Nur Statements zulassen, die Regex erfüllen: `^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$`
  - Optionaler Reasoning‑Gate vor Insert (Confidence ≥ 0.8), z. B. via `/api/reason` (aktivierbar per ENV in Engine‑Pfaden).
- Delete/Update sicherstellen (SQLite aktiv!), JSONL nicht mehr als Backend verwenden.
- CORS: Prod‑Whitelist via ENV.

---

## 7. Post‑Migration Validierung
1) Integritätsreport (read‑only):
```powershell
.\.venv_hexa\Scripts\python.exe scripts\generate_integrity_report.py
```
- Prüfen: `total`, `invalid`, `duplicates`, `isolated`, `contradictions` und `top_predicates`.

2) Stichproben (manuell):
- `/api/facts?limit=100` sichten.
- Suche `/api/search` nach repräsentativen Entitäten/Prädikaten.

3) Delete/Update erneut testen (Kapitel 3) – muss >0 liefern.

---

## 8. Rollout & Betrieb
- Rolloutplan (Low‑Risk):
  1) Backup/Snapshot
  2) API‑Umschaltung auf SQLite
  3) Import JSONL → SQLite
  4) Smoke‑Tests (Add/Update/Delete, Suche)
  5) Integritätsreport generieren
  6) Monitoring einschalten (nightly Trends)

- Betrieb:
  - SQLite als SoT weiter pflegen (optional `VACUUM/ANALYZE` monatlich).
  - JSONL bei Bedarf als Export generieren (nicht mehr als Backend‑Quelle verwenden).

---

## 9. Monitoring & Trends
- Nightly Report: `PROJECT_HUB/reports/knowledge_integrity_YYYYMMDD_HHMMSS.md`
- KPIs:
  - facts total, invalid/duplicates/isolated/contradictions
  - top predicates (Stabilität der Verteilungen)
  - Insert‑Rate (Fakten/Tag) aus Audits (optional)

---

## 10. Risiken & Gegenmaßnahmen
- Risiko: Alte Pfade schreiben weiterhin nach JSONL → Gegenmaßnahme: API auf SQLite hart umstellen, `/api/status` regelmäßig prüfen.
- Risiko: Stille No‑Ops bei JSONL (Delete/Update) → Gegenmaßnahme: JSONL nicht als Backend zulassen; 501 bei fehlenden Repo‑Methoden.
- Risiko: Formatfehler in Kandidaten → Gegenmaßnahme: Server‑Regex, optional Reasoning‑Gate.

---

## 11. Zeitplan (Vorschlag)
- Tag 0 (heute): Backup + Snapshots, API‑Umschaltung, Import, Smoke‑Tests (2–3 h)
- Tag 1–3: Monitoring & Feintuning, Confidence‑Gate optional aktivieren
- Woche 1: JSONL vollständig in Export‑Modus; Docs angleichen; Nightly Trends beobachten

---

## 12. Abschluss
Mit diesem Plan wird die Faktengenerierung verlustfrei und reversibel auf SQLite konsolidiert. Delete/Update funktionieren zuverlässig, Abfragen sind performant, und die Qualität bleibt durch Guardrails, Reports und Monitoring abgesichert. JSONL bleibt als Export/Archiv verfügbar, ohne operative Pfade zu stören.
