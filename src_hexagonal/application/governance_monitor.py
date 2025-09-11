#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Governance Monitor (for Pragmatic Governance v3)
Author: HAK/GAL Team
Purpose:
  - Monitor SQLite DB health for Governance V3.
  - Detect duplicate facts in facts_extended.statement.
  - Optionally tail audit JSONL for governance decisions.
  - Produce concise console reports.
"""

import argparse
import contextlib
import datetime as dt
import json
import os
import sqlite3
import sys
import time
from typing import Any, Dict, List

# ---------------- Helpers ----------------

def now_iso() -> str:
    return dt.datetime.utcnow().replace(tzinfo=dt.timezone.utc).isoformat()

def file_exists(path: str) -> bool:
    return bool(path) and os.path.isfile(path)

# ---------------- SQLite Probe ----------------

def probe_sqlite(db_path: str, busy_timeout_ms: int = 5000) -> Dict[str, Any]:
    result = {
        "ok": False,
        "wal_mode": None,
        "latency_ms": None,
        "facts_count": None,
        "duplicates": [],
        "errors": []
    }

    if not file_exists(db_path):
        result["errors"].append(f"Database not found: {db_path}")
        return result

    conn = None
    try:
        conn = sqlite3.connect(
            db_path,
            timeout=busy_timeout_ms / 1000,
            isolation_level=None,
            check_same_thread=False
        )
        conn.row_factory = sqlite3.Row

        # Set busy timeout
        with contextlib.closing(conn.cursor()) as c:
            c.execute(f"PRAGMA busy_timeout = {busy_timeout_ms};")

        # Check WAL mode
        with contextlib.closing(conn.cursor()) as c:
            c.execute("PRAGMA journal_mode;")
            row = c.fetchone()
            result["wal_mode"] = row[0] if row else None

        # Probe lock acquisition latency
        start = time.perf_counter()
        locked = False
        try:
            with contextlib.closing(conn.cursor()) as c:
                c.execute("BEGIN IMMEDIATE;")
                c.execute("SELECT 1;")
        except sqlite3.OperationalError as e:
            locked = True
            result["errors"].append(f"Lock probe failed: {e}")
        finally:
            with contextlib.closing(conn.cursor()) as c:
                try:
                    c.execute("ROLLBACK;")
                except sqlite3.OperationalError:
                    pass
        end = time.perf_counter()
        result["latency_ms"] = round((end - start) * 1000, 2)

        # Count total facts
        with contextlib.closing(conn.cursor()) as c:
            try:
                c.execute("SELECT COUNT(*) FROM facts_extended;")
                result["facts_count"] = int(c.fetchone()[0])
            except sqlite3.OperationalError:
                result["errors"].append("facts_extended table missing")

        # Find duplicate facts
        with contextlib.closing(conn.cursor()) as c:
            try:
                c.execute("""
                    SELECT statement, COUNT(*) as c
                    FROM facts_extended
                    GROUP BY statement
                    HAVING COUNT(*) > 1
                    ORDER BY c DESC
                    LIMIT 20;
                """)
                result["duplicates"] = [
                    {"statement": r[0], "count": r[1]} for r in c.fetchall()
                ]
            except sqlite3.OperationalError:
                pass

        result["ok"] = not locked
    except Exception as e:
        result["errors"].append(f"probe_sqlite exception: {e}")
    finally:
        if conn:
            with contextlib.suppress(Exception):
                conn.close()

    return result

# ---------------- Audit Tail ----------------

def tail_audit(audit_path: str, max_bytes: int = 32 * 1024) -> List[Dict[str, Any]]:
    events: List[Dict[str, Any]] = []
    if not file_exists(audit_path):
        return events
    try:
        size = os.path.getsize(audit_path)
        with open(audit_path, "rb") as f:
            if size > max_bytes:
                f.seek(size - max_bytes)
                f.readline()
            for line in f:
                try:
                    events.append(json.loads(line.decode("utf-8", errors="ignore")))
                except json.JSONDecodeError:
                    continue
    except Exception as e:
        events.append({"_error": str(e)})
    return events[-20:]

# ---------------- Reporting ----------------

def summarize_probe(probe: Dict[str, Any]) -> str:
    lines = []
    lines.append("=== Governance DB Health ===")
    lines.append(f"Time (UTC): {now_iso()}")
    lines.append(f"Status: {'OK' if probe.get('ok') else 'LOCKED/ISSUE'}")
    lines.append(f"Journal Mode: {probe.get('wal_mode')}")
    if probe.get("latency_ms") is not None:
        lines.append(f"Lock Probe Latency: {probe['latency_ms']} ms")
    if probe.get("facts_count") is not None:
        lines.append(f"Facts Total: {probe['facts_count']}")
    if probe.get("duplicates"):
        lines.append(f"Duplicate Facts: {len(probe['duplicates'])} groups")
        for d in probe["duplicates"][:5]:
            lines.append(f"  - {d['count']} × {d['statement'][:100]}")
    if probe.get("errors"):
        lines.append("Errors:")
        for e in probe["errors"]:
            lines.append(f"  ! {e}")
    return "\n".join(lines)

def summarize_audit(events: List[Dict[str, Any]]) -> str:
    if not events:
        return "No recent audit events."
    lines = ["=== Recent Audit Events ==="]
    for ev in reversed(events[-10:]):
        action = ev.get("action") or ev.get("op") or "-"
        allowed = ev.get("allowed")
        risk = ev.get("risk_score")
        conf = ev.get("confidence")
        src = ev.get("source") or ev.get("ctx", {}).get("source")
        lines.append(f"{action}: allowed={allowed}, risk={risk}, conf={conf}, source={src}")
    return "\n".join(lines)

# ---------------- Main ----------------

def main():
    parser = argparse.ArgumentParser(description="Governance v3 Live Monitor")
    parser.add_argument("--db", required=True, help="Path to SQLite DB")
    parser.add_argument("--audit", help="Optional path to audit JSONL")
    parser.add_argument("--interval", type=int, default=5, help="Polling interval in seconds")
    parser.add_argument("--once", action="store_true", help="Run a single probe and exit")
    args = parser.parse_args()

    while True:
        probe = probe_sqlite(args.db)
        print(summarize_probe(probe), flush=True)
        if args.audit:
            events = tail_audit(args.audit)
            print(summarize_audit(events), flush=True)
        if args.once:
            sys.exit(0 if probe.get("ok") else 1)
        time.sleep(args.interval)

if __name__ == "__main__":
    main()