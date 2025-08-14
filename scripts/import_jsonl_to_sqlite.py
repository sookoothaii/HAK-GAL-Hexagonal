#!/usr/bin/env python3
"""
Import JSONL knowledge base into SQLite (idempotent, insert-or-ignore).

- Source:   HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl
- Target:   HAK_GAL_HEXAGONAL/k_assistant.db  (table: facts(statement TEXT PRIMARY KEY, context TEXT, fact_metadata TEXT))
- Behavior: Skips invalid lines, inserts unique statements, preserves context when present
- Safety:   Read-only on source, idempotent on target

Usage (Windows PowerShell):
  .\.venv_hexa\Scripts\python.exe scripts\import_jsonl_to_sqlite.py
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    src = root / "data" / "k_assistant.kb.jsonl"
    dst = root / "k_assistant.db"

    if not src.exists():
        print(f"Source not found: {src}")
        return 0

    con = sqlite3.connect(dst)
    con.execute("CREATE TABLE IF NOT EXISTS facts (statement TEXT PRIMARY KEY, context TEXT DEFAULT '{}', fact_metadata TEXT DEFAULT '{}')")
    added = 0
    bad = 0
    total = 0
    with src.open('r', encoding='utf-8') as f:
        for line in f:
            total += 1
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except Exception:
                bad += 1
                continue
            st = (obj.get('statement') or '').strip()
            if not st:
                bad += 1
                continue
            ctx = obj.get('context') or {}
            try:
                cur = con.execute(
                    "INSERT OR IGNORE INTO facts(statement, context, fact_metadata) VALUES (?, json(?), '{}')",
                    (st, json.dumps(ctx, ensure_ascii=False))
                )
                added += cur.rowcount or 0
            except Exception:
                bad += 1
                continue
    con.commit(); con.close()
    print(f"Total: {total}  Added: {added}  Bad: {bad}")
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
