---
title: "Be Fe Discrepancy Analysis Gpt5 20250814"
created: "2025-09-15T00:08:01.088012Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Backend–Frontend Discrepancy Analysis (GPT‑5) – Hexagonal auf Port 5001

Datum: 2025‑08‑14
Autor: GPT‑5
Scope: Tiefenanalyse von Backend (Hexagonal, Port 5001) und Frontend (5001‑basiert) mit chirurgischer Präzision. Besonderer Fokus auf SQLite vs JSONL Datenebene sowie API‑Kontrakte, Response‑Formate und potenzielle Driftursachen.

---

## Executive Summary
- Backend läuft ausschließlich auf 5001 (Hexagonal). Legacy‑Proxy (5000) wurde entfernt.
- Frontend ist konsistent auf 5001 ausgerichtet; zentrale Endpunkte werden korrekt verwendet.
- Data Layer:
  - SQLite (`k_assistant.db`) ist die aktive, schreibfähige Prod‑Datenquelle.
  - JSONL (`data/k_assistant.kb.jsonl`) existiert als alternative Quelle/Export (append‑only Implementierung).
  - Kritische Diskrepanz: Bei Nutzung des JSONL‑adapters sind Delete/Update REST‑Operationen no‑op (werden mit 200/0 beantwortet). SQLite unterstützt Delete/Update voll.
- Empfehlung: SQLite als alleinige Schreibquelle – JSONL regelmäßig aus SQLite generieren oder vollständig deprecaten. Saubere Sync‑Pipelines und Monitoring einführen.

---

## Architekturüberblick (relevant für FE/BE‑Schnittstellen)
- Framework: Flask (+ Flask‑CORS), optional Flask‑SocketIO (WebSocket), Governor & Monitoring Hooks.
- Wichtige Routen (Hex‑Enhanced Build):
  - Core: `GET /health`, `GET /api/status`, `GET /api/facts`, `POST /api/facts`, `POST /api/search`, `POST /api/reason`
  - CRUD: `POST /api/facts/delete`, `PUT /api/facts/update`
  - Analytics: `GET /api/facts/count`, `GET /api/predicates/top`, `GET /api/quality/metrics`, `GET /openapi.json`
  - LLM: `POST /api/llm/get-explanation` (nur interne Provider oder 503)
- CORS: permissiv für Dev; in Produktion Whitelist empfohlen.

---

## Frontend‑Verwendung der API (Auszug)
- Basiskonfiguration: `frontend/src/config.js`
  - `api.baseUrl = 'http://127.0.0.1:5001'`
  - Endpunkte verwendet: `/health`, `/api/status`, `/api/facts`, `/api/search`, `/api/reason`, `/api/facts/delete`, `/api/facts/update`, `/api/facts/count`, `/api/predicates/top`, `/api/quality/metrics`, `/api/llm/get-explanation`.
- Services/Seiten (repräsentativ):
  - `src/services/apiService.ts`: holt `status`, `facts`, `facts/count`, `reason`, `predicates/top` – alles konform zur Hex‑API.
  - `src/pages/ProKnowledgeStats.tsx`: nutzt `/api/facts/count`, `/api/quality/metrics`, `/api/predicates/top` – vorhanden im Backend (Enhanced Build).
  - `src/pages/ProUnifiedQuery.tsx`: nutzt `/api/reason` und `/api/llm/get-explanation`; Response‑Normalisierung auf `explanation` oder `chatResponse.natural_language_explanation`.
  - `src/components/ProNavigation.tsx`: Ping über `/api/facts/count` – vorhanden.

Bewertung: Das Frontend ist aktuell API‑konform zum Enhanced‑Backend auf 5001.

---

## LLM‑Endpoint – Vertragsabgleich
- Backend (5001):
  - `POST /api/llm/get-explanation` gibt bei Erfolg i. d. R. `{ status: 'success', explanation: string, suggested_facts: string[] }` zurück; bei nicht konfigurierten internen Providern 503 mit Fehlermeldung.
- Frontend‑Normalisierung (`ProUnifiedQuery.tsx`):
  - Bevorzugt `data.explanation`; Fallbacks auf `data.result?.explanation` oder `data.chatResponse?.natural_language_explanation` – kompatibel mit der Hex‑Form.
- Empfehlung: Für Stabilität entweder a) Backend zusätzlich einheitliches `chatResponse.natural_language_explanation` spiegeln oder b) FE‑Normalisierung beibehalten (derzeit robust).

