#!/usr/bin/env python3
"""
HAK_GAL MCP Server - SQLite Version for Claude Desktop Integration
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
    """MCP Server for HAK_GAL Knowledge Base - SQLite Edition"""
    
    def __init__(self):
        # Legacy JSONL path (kept for compatibility)
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
        
        # SQLite KB detection - PRIMARY data source
        sqlite_env = os.environ.get("HAKGAL_SQLITE_DB_PATH", "").strip()
        default_sqlite = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        
        if sqlite_env:
            self.sqlite_db_path = Path(sqlite_env)
        elif default_sqlite.exists():
            self.sqlite_db_path = default_sqlite
        else:
            self.sqlite_db_path = default_sqlite  # Use default even if not exists yet
            
        self.use_sqlite = True  # ALWAYS use SQLite
        
        # Initialize SQLite DB if not exists
        self._init_sqlite_db()

    def _init_sqlite_db(self):
        """Initialize SQLite database with proper schema"""
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
                logger.info(f"SQLite DB initialized: {self.sqlite_db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite DB: {e}")

    def _yield_statements(self, limit=None):
        """Generator that yields statements from SQLite DB"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    yield row[0]
        except Exception as e:
            logger.error(f"Error reading from SQLite: {e}")
            return

    def _get_all_statements(self):
        """Get all statements from SQLite as a list"""
        statements = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                statements = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error getting all statements: {e}")
        return statements

    def _get_fact_objects(self, limit=None):
        """Get full fact objects from SQLite"""
        facts = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement, source, confidence, timestamp, tags FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    statement, source, confidence, timestamp, tags = row
                    fact = {
                        "statement": statement,
                        "source": source or "unknown",
                        "confidence": confidence or 1.0,
                        "timestamp": timestamp or time.time()
                    }
                    if tags:
                        try:
                            fact["tags"] = json.loads(tags) if isinstance(tags, str) else tags
                        except:
                            fact["tags"] = []
                    facts.append(fact)
        except Exception as e:
            logger.error(f"Error getting fact objects: {e}")
        return facts

    def _count_facts(self):
        """Count total facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                return cursor.fetchone()[0]
        except Exception:
            return 0

    def _is_write_allowed(self, provided_token: str) -> bool:
        """Return True if write ops are permitted"""
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
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = {"ts": ts, "action": action, "payload": payload}
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _parse_statement(self, statement: str):
        try:
            l = statement.find("(")
            r = statement.rfind(")")
            if l == -1 or r == -1 or r <= l:
                return None, []
            predicate = statement[:l].strip()
            inner = statement[l+1:r]
            args = [part.strip() for part in inner.split(",") if part.strip()]
            return predicate, args
        except Exception:
            return None, []
        
    async def send_response(self, response):
        """Send JSON-RPC response"""
        response_str = json.dumps(response)
        sys.stdout.write(response_str + "\n")
        sys.stdout.flush()
        logger.debug(f"Sent: {response_str[:200]}")
        
    async def handle_initialize(self, request):
        """Handle initialization request"""
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    "tools": {"listChanged": True},
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "HAK_GAL MCP (SQLite)",
                    "version": "2.0.0"
                }
            }
        }
        await self.send_response(response)
    
    async def handle_list_tools(self, request):
        """List available tools (MCP)"""
        tools = [
            {
                "name": "search_knowledge",
                "description": "Search the HAK_GAL knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "description": "Max results", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_system_status",
                "description": "Get HAK_GAL system status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "list_recent_facts",
                "description": "List recent facts from the knowledge base",
                "inputSchema