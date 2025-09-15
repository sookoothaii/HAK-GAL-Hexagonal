---
title: "Technical Report Latest"
created: "2025-09-15T00:08:01.128141Z"
author: "system-cleanup"
topics: ["technical_reports"]
tags: ["auto-generated"]
privacy: "internal"
summary_200: |-
  Auto-generated frontmatter. Document requires review.
---

# Technical Report — HAK_GAL_HEXAGONAL (LATEST)

## Summary
- Backends: 5001 (Standard, write), 5002 (Mojo, read-only)
- Architecture: Hexagonal (REST, WS, Governor, Kill-Switch)
- Mojo: native pybind11 module built and loaded (backend=mojo_kernels)
- Validation parity: Golden zuvor 0 mismatches (Python vs Mojo)
- Packaging: CMake + pybind11 konfiguriert; Build-Skripte vorhanden; Wheel-Pfad vorbereitet

## Backend Topology
- 5001: Flask REST, SQLiteFactRepository, WebSocket, Governor (write-enabled)
- 5002: gleiche API + Mojo-Adapter (read-only), Feature-Flags (MOJO_ENABLED/VALIDATE/DUPES)

## Live Data (soeben erhoben)
- 5001 /health:
{
  "architecture": "hexagonal",
  "mojo": {"available": true, "backend": "mojo_kernels", "flag_enabled": true},
  "port": 5001,
  "repository": "SQLiteFactRepository",
  "status": "operational"
}

- 5001 /api/facts/count:
{ "cached": false, "count": 3879, "ttl_sec": 30 }

- 5002 /health:
{
  "architecture": "hexagonal",
  "mojo": {"available": true, "backend": "mojo_kernels", "flag_enabled": true},
  "port": 5002,
  "repository": "SQLiteFactRepository",
  "status": "operational"
}

- 5002 /api/mojo/status:
{ "mojo": { "available": true, "backend": "mojo_kernels", "flag_enabled": true, "present": true } }

- 5002 /api/mojo/bench (limit=1000, threshold=0.95):
{
  "adapter": {"available": true, "backend": "mojo_kernels", "flag_enabled": true},
  "validate": {"duration_ms": 0.0, "valid_true": 1000, "valid_false": 0},
  "duplicates": {"checked_sample": 1000, "pairs": 52, "threshold": 0.95, "duration_ms": 191.16544723510742}
}

## Key Endpoints
- Health: /health
- Facts: /api/facts, /api/facts/count, /api/facts/paginated, /api/facts/export
- Mojo: /api/mojo/status, /api/mojo/flags (GET/POST), /api/mojo/golden, /api/mojo/bench
- Analysis: /api/analysis/duplicates, /api/analysis/similarity-top (neu)

## Packaging / Build
- Native module: native/mojo_kernels/build/Release/mojo_kernels.cp311-win_amd64.pyd
- CMake target: hakgal_mojo_kernels (OUTPUT_NAME=mojo_kernels)
- Build-Skripte: scripts/build_mojo_native.ps1 | .bat | .sh

## Operations
- 5002 ist read-only (Kill-Switch + ENV), sicher parallel zu 5001
- Flags erlauben schnellen Rollback zum Python-Fallback