Risiko: Ohne interne LLM‑Provider liefert Backend 503 – FE ist darauf vorbereitet (Fehlermeldung/Handling prüfen), dennoch UX‑Hinweis für klare Messaging‑Texte sinnvoll.

---

## Datenebene: SQLite vs JSONL – Tiefenanalyse

### Speicherorte & Standardpfade
- SQLite (aktiv, schreibfähig):
  - Adapter: `src_hexagonal/adapters/sqlite_adapter.py`
  - DB‑Pfad (Default): `.../HAK_GAL_HEXAGONAL/k_assistant.db`
  - Schema: Tabelle `facts(statement TEXT PRIMARY KEY, context TEXT, fact_metadata TEXT)`
- JSONL (append‑only, alternative Quelle/Export):
  - Adapter: `src_hexagonal/adapters/jsonl_adapter.py`
  - Datei: `.../HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl`
  - Format: 1 JSON‑Objekt pro Zeile mit mindestens `statement`; optional `context`, `metadata`.

### Implementierte Operationen
- SQLite:
  - `save(fact)`: INSERT OR IGNORE
  - `find_by_query(query)`: LIKE
  - `find_all(limit)`: SELECT LIMIT
  - `exists(statement)`: SELECT COUNT
  - `count()`: SELECT COUNT
  - `delete_by_statement(statement)`: DELETE WHERE
  - `update_statement(old, new)`: UPDATE WHERE
- JSONL:
  - `save(fact)`: Append (keine Duplikatsprüfung neben `exists()`)
  - `find_by_query`, `find_all`, `exists`, `count`: lineares Scannen
  - WICHTIG: Kein `delete_by_statement`, kein `update_statement` implementiert.

### Kritische Diskrepanz
- Backend‑Endpoints `/api/facts/delete` (POST) und `/api/facts/update` (PUT) prüfen zur Laufzeit via `hasattr()` ob das Repository die jeweilige Methode bereitstellt:
  - SQLite: Methoden existieren → Operationen werden ausgeführt, Status 200 und `removed/updated` > 0 möglich.
  - JSONL: Methoden fehlen → Backend antwortet 200 mit `removed: 0` bzw. `updated: 0` (no‑op). FE könnte dies als Erfolg interpretieren, obwohl keine Änderung erfolgte.

Konsequenz: Bei versehentlicher Umschaltung auf JSONL‑Adapter (oder Fallback) entstehen stille Inkonsistenzen: UI meldet „OK“, Daten bleiben unverändert. Monitoring/Alarme sollten Differenzen erkennen.

### Konsistenz & Drift‑Risiken
- Doppelte Quellen: SQLite (aktiv) und JSONL (historisch/export) können divergieren (Anzahl, Inhalt, Prädikate nach Migration).
- Unterschiedliche Validierungsregeln:
  - Backend erzwingt Punkt am Ende und Regex‑Format `Predicate(Entity1, Entity2).` – FE erzeugt teils Vorschläge aus Text via Pattern‑Match, kann Formatierungsfehler erzeugen.
- Entity/Case‑Sensitivity: LIKE‑Suche in SQLite vs Lowercase‑Vergleich in JSONL‑Adapter.

### Forensik – Schnelltests (empfohlen)
- Zählabgleich:
```
# SQLite (via API)
curl http://127.0.0.1:5001/api/facts/count

# JSONL direkt (lokal)
python - << 'PY'
import json
cnt=0
for l in open('HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl', encoding='utf-8'):
    if l.strip():
        try:
            o=json.loads(l); cnt+=1
        except: pass
print(cnt)
PY
```
- Stichproben‑Gegenprobe (Top‑Prädikate):
```
curl "http://127.0.0.1:5001/api/predicates/top?limit=10&sample_limit=5000"
```
- Delete/Update‑Wirksamkeit (stellt sicher, dass SQLite aktiv ist):
```
# Add
curl -s -X POST http://127.0.0.1:5001/api/facts -H "Content-Type: application/json" -d '{"statement":"TestFact(GPT5, Port5001)."}'
# Update
curl -s -X PUT  http://127.0.0.1:5001/api/facts/update -H "Content-Type: application/json" -d '{"old_statement":"TestFact(GPT5, Port5001).","new_statement":"TestFact(GPT5, Hexa)."}'
# Delete
curl -s -X POST http://127.0.0.1:5001/api/facts/delete -H "Content-Type: application/json" -d '{"statement":"TestFact(GPT5, Hexa)."}'
```
Erwartung: `updated`/`removed` > 0. Wenn 0, läuft JSONL‑Adapter oder Daten sind nicht vorhanden.

