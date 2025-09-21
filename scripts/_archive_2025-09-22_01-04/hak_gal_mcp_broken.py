#!/usr/bin/env python3
"""
HAK_GAL MCP Server - Fixed Version for Claude Desktop Integration
Research Project: Making MCP work with HAK_GAL
"""

import sys
import os
import json
import asyncio
import sqlite3
import logging
from pathlib import Path
import traceback
import time
import shutil
import math
import collections
import re
import hashlib
from datetime import datetime
import fnmatch
import glob
try:
    import requests
except Exception:
    requests = None

# Setup logging (stderr for console to avoid polluting STDOUT JSON-RPC)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\mcp_server.log'),
        logging.StreamHandler(sys.stderr)
    ]
)
logger = logging.getLogger(__name__)

class HAKGALMCPServer:
    """MCP Server for HAK_GAL Knowledge Base"""
    
    def __init__(self):
        self.kb_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
        self.running = True
        self.request_id = 0
        # Harden STDIO: enforce UTF-8 and line-buffering
        try:
            if hasattr(sys.stdin, 'reconfigure'):
                sys.stdin.reconfigure(encoding='utf-8')
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, write_through=True)
        except Exception:
            # Best-effort; fall back silently
            pass
        # Write-safety configuration (env-driven)
        self.write_enabled = os.environ.get("HAKGAL_WRITE_ENABLED", "false").lower() == "true"
        self.write_token_env = os.environ.get("HAKGAL_WRITE_TOKEN", "")
        self.kb_lock_path = self.kb_path.with_suffix(self.kb_path.suffix + ".lock")
        # Project Hub automation (optional)
        self.hub_path_env = os.environ.get("HAKGAL_HUB_PATH", "")
        self.auto_snapshot_on_shutdown = os.environ.get("HAKGAL_AUTO_SNAPSHOT_ON_SHUTDOWN", "false").lower() == "true"
        self.auto_digest_on_init = os.environ.get("HAKGAL_AUTO_DIGEST_ON_INIT", "false").lower() == "true"
        # Backend API base (for SQLite-backed operations)
        self.api_base_url = os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5001")
        # SQLite KB detection (prefer sqlite if available)
        sqlite_env = os.environ.get("HAKGAL_SQLITE_DB_PATH", "").strip()
        default_sqlite = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        local_sqlite = Path("hexagonal_kb.db")
        # Hard-pin auf Projektroot-DB, falls vorhanden
        pinned_sqlite = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        if pinned_sqlite.exists():
            self.sqlite_db_path = pinned_sqlite
        elif sqlite_env:
            self.sqlite_db_path = Path(sqlite_env)
        elif default_sqlite.exists():
            self.sqlite_db_path = default_sqlite
        else:
            self.sqlite_db_path = local_sqlite
        self.use_sqlite = self.sqlite_db_path.exists()
        self._init_sqlite_db()  # Initialize SQLite DB

    
    # ========== SQLite Helper Methods ==========
    def _init_sqlite_db(self):
        """Initialize SQLite database"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        statement TEXT UNIQUE NOT NULL,
                        source TEXT,
                        confidence REAL DEFAULT 1.0,
                        timestamp REAL,
                        tags TEXT
                    )
                """)
                conn.commit()
        except Exception as e:
            logger.error(f"SQLite init error: {e}")

    def _yield_statements(self, limit=None):
        """Yield statements from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    yield row[0]
        except Exception:
            return

    def _get_all_statements(self):
        """Get all statements as list"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def _is_write_allowed(self, provided_token: str) -> bool:
        """Return True if write ops are permitted.
        Rules:
        - Requires HAKGAL_WRITE_ENABLED=true
        - If HAKGAL_WRITE_TOKEN is set:
          - accept explicit matching token, OR
          - accept empty provided_token and use server's ENV token implicitly (desktop-local convenience)
        - If no token configured, allow writes when enabled
        """
        if not self.write_enabled:
            return False
        if self.write_token_env:
            if not provided_token:
                return True
            return provided_token == self.write_token_env
        return True

    def _acquire_lock(self, timeout_seconds: int = 5):
        start = time.time()
        while True:
            try:
                fd = os.open(str(self.kb_lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.close(fd)
                return
            except FileExistsError:
                if time.time() - start > timeout_seconds:
                    raise RuntimeError("KB is locked; try again later")
                time.sleep(0.05)

    def _release_lock(self):
        try:
            if self.kb_lock_path.exists():
                try:
                    self.kb_lock_path.unlink()
                except FileNotFoundError:
                    pass
        except Exception:
            pass

    def _append_audit(self, action: str, payload: dict):
        try:
            audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
            ts = time.strftime("%Y-%