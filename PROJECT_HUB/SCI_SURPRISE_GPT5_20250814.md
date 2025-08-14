# Wissenschaftliches Überraschungsei (GPT‑5) — Risikofreie Wissensexpansion

Datum: 2025‑08‑14
Autor: GPT‑5

## Idee
Beschleunigte, aber strikt verfassungskonforme Wissensexpansion durch zwei sichere Bausteine:
- Tages‑Integritätsreport (read‑only)
- Themen→Kandidaten→Review Pipeline (read‑only bis Freigabe)

Kein Systemrisiko: Keine stillen Backend‑Änderungen, alle Schritte sind reversibel und transparent.

## Neue Bausteine
- `scripts/generate_integrity_report.py`
  - Liefert Qualitäts-/Statusbericht nach `PROJECT_HUB/reports/knowledge_integrity_<ts>.md`.
- `scripts/auto_topics_from_kb.py`
  - Extrahiert Top‑Entitäten aus aktuellen Fakten, schreibt `PROJECT_HUB/topics.txt`.
- `scripts/generate_candidates_from_topics.py`
  - Baut aus `topics.txt` eine Kandidaten‑Checkliste `PROJECT_HUB/reports/candidates_<ts>.md`.
- `scripts/curated_candidate_pipeline.ps1`
  - Orchestriert Topics→Candidates mit einem Befehl, ohne KB zu beschreiben.

## Why it matters
- Forschungstempo: Mehr valide Kandidaten in kürzerer Zeit, Human‑in‑the‑Loop bleibt zentral.
- Qualität: Reports, Regex‑Validierung, optionaler Confidence‑Gate vor endgültigem Insert.
- Reproduzierbarkeit: Alle Outputs im Hub versioniert.

## Mini‑Runbook
1) Integritätsreport (optional täglich)
```powershell
.\.venv_hexa\Scripts\python.exe scripts\generate_integrity_report.py
```
2) Kuratierte Kandidaten
```powershell
# erzeugt topics.txt und candidates_<ts>.md
powershell -ExecutionPolicy Bypass -File .\scripts\curated_candidate_pipeline.ps1 -Limit 5000
```
3) Review & Freigabe
- Datei `PROJECT_HUB/reports/candidates_<ts>.md` öffnen
- Validierte Fakten per MCP/REST eintragen:
```powershell
# Beispiel REST Insert (mit Kontext)
$fact = 'HasProperty(QuantumComputer, Superposition).'
$ctx = @{ source = 'human_verified' } | ConvertTo-Json
Invoke-RestMethod -Method Post -Uri http://127.0.0.1:5001/api/facts -ContentType 'application/json' -Body (@{statement=$fact; context=$ctx} | ConvertTo-Json)
```

## Optional (Qualitätstor)
- ENV: `AETHELRED_STRICT_CONFIDENCE=0.80` → Engine nimmt nur Fakten mit Confidence ≥ 0.8.

## Nächste Schritte
- KPI‑Tracking im Report um „Fakten/Tag“ erweitern (Audit‑basiert)
- Candidate‑Review‑UI (leichtgewichtige Web‑Ansicht) für Bulk‑Approve

— Ende —
