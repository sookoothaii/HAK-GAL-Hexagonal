#!/usr/bin/env python3
"""
Auto-generate topics.txt from current KB facts (safe, read-only).
- Fetches up to N facts via /api/facts
- Parses statements Predicate(Entity1, Entity2).
- Ranks entities by frequency and writes PROJECT_HUB/topics.txt

Usage:
  .\.venv_hexa\Scripts\python.exe scripts\auto_topics_from_kb.py --limit 5000

Env:
  HAKGAL_API_BASE_URL (default: http://127.0.0.1:5001)
"""
from __future__ import annotations

import os
import re
import sys
import json
from pathlib import Path
from typing import Dict, Any
import argparse
import urllib.request

API_BASE = os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001")
PROJECT_ROOT = Path(__file__).resolve().parents[1]
HUB_DIR = PROJECT_ROOT / "PROJECT_HUB"
TOPICS_FILE = HUB_DIR / "topics.txt"

STMT_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*)\(([^,\)]+),\s*([^\)]+)\)\.?$")


def fetch_json(url: str, timeout: float = 20.0) -> Dict[str, Any]:
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8", errors="replace"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5000, help="Max facts to fetch")
    args = parser.parse_args()

    HUB_DIR.mkdir(parents=True, exist_ok=True)

    url = f"{API_BASE}/api/facts?limit={max(100, args.limit)}"
    try:
        data = fetch_json(url)
    except Exception as e:
        print(f"Error fetching facts: {e}")
        return 1

    facts = data.get("facts") or []
    freq: Dict[str, int] = {}

    for item in facts:
        stmt = item.get("statement") if isinstance(item, dict) else (item if isinstance(item, str) else "")
        if not stmt:
            continue
        m = STMT_RE.match(stmt.strip())
        if not m:
            continue
        _, a, b = m.groups()
        for ent in (a.strip(), b.strip()):
            if ent:
                freq[ent] = freq.get(ent, 0) + 1

    ranked = sorted(freq.items(), key=lambda kv: kv[1], reverse=True)
    topics = [name for name, _ in ranked[:300]]  # cap to 300

    if topics:
        TOPICS_FILE.write_text("\n".join(topics) + "\n", encoding="utf-8")
        print(f"Wrote {len(topics)} topics to {TOPICS_FILE}")
    else:
        print("No topics generated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
