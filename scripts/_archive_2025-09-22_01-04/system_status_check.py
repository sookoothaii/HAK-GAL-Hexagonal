#!/usr/bin/env python3
"""
System Status Check for HAK_GAL_HEXAGONAL (safe)
- Reads /api/status, /api/facts/count, /api/quality/metrics
- Prints concise summary

Usage:
  .\.venv_hexa\Scripts\python.exe scripts\system_status_check.py
"""
from __future__ import annotations

import os
import json
from urllib.request import urlopen, Request

BASE = os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001")


def get(path: str):
    try:
        with urlopen(Request(BASE + path)) as r:
            return json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def main() -> int:
    status = get("/api/status")
    count = get("/api/facts/count")
    quality = get("/api/quality/metrics?sample_limit=5000")

    print("=== HEXAGONAL SYSTEM STATUS ===")
    print(json.dumps(status, indent=2))
    print("\n=== FACTS COUNT ===")
    print(json.dumps(count, indent=2))
    print("\n=== QUALITY (sample) ===")
    print(json.dumps(quality, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
