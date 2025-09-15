---
title: "Auto Health Report 5002 Latest"
created: "2025-09-15T00:08:01.078169Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# AUTO HEALTH REPORT — 5002 (Mojo) — LATEST

Quelle: Live-Checks aus aktiver `.venv_hexa` (PowerShell HTTP Requests)

## Health
```json
{
  "architecture": "hexagonal",
  "mojo": { "available": true, "backend": "mojo_kernels", "flag_enabled": true },
  "port": 5001,
  "repository": "SQLiteFactRepository",
  "status": "operational"
}
```

## Flags
```json
{
  "adapter": { "available": true, "flag_enabled": true },
  "env": { "MOJO_DUPES_ENABLED": "true", "MOJO_ENABLED": "true", "MOJO_VALIDATE_ENABLED": "true" }
}
```

## Facts Count
```json
{ "count": 3879, "ttl_sec": 30 }
```

## Golden (limit=5000, threshold=0.95)
```json
{
  "adapters": {
    "mojo": { "available": true, "backend": "mojo_kernels", "flag_enabled": true },
    "python": { "available": false, "backend": "python_fallback", "flag_enabled": false }
  },
  "duplicates": { "pairs_mojo": 104, "pairs_python": 104, "sample": 2000, "threshold": 0.95 },
  "validate": { "total": 3879, "mismatches": 0 }
}
```

## Bench (limit=5000, threshold=0.95)
```json
{
  "adapter": { "available": true, "backend": "mojo_kernels", "flag_enabled": true },
  "validate": { "duration_ms": 1.0233, "valid_true": 3874, "valid_false": 5 },
  "duplicates": { "checked_sample": 2000, "pairs": 104, "threshold": 0.95, "duration_ms": 767.8485 }
}
```

## Kurzfazit
- 5002 ist erreichbar (200) und Mojo ist aktiv (available=true, flag_enabled=true)
- Golden: 0 Mismatches; Dupe-Paare identisch (52 vs 52)
- Bench: ~170 ms für Duplikate auf 1000er Sample; Validation 100% true


