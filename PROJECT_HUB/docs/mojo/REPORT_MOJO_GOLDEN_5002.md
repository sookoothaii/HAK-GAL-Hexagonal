---
title: "Report Mojo Golden 5002"
created: "2025-09-15T00:08:01.057313Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# MOJO Golden Test – Python vs Mojo (Read-Only)

Zeitpunkt: 2025-08-14 22:33:45
API Base: http://127.0.0.1:5002
Limit: 5000

## Ergebnis
```
{
  "validate": {
    "total": 3877,
    "mismatches": 0,
    "mismatch_indices_preview": []
  },
  "duplicates": {
    "sample": 2000,
    "pairs_python": 104,
    "pairs_mojo": 104,
    "only_python_preview": [],
    "only_mojo_preview": [],
    "threshold": 0.95
  },
  "adapters": {
    "python": {
      "flag_enabled": false,
      "available": false,
      "backend": "python_fallback"
    },
    "mojo": {
      "flag_enabled": true,
      "available": true,
      "backend": "mojo_kernels"
    }
  }
}
```

## Interpretation
- Ziel ist 0 Mismatches bei validate und sehr ähnliche Dupe-Pair-Sets.
- Kleinere Abweichungen bei Dedupe sind durch Gleichstand/Tokenisierung möglich – prüfen, ob akzeptabel.
