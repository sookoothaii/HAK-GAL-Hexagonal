---
title: "Report Mojo Benchmark"
created: "2025-09-15T00:08:01.057313Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Mojo Adapter Benchmark (Read-Only)

Zeitpunkt: 2025-08-14 23:25:27
API Base: http://127.0.0.1:5002
Limit: 5000

## Adapter
- flag_enabled: True
- available: True
- backend: mojo_kernels

## Ergebnisse
```
{
  "adapter": {
    "flag_enabled": true,
    "available": true,
    "backend": "mojo_kernels"
  },
  "sample_size": 3877,
  "validate": {
    "valid_true": 3872,
    "valid_false": 5,
    "duration_ms": 1.192
  },
  "duplicates": {
    "checked_sample": 2000,
    "pairs": 104,
    "duration_ms": 500.887,
    "threshold": 0.95
  }
}
```

## Hinweise
- Nur GET-Aufrufe; keine Schreiboperationen.
- Dedupe-Sample begrenzt (max 2000) zur Laufzeitbegrenzung.
