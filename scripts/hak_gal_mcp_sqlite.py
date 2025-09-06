#!/usr/bin/env python3
"""
HAK_GAL MCP Server - FULL SQLite Version (NO JSONL!)
All tools use SQLite directly - no JSONL fallback
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

# Setup logging
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
    """MCP Server for HAK_GAL Knowledge Base - SQLite Only"""
    
    def __init__(self):
        # SQLite is the ONLY backend - no JSONL!
        self.sqlite_db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        if not self.sqlite_db_path.exists():
            logger.error(f"SQLite DB not found: {self.sqlite_db_path}")
            # Create empty DB with schema
            self._init_sqlite_db()
        
        self.running = True
        self.request_id = 0
        
        # UTF-8 setup
        try:
            if hasattr(sys.stdin, 'reconfigure'):
                sys.stdin.reconfigure(encoding='utf-8')
            if hasattr(sys.stdout, 'reconfigure'):
                sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, write_through=True)
        except Exception:
            pass
        
        # Write safety
        self.write_enabled = os.environ.get("HAKGAL_WRITE_ENABLED", "false").lower() == "true"
        self.write_token_env = os.environ.get("HAKGAL_WRITE_TOKEN", "")
        
        logger.info(f"HAK_GAL SQLite MCP Server initialized")
        logger.info(f"SQLite DB: {self.sqlite_db_path} (exists: {self.sqlite_db_path.exists()})")
        logger.info(f"Write enabled: {self.write_enabled}")

    def _init_sqlite_db(self):
        """Initialize empty SQLite DB with correct schema"""
        with sqlite3.connect(str(self.sqlite_db_path)) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT NOT NULL UNIQUE,
                    context TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_statement ON facts(statement)')
            conn.commit()
        logger.info("Initialized empty SQLite DB")

    def _yield_statements(self):
        """Yield all statements from SQLite DB"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cur = conn.execute('SELECT statement FROM facts ORDER BY id')
                for row in cur:
                    yield row[0]
        except Exception as e:
            logger.error(f"Error reading from SQLite: {e}")
            return

    def _get_all_statements(self):
        """Get all statements as a list"""
        return list(self._yield_statements())

    def _count_facts(self):
        """Count facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cur = conn.execute('SELECT COUNT(*) FROM facts')
                return cur.fetchone()[0]
        except Exception:
            return 0

    def _add_fact(self, statement: str, context: dict = None):
        """Add fact to SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute(
                    'INSERT INTO facts (statement, context) VALUES (?, ?)',
                    (statement, json.dumps(context) if context else None)
                )
                conn.commit()
                return True
        except sqlite3.IntegrityError:
            return False  # Already exists
        except Exception as e:
            logger.error(f"Error adding fact: {e}")
            raise

    def _delete_fact(self, statement: str):
        """Delete fact from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cur = conn.execute('DELETE FROM facts WHERE statement = ?', (statement,))
                conn.commit()
                return cur.rowcount
        except Exception as e:
            logger.error(f"Error deleting fact: {e}")
            raise

    def _update_fact(self, old_statement: str, new_statement: str):
        """Update fact in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cur = conn.execute(
                    'UPDATE facts SET statement = ? WHERE statement = ?',
                    (new_statement, old_statement)
                )
                conn.commit()
                return cur.rowcount
        except Exception as e:
            logger.error(f"Error updating fact: {e}")
            raise

    def _search_facts(self, query: str, limit: int = 10):
        """Search facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                # Simple LIKE search
                search_pattern = f'%{query}%'
                cur = conn.execute(
                    'SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?',
                    (search_pattern, limit)
                )
                return [row[0] for row in cur]
        except Exception as e:
            logger.error(f"Error searching facts: {e}")
            return []

    def _get_recent_facts(self, count: int = 5):
        """Get most recent facts from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cur = conn.execute(
                    'SELECT statement FROM facts ORDER BY id DESC LIMIT ?',
                    (count,)
                )
                return [row[0] for row in cur]
        except Exception as e:
            logger.error(f"Error getting recent facts: {e}")
            return []

    def _is_write_allowed(self, provided_token: str) -> bool:
        """Check if write operations are allowed"""
        if not self.write_enabled:
            return False
        if self.write_token_env:
            if not provided_token:
                return True
            return provided_token == self.write_token_env
        return True

    def _parse_statement(self, statement: str):
        """Parse statement into predicate and arguments"""
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

    def _append_audit(self, action: str, payload: dict):
        """Append to audit log"""
        try:
            audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = {"ts": ts, "action": action, "payload": payload}
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

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
                    "name": "HAK_GAL SQLite MCP",
                    "version": "2.0.0"
                }
            }
        }
        await self.send_response(response)

    async def handle_list_tools(self, request):
        """List available tools"""
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
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of facts", "default": 5}
                    }
                }
            },
            {
                "name": "add_fact",
                "description": "Add a new fact to the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "source": {"type": "string"},
                        "tags": {"type": "array", "items": {"type": "string"}},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["statement"]
                }
            },
            {
                "name": "delete_fact",
                "description": "Delete fact from the knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["statement"]
                }
            },
            {
                "name": "update_fact",
                "description": "Update an existing fact",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "old_statement": {"type": "string"},
                        "new_statement": {"type": "string"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["old_statement", "new_statement"]
                }
            },
            {
                "name": "kb_stats",
                "description": "Get knowledge base statistics",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_predicates_stats",
                "description": "Get predicate frequency statistics",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_entities_stats",
                "description": "Get entity frequency statistics",
                "inputSchema": {
                    "type": "object",
                    "properties": {"min_occurrences": {"type": "integer", "default": 2}}
                }
            },
            {
                "name": "search_by_predicate",
                "description": "Find facts by predicate name",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "predicate": {"type": "string"},
                        "limit": {"type": "integer", "default": 100}
                    },
                    "required": ["predicate"]
                }
            },
            {
                "name": "query_related",
                "description": "Find all facts mentioning an entity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity": {"type": "string"},
                        "limit": {"type": "integer", "default": 100}
                    },
                    "required": ["entity"]
                }
            },
            {
                "name": "get_knowledge_graph",
                "description": "Export subgraph around an entity",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "entity": {"type": "string"},
                        "depth": {"type": "integer", "default": 2},
                        "format": {"type": "string", "default": "json"}
                    },
                    "required": ["entity"]
                }
            },
            {
                "name": "find_isolated_facts",
                "description": "Find facts with unique entities",
                "inputSchema": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 50}}
                }
            },
            {
                "name": "health_check",
                "description": "Check system health",
                "inputSchema": {"type": "object", "properties": {}}
            }
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": {"tools": tools}
        }
        await self.send_response(response)

    async def handle_tool_call(self, request):
        """Handle tool execution"""
        params = request.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        
        result = {"content": [{"type": "text", "text": "Unknown tool"}]}
        
        try:
            if tool_name == "search_knowledge":
                query = tool_args.get("query", "")
                limit = tool_args.get("limit", 10)
                facts = self._search_facts(query, limit)
                text = f"Found {len(facts)} facts:\n" + "\n".join([f"- {s}" for s in facts])
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "get_system_status":
                count = self._count_facts()
                try:
                    st = self.sqlite_db_path.stat()
                    size = st.st_size
                    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
                except Exception:
                    size = -1
                    mtime = '<unknown>'
                text = (
                    f"Status: OK\n"
                    f"Facts: {count}\n"
                    f"DB: {self.sqlite_db_path}\n"
                    f"Size: {size} bytes\n"
                    f"Modified: {mtime}\n"
                    f"Backend: SQLite"
                )
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "list_recent_facts":
                count = tool_args.get("count", 5)
                facts = self._get_recent_facts(count)
                text = "Recent facts:\n" + "\n".join([f"- {s}" for s in facts])
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "add_fact":
                statement = tool_args.get("statement", "").strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled"}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing statement"}]}
                else:
                    success = self._add_fact(statement, {"source": tool_args.get("source", "mcp")})
                    if success:
                        self._append_audit("add_fact", {"statement": statement})
                        result = {"content": [{"type": "text", "text": "OK: fact added"}]}
                    else:
                        result = {"content": [{"type": "text", "text": "Fact already exists"}]}
                        
            elif tool_name == "delete_fact":
                statement = tool_args.get("statement", "")
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled"}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing statement"}]}
                else:
                    removed = self._delete_fact(statement)
                    self._append_audit("delete_fact", {"statement": statement, "removed": removed})
                    result = {"content": [{"type": "text", "text": f"OK: removed {removed}"}]}
                    
            elif tool_name == "update_fact":
                old_stmt = tool_args.get("old_statement", "")
                new_stmt = tool_args.get("new_statement", "")
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled"}]}
                elif not old_stmt or not new_stmt:
                    result = {"content": [{"type": "text", "text": "Missing statements"}]}
                else:
                    updated = self._update_fact(old_stmt, new_stmt)
                    self._append_audit("update_fact", {"old": old_stmt, "new": new_stmt, "updated": updated})
                    result = {"content": [{"type": "text", "text": f"OK: updated {updated}"}]}
                    
            elif tool_name == "kb_stats":
                count = self._count_facts()
                try:
                    st = self.sqlite_db_path.stat()
                    size = st.st_size
                    mtime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))
                except Exception:
                    size = -1
                    mtime = '<unknown>'
                text = (
                    f"KB (SQLite) facts: {count}\n"
                    f"KB size(bytes): {size}\n"
                    f"KB last_modified: {mtime}\n"
                    f"KB path: {self.sqlite_db_path}"
                )
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "get_predicates_stats":
                freq = {}
                for stmt in self._yield_statements():
                    pred, _ = self._parse_statement(stmt)
                    if pred:
                        freq[pred] = freq.get(pred, 0) + 1
                items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
                text = "\n".join([f"{k}: {v}" for k,v in items]) or "<none>"
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "get_entities_stats":
                min_occ = int(tool_args.get("min_occurrences", 2))
                freq = {}
                for stmt in self._yield_statements():
                    _, args = self._parse_statement(stmt)
                    for a in args:
                        freq[a] = freq.get(a, 0) + 1
                items = [(k,v) for k,v in freq.items() if v >= min_occ]
                items.sort(key=lambda x: x[1], reverse=True)
                text = "\n".join([f"{k}: {v}" for k,v in items]) or "<none>"
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "search_by_predicate":
                predicate = str(tool_args.get("predicate", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not predicate:
                    result = {"content": [{"type": "text", "text": "Missing predicate"}]}
                else:
                    matches = []
                    for stmt in self._yield_statements():
                        pred, _ = self._parse_statement(stmt)
                        if pred == predicate:
                            matches.append(stmt)
                            if len(matches) >= limit:
                                break
                    text = "\n".join([f"- {s}" for s in matches]) or "<no matches>"
                    result = {"content": [{"type": "text", "text": text}]}
                    
            elif tool_name == "query_related":
                entity = str(tool_args.get("entity", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing entity"}]}
                else:
                    matches = []
                    for stmt in self._yield_statements():
                        if entity in stmt:
                            matches.append(stmt)
                            if len(matches) >= limit:
                                break
                    text = "\n".join([f"- {s}" for s in matches]) or "<no matches>"
                    result = {"content": [{"type": "text", "text": text}]}
                    
            elif tool_name == "get_knowledge_graph":
                entity = str(tool_args.get("entity", "")).strip()
                depth = int(tool_args.get("depth", 2))
                fmt = str(tool_args.get("format", "json")).lower()
                
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing entity"}]}
                else:
                    edges = []
                    nodes = set([entity])
                    facts = []
                    all_st = self._get_all_statements()
                    frontier = {entity}
                    
                    for _ in range(max(0, depth)):
                        next_frontier = set()
                        for st in all_st:
                            pred, args = self._parse_statement(st)
                            if not pred or not args:
                                continue
                            if any(e in args for e in frontier):
                                facts.append(st)
                                if len(args) >= 2:
                                    edges.append((args[0], pred, args[1]))
                                for a in args:
                                    if a not in nodes:
                                        nodes.add(a)
                                        next_frontier.add(a)
                        frontier = next_frontier
                    
                    if fmt == 'dot':
                        lines = ["digraph G {"]
                        for a,p,b in edges:
                            lines.append(f'  "{a}" -> "{b}" [label="{p}"];')
                        lines.append("}")
                        text = "\n".join(lines)
                    else:
                        graph = {
                            "nodes": sorted(list(nodes)),
                            "edges": [{"source": a, "predicate": p, "target": b} for a,p,b in edges],
                            "facts": facts,
                        }
                        text = json.dumps(graph, ensure_ascii=False, indent=2)
                    result = {"content": [{"type": "text", "text": text}]}
                    
            elif tool_name == "find_isolated_facts":
                limit = int(tool_args.get("limit", 50))
                counts = collections.Counter()
                statements = []
                
                for st in self._yield_statements():
                    statements.append(st)
                    _, args = self._parse_statement(st)
                    for a in args:
                        counts[a] += 1
                
                isolated = []
                for st in statements:
                    _, args = self._parse_statement(st)
                    if args and all(counts[a] == 1 for a in args):
                        isolated.append(st)
                        if len(isolated) >= limit:
                            break
                
                text = "\n".join([f"- {s}" for s in isolated]) or "<none>"
                result = {"content": [{"type": "text", "text": text}]}
                
            elif tool_name == "health_check":
                count = self._count_facts()
                db_exists = self.sqlite_db_path.exists()
                try:
                    st = self.sqlite_db_path.stat()
                    size = st.st_size
                except Exception:
                    size = 0
                
                text = (
                    f"Status: OK\n"
                    f"DB exists: {db_exists}\n"
                    f"Facts: {count}\n"
                    f"DB size(bytes): {size}\n"
                    f"Write enabled: {self.write_enabled}\n"
                    f"Backend: SQLite ONLY (no JSONL)"
                )
                result = {"content": [{"type": "text", "text": text}]}
                
        except Exception as e:
            logger.error(f"Error in tool {tool_name}: {e}")
            result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": result
        }
        await self.send_response(response)

    async def handle_request(self, request):
        """Route JSON-RPC requests"""
        method = request.get("method", "")
        
        if method == "initialize":
            await self.handle_initialize(request)
        elif method == "tools/list":
            await self.handle_list_tools(request)
        elif method == "tools/call":
            await self.handle_tool_call(request)
        elif method == "shutdown":
            self.running = False
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": None
            }
            await self.send_response(response)
        else:
            error_response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
            await self.send_response(error_response)

    async def run(self):
        """Main server loop"""
        logger.info("HAK_GAL SQLite MCP Server starting...")
        logger.info(f"SQLite DB: {self.sqlite_db_path}")
        logger.info(f"DB exists: {self.sqlite_db_path.exists()}")
        
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                logger.debug(f"Received: {line[:200]}")
                
                try:
                    request = json.loads(line)
                    await self.handle_request(request)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    await self.send_response(error_response)
                    
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Unexpected error: {e}")
                logger.error(traceback.format_exc())
                
        logger.info("HAK_GAL SQLite MCP Server stopped")

async def main():
    server = HAKGALMCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server interrupted")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
