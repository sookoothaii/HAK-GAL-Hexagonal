# AUTO HEALTH REPORT — 5001 (Standard/Python) — LATEST

Quelle: Live-Checks aus aktiver `.venv_hexa` (PowerShell HTTP Requests)

## Health
```json
{
  "architecture": "hexagonal",
  "mojo": { "available": false, "backend": "python_fallback", "flag_enabled": false },
  "port": 5001,
  "repository": "SQLiteFactRepository",
  "status": "operational"
}
```

## Facts Count
```json
{ "cached": false, "count": 3879, "ttl_sec": 30 }
```

## Mojo Flags
```json
{
  "adapter": { "available": false, "backend": "python_fallback", "flag_enabled": false },
  "env": { "MOJO_ENABLED": null, "MOJO_VALIDATE_ENABLED": null }
}
```

## Golden (limit=1000, threshold=0.95)
```json
{
  "adapters": {
    "mojo": { "available": false, "backend": "python_fallback", "flag_enabled": false },
    "python": { "available": false, "backend": "python_fallback", "flag_enabled": false }
  },
  "duplicates": { "pairs_mojo": 52, "pairs_python": 52, "sample": 1000, "threshold": 0.95 },
  "validate": { "mismatch_indices_preview": [], "total": 1000 }
}
```

## Bench (limit=1000, threshold=0.95)
```json
{
  "adapter": { "available": false, "backend": "python_fallback", "flag_enabled": false },
  "validate": { "duration_ms": 0.0, "valid_true": 1000, "valid_false": 0 },
  "duplicates": { "checked_sample": 1000, "pairs": 52, "threshold": 0.95, "duration_ms": 194.0863 }
}
```

## Kurzfazit
- 5001 ist erreichbar (200), läuft ohne Mojo (reiner Python-Pfad)
- Golden: identische Dupe-Paare (52/52) auf 1000er Sample; Validate total=1000
- Bench: ~194 ms für Duplikate (Sample 1000); Validation 100% true


