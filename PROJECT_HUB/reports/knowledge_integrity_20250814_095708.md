# Knowledge Integrity Report — 2025-08-14 09:57:16

API Base: `http://127.0.0.1:5001`

## System Status (light)
Status: <unavailable>

## Facts Count
- <unavailable>

## Top Predicates (sample)
<unavailable>

## Quality Metrics (sample)
<unavailable>

## Actionable Checks
- Ensure adapter is SQLite (writable) in status; if JSONL, write ops may be no-op.
- If invalid/duplicates/contradictions are non-zero, schedule clean-up runs and human verification.
- Track trends by comparing this report against previous days.

## Collector Notes
```
Fetch error /api/status?light=1: <urlopen error [WinError 10061] Es konnte keine Verbindung hergestellt werden, da der Zielcomputer die Verbindung verweigerte>
Fetch error /api/facts/count: <urlopen error [WinError 10061] Es konnte keine Verbindung hergestellt werden, da der Zielcomputer die Verbindung verweigerte>
Fetch error /api/predicates/top?limit=15&sample_limit=5000: <urlopen error [WinError 10061] Es konnte keine Verbindung hergestellt werden, da der Zielcomputer die Verbindung verweigerte>
Fetch error /api/quality/metrics?sample_limit=5000: <urlopen error [WinError 10061] Es konnte keine Verbindung hergestellt werden, da der Zielcomputer die Verbindung verweigerte>
```
