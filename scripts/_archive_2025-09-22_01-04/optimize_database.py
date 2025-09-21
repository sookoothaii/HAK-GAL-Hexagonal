#!/usr/bin/env python3
"""
Optimize SQLite database for HAK_GAL_HEXAGONAL (safe).
- Ensures table exists
- ANALYZE, VACUUM, PRAGMA optimize
- Prints basic stats before/after

Usage:
  .\.venv_hexa\Scripts\python.exe scripts\optimize_database.py
"""
from __future__ import annotations

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[1] / "k_assistant.db"

def get_count(con: sqlite3.Connection) -> int:
    try:
        cur = con.execute("SELECT COUNT(*) FROM facts")
        return int(cur.fetchone()[0])
    except Exception:
        return -1

def main() -> int:
    if not DB_PATH.exists():
        print(f"DB not found: {DB_PATH}")
        return 0
    con = sqlite3.connect(DB_PATH)
    con.execute("CREATE TABLE IF NOT EXISTS facts (statement TEXT PRIMARY KEY, context TEXT DEFAULT '{}', fact_metadata TEXT DEFAULT '{}')")
    before = get_count(con)
    print(f"Facts before: {before}")
    try:
        con.execute("ANALYZE")
    except Exception as e:
        print(f"ANALYZE warning: {e}")
    try:
        con.execute("PRAGMA optimize")
    except Exception as e:
        print(f"PRAGMA optimize warning: {e}")
    # VACUUM must be done outside transaction
    con.commit()
    try:
        con.execute("VACUUM")
    except Exception as e:
        print(f"VACUUM warning: {e}")
    after = get_count(con)
    print(f"Facts after: {after}")
    con.close()
    print("Optimization complete.")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