### Synchronisationsstrategie (empfohlen)
1. Quelle definieren: SQLite als „Source of Truth“.
2. Export‑Pipeline bauen (geplant/skriptbasiert), z. B. täglicher Export SQLite → JSONL (für Analyse/Archiv), oder JSONL vollständig deprecaten.
3. Integritätschecks:
   - Periodische Counts, Top‑Prädikate, deduplizierte Statements.
   - Reports in `PROJECT_HUB/reports/nightly_trend_YYYYMMDD.md` ergänzen.
4. Migrationsskripte nutzen (vorhanden): `import_jsonl_to_sqlite.py` (für Einmal‑Import), danach nur noch SQLite schreiben.

---

## Weitere potenzielle Diskrepanzen FE ↔ BE
- Response‑Schlüssel in `/api/status`:
  - Backend liefert `fact_count`, `repository_type`, `reasoning_available` – FE greift primär auf `/api/facts/count` zurück; keine harte Abhängigkeit auf exakte Status‑Keys erkannt.
- LLM‑Fälle ohne Provider (503):
  - FE normalisiert `explanation` sauber; 503 sollte UI‑seitig abgefangen und mit Hinweistext versehen werden (aktueller Code deutet darauf hin, bitte UX prüfen).
- Regex/Validierung:
  - Backend erzwingt Format; FE extrahiert Muster via Regex aus Freitext → Eingaben ggf. vor dem Senden säubern (abschließender Punkt, Leerzeichen nach Komma, gültiger Prädikatname).

---

## Maßnahmenplan
- Sofort (1–2 Tage):
  - „Adapter‑Wächter“: In `/api/facts/delete`/`update` bei fehlender Methode HTTP 501 zurückgeben statt 200/0 – verhindert stille No‑Ops bei JSONL.
  - Health‑Signal erweitern: `/api/status?light=1` zusätzlich `data_source: sqlite|jsonl`, `writable: true|false` ausgeben und im FE anzeigen.
  - CORS‑Whitelist für produktionsähnliche Deployments setzen.
- Kurzfristig (1–2 Wochen):
  - Export‑Pipeline SQLite → JSONL oder Deprecation von JSONL definieren.
  - Monitoring: Nightly Checks und Drift‑Berichte (Counts, Top‑Prädikate, Deduplikate) automatisieren.
- Mittelfristig:
  - Einheitliches Fact‑ID‑Konzept (falls später Non‑unique Statements benötigt werden).
  - LLM‑Provider stabilisieren (Keys via `.env`) und FE‑UX für 503‑Fälle verfeinern.

---

## Anhang A – Endpoint‑Matrix (Soll/Ist)
- Frontend verwendet alle kritischen Endpunkte der Enhanced‑API. Zusätzliche Hex‑Endpunkte (`/api/quality/metrics`, `/api/predicates/top`) sind implementiert und werden genutzt.
- Legacy‑abhängige Endpunkte/Proxys entfernt.

## Anhang B – Datenmodelle/Validierung
- SQLite `facts`:
```
statement TEXT PRIMARY KEY
context   TEXT DEFAULT '{}'
fact_metadata TEXT DEFAULT '{}'
```
- JSONL Zeile:
```
{"statement":"Predicate(A,B).","context":{...},"metadata":{...}}
```
- Backend‑Validierung Add/Command: Regex `^[A-Za-z_][A-Za-z0-9_]*\([^,\)]+,\s*[^\)]+\)\.$`

## Anhang C – Risiken & Gegenmaßnahmen
- No‑Op bei JSONL für Delete/Update → 501 erzwingen & Telemetrie.
- Daten‑Drift JSONL vs SQLite → EIN Source of Truth + Export + Monitoring.
- Falsches Format durch FE‑Extraktion → FE‑Normalisierung vor API‑Call + Server‑seitige Fehlermeldungen klar halten.

---

Verweis: Technische Migrationsdetails und Änderungen siehe `PROJECT_HUB/TECHNICAL_HANDOVER_GPT5_20250814.md`.
