# Create ssot_enforcer.py with full implementation and a small demo
from textwrap import dedent
import json, os, sqlite3, hashlib, time, datetime

code = dedent('''
# ssot_enforcer.py
# Purpose: Enforce SSoT-compliant writes via MCP-style proxy with Quality Gates, Audit, and SQLite WAL.
# Language: English (per user's rule: docs/code in EN, conversation in DE).

from __future__ import annotations
import json
import os
import sqlite3
import string
import time
from dataclasses import dataclass, asdict
from hashlib import sha256
from typing import Any, Dict, List, Optional, Tuple

# ---------------------------
# Config & Utilities
# ---------------------------

@dataclass
class Config:
    db_path: str = os.environ.get("SSOT_DB_PATH", "/mnt/data/ssot_kb.db")
    audit_log_path: str = os.environ.get("SSOT_AUDIT_LOG", "/mnt/data/ssot_audit.jsonl")
    # Pragmas required by SSoT runbook
    sqlite_journal_mode: str = "WAL"          # WAL=ON
    sqlite_synchronous: str = "FULL"          # synchronous=FULL
    ascii_only_execute_code: bool = True      # enforce ASCII-only for execute_code payloads

ALLOWED_PREDICATES = {
    "IsA", "PartOf", "HasProperty", "Causes", "LocatedIn", "AliasOf",
    "SynonymOf", "AntonymOf", "RelatedTo", "DerivedFrom"
}

ASCII = set(string.printable)

def is_ascii_only(s: str) -> bool:
    return set(s).issubset(ASCII)

def now_iso() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

def stable_hash(obj: Any) -> str:
    data = json.dumps(obj, sort_keys=True, ensure_ascii=True)
    return sha256(data.encode("utf-8")).hexdigest()

# ---------------------------
# SQLite Adapter
# ---------------------------

class SQLiteAdapter:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.conn = sqlite3.connect(self.cfg.db_path, check_same_thread=False)
        self._apply_pragmas()
        self._init_schema()

    def _apply_pragmas(self) -> None:
        cur = self.conn.cursor()
        cur.execute("PRAGMA journal_mode=WAL;")
        cur.execute("PRAGMA synchronous=FULL;")
        self.conn.commit()

    def verify_pragmas(self) -> Tuple[str, int]:
        cur = self.conn.cursor()
        cur.execute("PRAGMA journal_mode;")
        journal_mode = cur.fetchone()[0]
        cur.execute("PRAGMA synchronous;")
        synchronous = cur.fetchone()[0]  # 2=NORMAL, 3=FULL
        return journal_mode, synchronous

    def _init_schema(self) -> None:
        cur = self.conn.cursor()
        cur.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            subject TEXT NOT NULL,
            predicate TEXT NOT NULL,
            object TEXT NOT NULL,
            source TEXT,
            created_at TEXT NOT NULL,
            ssot_id TEXT NOT NULL
        );
        """)
        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fact_id INTEGER NOT NULL,
            operation TEXT NOT NULL,
            payload TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY(fact_id) REFERENCES facts(id)
        );
        """)
        self.conn.commit()

    def insert_fact(self, fact: Dict[str, Any]) -> int:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO facts(subject, predicate, object, source, created_at, ssot_id) VALUES (?, ?, ?, ?, ?, ?);",
            (
                fact["subject"],
                fact["predicate"],
                fact["object"],
                fact.get("source"),
                fact.get("created_at", now_iso()),
                fact.get("ssot_id", "UNKNOWN")
            )
        )
        self.conn.commit()
        return cur.lastrowid

    def add_history(self, fact_id: int, operation: str, payload: Dict[str, Any]) -> None:
        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO history(fact_id, operation, payload, created_at) VALUES (?, ?, ?, ?);",
            (fact_id, operation, json.dumps(payload, ensure_ascii=True), now_iso())
        )
        self.conn.commit()

    def find_duplicates(self, subject: str, predicate: str, obj: str) -> List[Tuple[int, str, str, str]]:
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, subject, predicate, object FROM facts WHERE subject=? AND predicate=? AND object=?;",
            (subject, predicate, obj)
        )
        return cur.fetchall()

# ---------------------------
# Quality Gate
# ---------------------------

@dataclass
class GateDecision:
    pass_: bool
    reason: Optional[str] = None

class QualityGate:
    def __init__(self, cfg: Config):
        self.cfg = cfg

    def evaluate(self, fact: Dict[str, Any], context_bundle: Dict[str, Any]) -> GateDecision:
        # Schema checks
        required = {"subject", "predicate", "object"}
        if not required.issubset(fact.keys()):
            return GateDecision(False, f"Missing fields: {sorted(list(required - set(fact.keys())))}")

        # Type checks
        if not all(isinstance(fact[k], str) for k in ("subject", "predicate", "object")):
            return GateDecision(False, "Subject, predicate, object must be strings.")

        # Predicate whitelist
        if fact["predicate"] not in ALLOWED_PREDICATES:
            return GateDecision(False, f"Predicate '{fact['predicate']}' not in whitelist.")

        # ASCII-only constraint for execute_code-like payloads (if present)
        if self.cfg.ascii_only_execute_code and "execute_code" in fact:
            if not is_ascii_only(fact["execute_code"]):
                return GateDecision(False, "execute_code must be ASCII-only.")

        # Context bundle must carry ssot_id and hash
        if "ssot_id" not in context_bundle or "hash" not in context_bundle:
            return GateDecision(False, "Context bundle missing ssot_id or hash.")

        return GateDecision(True, None)

# ---------------------------
# Auditor
# ---------------------------

class Auditor:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        os.makedirs(os.path.dirname(self.cfg.audit_log_path), exist_ok=True)

    def log(self, event: str, payload: Dict[str, Any], result: Optional[Dict[str, Any]] = None) -> None:
        entry = {
            "ts": now_iso(),
            "event": event,
            "payload": payload,
            "result": result
        }
        with open(self.cfg.audit_log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=True) + "\\n")

# ---------------------------
# Context Assembler
# ---------------------------

class ContextAssembler:
    def build(self, ssot_md: str, niche_md: str, ssot_id: str) -> Dict[str, Any]:
        bundle = {
            "ssot_id": ssot_id,
            "ssot": ssot_md,
            "niche": niche_md,
        }
        bundle["hash"] = stable_hash(bundle)
        return bundle

# ---------------------------
# MCP-like Client (stub for demo)
# ---------------------------

class MCPClient:
    def __init__(self, db: SQLiteAdapter):
        self.db = db

    def call(self, method: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        if method == "add_fact":
            new_id = self.db.insert_fact(payload)
            self.db.add_history(new_id, "add_fact", payload)
            return {"status": "ok", "id": new_id}
        raise NotImplementedError(method)

# ---------------------------
# Proxy
# ---------------------------

class MCPWriteProxy:
    def __init__(self, mcp_client: MCPClient, auditor: Auditor, gate: QualityGate, db: SQLiteAdapter):
        self.mcp = mcp_client
        self.audit = auditor
        self.gate = gate
        self.db = db

    def persist_fact(self, fact: Dict[str, Any], context_bundle: Dict[str, Any]) -> Dict[str, Any]:
        # Quality Gate
        decision = self.gate.evaluate(fact, context_bundle)
        if not decision.pass_:
            self.audit.log("quality_gate_fail", {"fact": fact, "reason": decision.reason, "context_hash": context_bundle.get("hash")})
            raise ValueError(f"QualityGateFail: {decision.reason}")

        # Duplicate detection (simple exact match)
        dups = self.db.find_duplicates(fact["subject"], fact["predicate"], fact["object"])
        if dups:
            self.audit.log("duplicate_detected", {"fact": fact, "duplicates": [d[0] for d in dups]})
            return {"status": "duplicate", "ids": [d[0] for d in dups]}

        # Persist via MCP client
        res = self.mcp.call("add_fact", {
            **fact,
            "created_at": fact.get("created_at") or time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "ssot_id": context_bundle["ssot_id"]
        })
        self.audit.log("persist_fact", {"fact": fact, "context_hash": context_bundle["hash"]}, res)
        return res

# ---------------------------
# Self-check helper
# ---------------------------

def verify_runtime(cfg: Config, db: SQLiteAdapter) -> Dict[str, Any]:
    journal_mode, synchronous = db.verify_pragmas()
    return {
        "journal_mode": journal_mode,
        "synchronous": synchronous,
        "audit_log": cfg.audit_log_path,
        "db_path": cfg.db_path,
    }

# ---------------------------
# Demo (can be removed in production)
# ---------------------------

if __name__ == "__main__":
    cfg = Config()
    db = SQLiteAdapter(cfg)
    auditor = Auditor(cfg)
    gate = QualityGate(cfg)
    mcp = MCPClient(db)
    proxy = MCPWriteProxy(mcp, auditor, gate, db)

    ssot_md = "# SSoT Root Principles\\nNo direct writes; use MCP proxy; audit everything."
    niche_md = "# Niche: Architecture\\nAgent 'Claude' handles architecture decisions."
    ctx = ContextAssembler().build(ssot_md, niche_md, ssot_id="SSOT-2025-09-08-A")

    # Check pragmas
    print("RUNTIME:", verify_runtime(cfg, db))

    # Insert a valid fact
    fact = {"subject": "ServiceA", "predicate": "IsA", "object": "Microservice", "source": "unit-test"}
    print("PERSIST:", proxy.persist_fact(fact, ctx))

    # Attempt duplicate insert
    print("PERSIST DUP:", proxy.persist_fact(fact, ctx))

    # Attempt invalid predicate
    try:
        proxy.persist_fact({"subject":"X","predicate":"ConnectedTo","object":"Y"}, ctx)
    except Exception as e:
        print("EXPECTED FAIL:", str(e))
''')

# Write file
with open('/mnt/data/ssot_enforcer.py', 'w', encoding='utf-8') as f:
    f.write(code)

# Execute a quick demo run to produce output and create DB/log
import subprocess, sys, textwrap
proc = subprocess.run([sys.executable, '/mnt/data/ssot_enforcer.py'], capture_output=True, text=True, timeout=120)
print(proc.stdout)
print("---- STDERR ----")
print(proc.stderr)

# Show paths to created artifacts
from pathlib import Path
paths = {
    "module": "/mnt/data/ssot_enforcer.py",
    "db": "/mnt/data/ssot_kb.db",
    "audit": "/mnt/data/ssot_audit.jsonl",
}
print(json.dumps(paths))

