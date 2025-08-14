#!/usr/bin/env python3
"""
HAK_GAL MCP Server - Fixed Version for Claude Desktop Integration
Research Project: Making MCP work with HAK_GAL
"""

import sys
import os
import json
import asyncio
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
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = {"ts": ts, "action": action, "payload": payload}
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _delete_one_statement(self, target_statement: str) -> int:
        removed = 0
        tmp_path = self.kb_path.with_suffix(self.kb_path.suffix + ".tmp")
        with open(self.kb_path, "r", encoding="utf-8") as src, open(tmp_path, "w", encoding="utf-8") as dst:
            skipped = False
            for line in src:
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except Exception:
                    obj = None
                if (not skipped) and obj and obj.get("statement") == target_statement:
                    skipped = True
                    removed += 1
                    continue
                dst.write(line)
        os.replace(tmp_path, self.kb_path)
        return removed

    def _parse_statement(self, statement: str):
        try:
            l = statement.find("(")
            r = statement.rfind(")")
            if l == -1 or r == -1 or r <= l:
                return None, []
            predicate = statement[:l].strip()
            inner = statement[l+1:r]
            # Split by comma without complex parsing (assumes no nested commas)
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
                    "name": "HAK_GAL MCP",
                    "version": "1.0.0"
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
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Number of facts", "default": 5}
                    }
                }
            },
            {
                "name": "add_fact",
                "description": "Append a new fact (requires write enable + optional token)",
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
                "description": "Delete facts matching exact statement (requires write enable)",
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
                "description": "Replace an exact statement with a new one (requires write enable)",
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
                "description": "Return KB metrics (count, size, last_modified)",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "list_audit",
                "description": "List last N audit entries",
                "inputSchema": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 20}}
                }
            },
            {
                "name": "export_facts",
                "description": "Export first/last N facts (direction='head'|'tail')",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 50},
                        "direction": {"type": "string", "default": "tail"}
                    }
                }
            },
            {
                "name": "growth_stats",
                "description": "Growth over last N days based on audit (fallback: total only)",
                "inputSchema": {"type": "object", "properties": {"days": {"type": "integer", "default": 30}}}
            },
            {
                "name": "health_check",
                "description": "Comprehensive health status of MCP server and KB",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "semantic_similarity",
                "description": "Find semantically similar facts (cosine over token TF)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statement": {"type": "string"},
                        "threshold": {"type": "number", "default": 0.8},
                        "limit": {"type": "integer", "default": 50}
                    },
                    "required": ["statement"]
                }
            },
            {
                "name": "consistency_check",
                "description": "Detect simple contradictory pairs (Nicht- vs positive predicate)",
                "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 1000}}}
            },
            {
                "name": "validate_facts",
                "description": "Validate syntax of facts (simple predicate(args) check)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 1000}}
                }
            },
            {
                "name": "get_entities_stats",
                "description": "Frequency of entities across arguments",
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
                    "properties": {"predicate": {"type": "string"}, "limit": {"type": "integer", "default": 100}},
                    "required": ["predicate"]
                }
            },
            {
                "name": "get_fact_history",
                "description": "Show audit entries related to a statement",
                "inputSchema": {
                    "type": "object",
                    "properties": {"statement": {"type": "string"}, "limit": {"type": "integer", "default": 50}},
                    "required": ["statement"]
                }
            },
            {
                "name": "backup_kb",
                "description": "Create a timestamped backup of the KB (requires write enable)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"description": {"type": "string"}, "auth_token": {"type": "string"}}
                }
            },
            {
                "name": "restore_kb",
                "description": "Restore KB from a backup id or path (requires write enable)",
                "inputSchema": {
                    "type": "object",
                    "properties": {"backup_id": {"type": "string"}, "path": {"type": "string"}, "auth_token": {"type": "string"}}
                }
            },
            {
                "name": "bulk_delete",
                "description": "Delete multiple exact statements (requires write enable)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "statements": {"type": "array", "items": {"type": "string"}},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["statements"]
                }
            },
            {
                "name": "get_predicates_stats",
                "description": "Return frequency of predicates",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "query_related",
                "description": "Return all facts mentioning an entity",
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
                "name": "analyze_duplicates",
                "description": "Find potentially duplicate/similar facts (token Jaccard)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "threshold": {"type": "number", "default": 0.9},
                        "max_pairs": {"type": "integer", "default": 200}
                    }
                }
            },
            {
                "name": "get_knowledge_graph",
                "description": "Export subgraph around an entity as JSON or DOT",
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
                "description": "Find facts whose entities appear only once in KB",
                "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}}
            },
            {
                "name": "inference_chain",
                "description": "Build a simple chain of related facts by shared entities",
                "inputSchema": {
                    "type": "object",
                    "properties": {"start_fact": {"type": "string"}, "max_depth": {"type": "integer", "default": 5}},
                    "required": ["start_fact"]
                }
            },
            {
                "name": "bulk_translate_predicates",
                "description": "Translate predicates in the KB using a mapping (dry-run by default)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mapping": {"type": "object", "description": "Map of oldPredicate -> newPredicate"},
                        "predicates": {"type": "array", "items": {"type": "string"}, "description": "Optional allowlist of predicates to consider"},
                        "exclude_predicates": {"type": "array", "items": {"type": "string"}, "description": "Optional blocklist of predicates to skip"},
                        "dry_run": {"type": "boolean", "default": True},
                        "limit": {"type": "integer", "default": 0, "description": "Max lines to process when limit_mode=lines (0 = all)"},
                        "limit_mode": {"type": "string", "default": "lines", "enum": ["lines", "changes"], "description": "Interpretation of limit: lines vs number of changes"},
                        "start_offset": {"type": "integer", "default": 0, "description": "Skip the first N lines before processing"},
                        "sample_strategy": {"type": "string", "default": "head", "enum": ["head", "tail", "stratified"], "description": "Dry-run only sampling strategy"},
                        "report_path": {"type": "string", "description": "Optional file path to write a summary report (md or json)"},
                        "auth_token": {"type": "string", "description": "Write authorization when dry_run=false"}
                    },
                    "required": ["mapping"]
                }
            },
            {
                "name": "project_snapshot",
                "description": "Create a timestamped project snapshot in a hub folder (Markdown + JSON). Requires write.",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "description": {"type": "string"},
                        "hub_path": {"type": "string"},
                        "auth_token": {"type": "string"}
                    }
                }
            },
            {
                "name": "project_list_snapshots",
                "description": "List recent project snapshots from the hub folder",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hub_path": {"type": "string"},
                        "limit": {"type": "integer", "default": 20}
                    }
                }
            },
            {
                "name": "project_hub_digest",
                "description": "Return a digest of the latest snapshot files for quick context",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hub_path": {"type": "string"},
                        "limit_files": {"type": "integer", "default": 3},
                        "max_chars": {"type": "integer", "default": 20000}
                    }
                }
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
                data = await self.search_knowledge(
                    tool_args.get("query", ""),
                    tool_args.get("limit", 10)
                )
                text = "Found {} facts:\n".format(data.get("count", 0)) + "\n".join([f"- {s}" for s in data.get("facts", [])])
                result = {"content": [{"type": "text", "text": text}]}
            elif tool_name == "get_system_status":
                data = await self.get_system_status()
                if "error" in data:
                    result = {"content": [{"type": "text", "text": f"Error: {data['error']}"}]}
                else:
                    text = (
                        f"Status: {data.get('status','unknown')}\n"
                        f"Facts: {data.get('kb_facts',0)}\n"
                        f"KB: {data.get('kb_path','')}\n"
                        f"Server: {data.get('server','')}"
                    )
                    result = {"content": [{"type": "text", "text": text}]}
            elif tool_name == "list_recent_facts":
                data = await self.list_recent_facts(
                    tool_args.get("count", 5)
                )
                if "error" in data:
                    result = {"content": [{"type": "text", "text": f"Error: {data['error']}"}]}
                else:
                    text = "Recent facts:\n" + "\n".join([f"- {s}" for s in data.get("facts", [])])
                    result = {"content": [{"type": "text", "text": text}]}
            elif tool_name == "add_fact":
                statement = tool_args.get("statement", "").strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                elif requests is None:
                    result = {"content": [{"type": "text", "text": "Error: 'requests' module not available"}]}
                else:
                    try:
                        resp = requests.post(f"{self.api_base_url}/api/facts", json={
                            "statement": statement,
                            "context": {"source": tool_args.get("source") or "mcp"}
                        }, timeout=10)
                        if resp.status_code in (200, 201):
                            self._append_audit("add_fact", {"statement": statement})
                            result = {"content": [{"type": "text", "text": "OK: fact appended (SQLite)"}]}
                        elif resp.status_code == 409:
                            result = {"content": [{"type": "text", "text": "Fact already exists"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code} {resp.text}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "delete_fact":
                statement = tool_args.get("statement", "")
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                elif requests is None:
                    result = {"content": [{"type": "text", "text": "Error: 'requests' module not available"}]}
                else:
                    try:
                        resp = requests.post(f"{self.api_base_url}/api/facts/delete", json={"statement": statement}, timeout=10)
                        if resp.ok:
                            removed = 0
                            try:
                                removed = resp.json().get("removed", 0)
                            except Exception:
                                pass
                            self._append_audit("delete_fact", {"statement": statement, "removed": removed})
                            result = {"content": [{"type": "text", "text": f"OK: removed {removed} (SQLite)"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code} {resp.text}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "update_fact":
                old_stmt = tool_args.get("old_statement", "")
                new_stmt = tool_args.get("new_statement", "")
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                elif not old_stmt or not new_stmt:
                    result = {"content": [{"type": "text", "text": "Missing 'old_statement' or 'new_statement'"}]}
                elif requests is None:
                    result = {"content": [{"type": "text", "text": "Error: 'requests' module not available"}]}
                else:
                    try:
                        resp = requests.put(f"{self.api_base_url}/api/facts/update", json={
                            "old_statement": old_stmt,
                            "new_statement": new_stmt
                        }, timeout=10)
                        if resp.ok:
                            updated = 0
                            try:
                                updated = resp.json().get("updated", 0)
                            except Exception:
                                pass
                            self._append_audit("update_fact", {"old": old_stmt, "new": new_stmt, "updated": updated})
                            result = {"content": [{"type": "text", "text": f"OK: updated {updated} (SQLite)"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code} {resp.text}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "kb_stats":
                try:
                    st = self.kb_path.stat()
                    # count lines quickly
                    cnt = 0
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for _ in f:
                            cnt += 1
                    text = (
                        f"KB count(lines): {cnt}\n"
                        f"KB size(bytes): {st.st_size}\n"
                        f"KB last_modified: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(st.st_mtime))}"
                    )
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "list_audit":
                limit = int(tool_args.get("limit", 20))
                lines = []
                try:
                    audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                    if audit_path.exists():
                        with open(audit_path, 'r', encoding='utf-8') as f:
                            lines = f.readlines()[-limit:]
                    text = "".join(lines) if lines else "<empty>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "export_facts":
                count = int(tool_args.get("count", 50))
                direction = str(tool_args.get("direction", "tail")).lower()
                try:
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                    sel = lines[:count] if direction == 'head' else lines[-count:]
                    text = "".join(sel)
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "growth_stats":
                days = int(tool_args.get("days", 30))
                try:
                    by_day = collections.Counter()
                    total = 0
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for _ in f:
                            total += 1
                    audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                    if audit_path.exists():
                        cutoff = time.time() - days*86400
                        with open(audit_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    obj = json.loads(line)
                                    if obj.get('action') == 'add_fact':
                                        # parse ts "YYYY-MM-DD HH:MM:SS"
                                        ts = obj.get('ts')
                                        t = time.mktime(time.strptime(ts, "%Y-%m-%d %H:%M:%S"))
                                        if t >= cutoff:
                                            day = time.strftime('%Y-%m-%d', time.localtime(t))
                                            by_day[day] += 1
                                except Exception:
                                    pass
                    days_list = []
                    for i in range(days-1, -1, -1):
                        day = time.strftime('%Y-%m-%d', time.localtime(time.time()-i*86400))
                        days_list.append((day, by_day.get(day, 0)))
                    avg = sum(v for _,v in days_list)/len(days_list) if days_list else 0
                    text = "\n".join([f"{d}: +{v}" for d,v in days_list])
                    text = f"Total: {total}\nAvg/day({days}d): {avg:.2f}\n" + text
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "health_check":
                try:
                    st = self.kb_path.stat()
                    kb_exists = self.kb_path.exists()
                    kb_size = st.st_size if kb_exists else 0
                    # quick count
                    cnt = 0
                    if kb_exists:
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for _ in f:
                                cnt += 1
                    write_enabled = self.write_enabled
                    env_ok = os.environ.get('PYTHONIOENCODING','').lower() == 'utf-8'
                    text = (f"status: OK\nKB exists: {kb_exists}\nKB lines: {cnt}\nKB size(bytes): {kb_size}\n"
                            f"write_enabled: {write_enabled}\nPYTHONIOENCODING=utf-8: {env_ok}")
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "semantic_similarity":
                base = str(tool_args.get("statement", ""))
                threshold = float(tool_args.get("threshold", 0.8))
                limit = int(tool_args.get("limit", 50))
                if not base:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                else:
                    def vec(text: str):
                        tokens = re.findall(r"\w+", text.lower())
                        c = collections.Counter(tokens)
                        nrm = math.sqrt(sum(v*v for v in c.values())) or 1.0
                        return c, nrm
                    def cosine(a, b):
                        ca, na = a
                        cb, nb = b
                        inter = set(ca) & set(cb)
                        dot = sum(ca[t]*cb[t] for t in inter)
                        return dot/(na*nb)
                    try:
                        base_vec = vec(base)
                        sims = []
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    obj = json.loads(line)
                                    st = obj.get('statement','')
                                    if not st:
                                        continue
                                    v = vec(st)
                                    cs = cosine(base_vec, v)
                                    if cs >= threshold:
                                        sims.append((cs, st))
                                except Exception:
                                    pass
                        sims.sort(key=lambda x: x[0], reverse=True)
                        text = "\n".join([f"{cs:.3f} {st}" for cs,st in sims[:limit]]) or "<no similar>"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "consistency_check":
                limit = int(tool_args.get("limit", 1000))
                # Simple heuristic: predicate vs "Nicht"+predicate contradictions
                try:
                    pos = set()
                    neg = set()
                    checked = 0
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                                pred, args = self._parse_statement(st)
                                if not pred or not args:
                                    continue
                                if pred.startswith('Nicht'):
                                    neg.add((pred[5:], tuple(args)))
                                else:
                                    pos.add((pred, tuple(args)))
                                checked += 1
                                if checked >= limit:
                                    break
                            except Exception:
                                pass
                    conflicts = []
                    for p in pos:
                        if ('Nicht'+p[0], p[1]) in {('Nicht'+a, b) for a,b in pos}:
                            # ignore; we only want pos vs neg
                            pass
                    for npred, nargs in list(neg):
                        if (npred, nargs) in pos:
                            conflicts.append((npred, list(nargs)))
                    text = "\n".join([f"Widerspruch: {pred}({', '.join(args)}) vs Nicht{pred}({', '.join(args)})" for pred,args in conflicts]) or "<none>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "validate_facts":
                limit = int(tool_args.get("limit", 1000))
                errors = []
                checked = 0
                try:
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                            except Exception as e:
                                errors.append(f"JSON error: {e}")
                                continue
                            pred, args = self._parse_statement(st)
                            if not pred:
                                errors.append(f"Invalid syntax: {st}")
                            elif not args:
                                errors.append(f"No arguments: {st}")
                            checked += 1
                            if checked >= limit:
                                break
                    text = ("OK" if not errors else "\n".join(errors[:200]))
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "get_entities_stats":
                min_occ = int(tool_args.get("min_occurrences", 2))
                freq = {}
                try:
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                                _, args = self._parse_statement(st)
                                for a in args:
                                    freq[a] = freq.get(a, 0) + 1
                            except Exception:
                                pass
                    items = [(k,v) for k,v in freq.items() if v >= min_occ]
                    items.sort(key=lambda x: x[1], reverse=True)
                    text = "\n".join([f"{k}: {v}" for k,v in items]) or "<none>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "search_by_predicate":
                predicate = str(tool_args.get("predicate", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not predicate:
                    result = {"content": [{"type": "text", "text": "Missing 'predicate'"}]}
                else:
                    out = []
                    try:
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    obj = json.loads(line)
                                    st = obj.get('statement','')
                                    pred, _ = self._parse_statement(st)
                                    if pred == predicate:
                                        out.append(st)
                                        if len(out) >= limit:
                                            break
                                except Exception:
                                    pass
                        text = "\n".join([f"- {s}" for s in out]) or "<no matches>"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "get_fact_history":
                statement = str(tool_args.get("statement", ""))
                limit = int(tool_args.get("limit", 50))
                if not statement:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                else:
                    try:
                        audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                        lines = []
                        if audit_path.exists():
                            with open(audit_path, 'r', encoding='utf-8') as f:
                                for line in f:
                                    if statement in line:
                                        lines.append(line)
                        text = "".join(lines[-limit:]) or "<no history>"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "backup_kb":
                desc = str(tool_args.get("description", "")).strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                else:
                    try:
                        ts = time.strftime("%Y%m%d%H%M%S")
                        backups_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/backups")
                        backups_dir.mkdir(parents=True, exist_ok=True)
                        backup_id = ts
                        if desc:
                            safe_desc = re.sub(r"[^A-Za-z0-9_-]+", "_", desc)[:40]
                            backup_id = f"{ts}_{safe_desc}"
                        dst = backups_dir / f"kb_{backup_id}.jsonl"
                        shutil.copy2(self.kb_path, dst)
                        self._append_audit("backup_kb", {"id": backup_id, "path": str(dst)})
                        text = f"OK: backup_id={backup_id}\npath={dst}"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "restore_kb":
                backup_id = str(tool_args.get("backup_id", "")).strip()
                path_override = str(tool_args.get("path", "")).strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                else:
                    try:
                        src_path = None
                        if path_override:
                            src_path = Path(path_override)
                        else:
                            backups_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/backups")
                            candidate = backups_dir / f"kb_{backup_id}.jsonl"
                            if candidate.exists():
                                src_path = candidate
                        if not src_path or not src_path.exists():
                            raise FileNotFoundError("Backup not found")
                        self._acquire_lock()
                        shutil.copy2(src_path, self.kb_path)
                        self._append_audit("restore_kb", {"from": str(src_path)})
                        result = {"content": [{"type": "text", "text": "OK: restored"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                    finally:
                        self._release_lock()
            elif tool_name == "bulk_delete":
                stmts = tool_args.get("statements", []) or []
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                elif requests is None:
                    result = {"content": [{"type": "text", "text": "Error: 'requests' module not available"}]}
                else:
                    total_removed = 0
                    errors = 0
                    for s in stmts:
                        try:
                            resp = requests.post(f"{self.api_base_url}/api/facts/delete", json={"statement": str(s)}, timeout=10)
                            if resp.ok:
                                try:
                                    total_removed += resp.json().get("removed", 0)
                                except Exception:
                                    pass
                            else:
                                errors += 1
                        except Exception:
                            errors += 1
                    self._append_audit("bulk_delete", {"count": len(stmts), "removed": total_removed, "errors": errors})
                    result = {"content": [{"type": "text", "text": f"OK: removed {total_removed}, errors {errors} (SQLite)"}]}
            elif tool_name == "get_predicates_stats":
                try:
                    freq = {}
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                                pred, _ = self._parse_statement(st)
                                if pred:
                                    freq[pred] = freq.get(pred, 0) + 1
                            except Exception:
                                pass
                    # sort by count desc
                    items = sorted(freq.items(), key=lambda x: x[1], reverse=True)
                    text = "\n".join([f"{k}: {v}" for k,v in items])
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "query_related":
                entity = str(tool_args.get("entity", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing 'entity'"}]}
                else:
                    matches = []
                    try:
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    obj = json.loads(line)
                                    st = obj.get('statement','')
                                    if entity in st:
                                        matches.append(st)
                                        if len(matches) >= limit:
                                            break
                                except Exception:
                                    pass
                        text = "\n".join([f"- {s}" for s in matches]) or "<no matches>"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "analyze_duplicates":
                threshold = float(tool_args.get("threshold", 0.9))
                max_pairs = int(tool_args.get("max_pairs", 200))
                # simple token Jaccard similarity on statements
                def jaccard(a: str, b: str) -> float:
                    ta = set(re.findall(r"\w+", a.lower()))
                    tb = set(re.findall(r"\w+", b.lower()))
                    if not ta and not tb:
                        return 1.0
                    if not ta or not tb:
                        return 0.0
                    inter = len(ta & tb)
                    union = len(ta | tb)
                    return inter / union if union else 0.0
                try:
                    statements = []
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                                if st:
                                    statements.append(st)
                            except Exception:
                                pass
                    pairs = []
                    n = len(statements)
                    checked = 0
                    for i in range(n):
                        for j in range(i+1, n):
                            if checked >= max_pairs:
                                break
                            sim = jaccard(statements[i], statements[j])
                            if sim >= threshold:
                                pairs.append((statements[i], statements[j], sim))
                            checked += 1
                        if checked >= max_pairs:
                            break
                    pairs.sort(key=lambda x: x[2], reverse=True)
                    text = "\n\n".join([f"SIM={sim:.2f}\nA: {a}\nB: {b}" for a,b,sim in pairs]) or "<no similar pairs>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "get_knowledge_graph":
                entity = str(tool_args.get("entity", "")).strip()
                depth = int(tool_args.get("depth", 2))
                fmt = str(tool_args.get("format", "json")).lower()
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing 'entity'"}]}
                else:
                    # BFS über Fakten via gemeinsam vorkommende Entitäten
                    try:
                        edges = []
                        nodes = set([entity])
                        facts = []
                        # Preload statements
                        all_st = []
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if not line.strip():
                                    continue
                                try:
                                    obj = json.loads(line)
                                    st = obj.get('statement','')
                                    all_st.append(st)
                                except Exception:
                                    pass
                        frontier = {entity}
                        for _ in range(max(0, depth)):
                            next_frontier = set()
                            for st in all_st:
                                pred, args = self._parse_statement(st)
                                if not pred or not args:
                                    continue
                                if any(e in args for e in frontier):
                                    facts.append(st)
                                    # Kanten: (arg_i) -[pred]-> (arg_j)
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
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "find_isolated_facts":
                limit = int(tool_args.get("limit", 50))
                try:
                    counts = collections.Counter()
                    statements = []
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                st = obj.get('statement','')
                                statements.append(st)
                                _, args = self._parse_statement(st)
                                for a in args:
                                    counts[a] += 1
                            except Exception:
                                pass
                    isolated = []
                    for st in statements:
                        _, args = self._parse_statement(st)
                        if args and all(counts[a] == 1 for a in args):
                            isolated.append(st)
                            if len(isolated) >= limit:
                                break
                    text = "\n".join([f"- {s}" for s in isolated]) or "<none>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "inference_chain":
                start_fact = str(tool_args.get("start_fact", ""))
                max_depth = int(tool_args.get("max_depth", 5))
                if not start_fact:
                    result = {"content": [{"type": "text", "text": "Missing 'start_fact'"}]}
                else:
                    try:
                        chain = [start_fact]
                        _, seed_args = self._parse_statement(start_fact)
                        if not seed_args:
                            result = {"content": [{"type": "text", "text": "Start fact has no arguments"}]}
                        else:
                            current_entities = set(seed_args)
                            with open(self.kb_path, 'r', encoding='utf-8') as f:
                                all_st = [json.loads(l).get('statement','') for l in f if l.strip()]
                            used = set([start_fact])
                            for _ in range(max_depth):
                                extended = False
                                for st in all_st:
                                    if st in used:
                                        continue
                                    _, args = self._parse_statement(st)
                                    if not args:
                                        continue
                                    if any(a in current_entities for a in args):
                                        chain.append(st)
                                        used.add(st)
                                        for a in args:
                                            current_entities.add(a)
                                        extended = True
                                        break
                                if not extended:
                                    break
                            text = "\n".join([f"- {s}" for s in chain])
                            result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "project_snapshot":
                title = str(tool_args.get("title", "")).strip() or "Session Snapshot"
                description = str(tool_args.get("description", "")).strip()
                hub_path = str(tool_args.get("hub_path", "")).strip() or self.hub_path_env
                auth_token = tool_args.get("auth_token", "")
                if not hub_path:
                    result = {"content": [{"type": "text", "text": "Missing 'hub_path'"}]}
                elif not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                else:
                    try:
                        hub = Path(hub_path)
                        hub.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        snap_dir = hub / f"snapshot_{ts}"
                        snap_dir.mkdir(parents=True, exist_ok=True)
                        # Sammle Basisdaten (KB/Handover)
                        # 1) Health
                        st = self.kb_path.stat()
                        kb_lines = 0
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for _ in f: kb_lines += 1
                        # 2) Top-Predicates
                        freq = {}
                        with open(self.kb_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                if not line.strip(): continue
                                try:
                                    obj = json.loads(line)
                                    stt = obj.get('statement','')
                                    pred, _ = self._parse_statement(stt)
                                    if pred: freq[pred] = freq.get(pred,0)+1
                                except Exception: pass
                        top_preds = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:20]
                        # 3) Letzte Audits
                        audit_entries = []
                        audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                        if audit_path.exists():
                            with open(audit_path, 'r', encoding='utf-8') as f:
                                audit_entries = f.readlines()[-50:]
                        # Schreibe KB-Handover (Markdown)
                        kb_md = [
                            f"# {title} — KB Handover",
                            "",
                            f"{description}",
                            "",
                            "## Health",
                            f"- KB lines: {kb_lines}",
                            f"- KB size(bytes): {st.st_size}",
                            f"- KB path: {self.kb_path}",
                            "",
                            "## Top Predicates",
                        ]
                        for k,v in top_preds:
                            kb_md.append(f"- {k}: {v}")
                        kb_md += ["", "## Recent Audit (last 50)", "``````"]
                        kb_md += [e.rstrip("\n") for e in audit_entries]
                        kb_md += ["``````"]
                        (snap_dir / "SNAPSHOT_KB.md").write_text("\n".join(kb_md), encoding='utf-8')
                        # Schreibe KB JSON
                        json_obj = {
                            "title": title,
                            "description": description,
                            "timestamp": ts,
                            "kb": {"lines": kb_lines, "size": st.st_size, "path": str(self.kb_path)},
                            "top_predicates": top_preds,
                            "recent_audit": audit_entries,
                        }
                        (snap_dir / "snapshot_kb.json").write_text(json.dumps(json_obj, ensure_ascii=False, indent=2), encoding='utf-8')

                        # TECH Handover: Architektur-Überblick + Manifest + Diff vs letztem Snapshot
                        project_root = Path(__file__).resolve().parent.parent  # Projektwurzel
                        include_dirs = [
                            project_root / 'src_hexagonal',
                            project_root / 'infrastructure',
                            project_root / 'scripts',
                        ]
                        def make_tree(path: Path, max_depth: int = 3) -> list:
                            lines = []
                            base_len = len(str(path))
                            def walk(p: Path, depth: int):
                                if depth > max_depth:
                                    return
                                try:
                                    entries = sorted(p.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
                                except Exception:
                                    return
                                for e in entries:
                                    rel = str(e)[base_len+1:]
                                    if any(skip in rel for skip in ['.venv', 'node_modules', 'backups', '__pycache__']):
                                        continue
                                    indent = '  ' * depth
                                    lines.append(f"{indent}- {'[DIR]' if e.is_dir() else '[FILE]'} {rel}")
                                    if e.is_dir():
                                        walk(e, depth+1)
                            if path.exists():
                                lines.append(f"[ROOT] {path}")
                                walk(path, 1)
                            return lines

                        def build_manifest(root: Path) -> dict:
                            manifest = {}
                            for dirpath, dirnames, filenames in os.walk(root):
                                if any(skip in dirpath for skip in ['.venv', 'node_modules', 'backups', '__pycache__', 'PROJECT_HUB']):
                                    continue
                                for fn in filenames:
                                    if not any(fn.lower().endswith(ext) for ext in ('.py','.md','.json','.yml','.yaml','.toml','.txt')):
                                        continue
                                    p = Path(dirpath) / fn
                                    try:
                                        data = p.read_bytes()
                                        h = hashlib.sha256(data).hexdigest()
                                        stt = p.stat()
                                        manifest[str(p)] = {"sha256": h, "size": stt.st_size, "mtime": stt.st_mtime}
                                    except Exception:
                                        pass
                            return manifest

                        # Erstelle Manifest und vergleiche mit letztem Snapshot
                        manifest = build_manifest(project_root)
                        (snap_dir / 'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
                        # Finde letztes Snapshot mit Manifest
                        prev_snaps = [p for p in hub.iterdir() if p.is_dir() and p.name.startswith('snapshot_') and p != snap_dir]
                        prev_snaps.sort(key=lambda p: p.name, reverse=True)
                        added = removed = changed = []
                        if prev_snaps:
                            prev = prev_snaps[0]
                            prev_mf_path = prev / 'manifest.json'
                            if prev_mf_path.exists():
                                try:
                                    prev_mf = json.loads(prev_mf_path.read_text(encoding='utf-8'))
                                    prev_keys = set(prev_mf.keys())
                                    cur_keys = set(manifest.keys())
                                    added = sorted(list(cur_keys - prev_keys))
                                    removed = sorted(list(prev_keys - cur_keys))
                                    changed = sorted([k for k in (cur_keys & prev_keys) if prev_mf[k]['sha256'] != manifest[k]['sha256']])
                                except Exception:
                                    pass

                        # Schreibe TECH Markdown
                        tech_md = [
                            f"# {title} — Technical Handover",
                            "",
                            f"{description}",
                            "",
                            "## Architecture Overview (Hexagonal)",
                        ]
                        for d in include_dirs:
                            tech_md.append("")
                            tech_md.append(f"### Tree: {d}")
                            tech_md += make_tree(d, max_depth=3)
                        tech_md += [
                            "",
                            "## Changes vs previous snapshot",
                            f"- Added: {len(added)}",
                            f"- Removed: {len(removed)}",
                            f"- Changed: {len(changed)}",
                            "",
                            "### Added",
                        ]
                        tech_md += [f"- {p}" for p in added[:200]] or ["- <none>"]
                        tech_md += ["", "### Removed"]
                        tech_md += [f"- {p}" for p in removed[:200]] or ["- <none>"]
                        tech_md += ["", "### Changed"]
                        tech_md += [f"- {p}" for p in changed[:200]] or ["- <none>"]

                        (snap_dir / "SNAPSHOT_TECH.md").write_text("\n".join(tech_md), encoding='utf-8')

                        # Kurzer Gesamt-SNAPSHOT als Einstieg weiterhin bereitstellen
                        summary_md = [
                            f"# {title}",
                            "",
                            f"{description}",
                            "",
                            "- Enthält: SNAPSHOT_TECH.md (Architektur/Diff), SNAPSHOT_KB.md (KB & Audit)",
                        ]
                        (snap_dir / "SNAPSHOT.md").write_text("\n".join(summary_md), encoding='utf-8')

                        text = f"OK: snapshot at {snap_dir}"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "bulk_translate_predicates":
                mapping = tool_args.get("mapping", {}) or {}
                allow = tool_args.get("predicates") or None
                exclude = tool_args.get("exclude_predicates") or None
                dry_run = bool(tool_args.get("dry_run", True))
                limit_val = int(tool_args.get("limit", 0))  # 0 = all
                limit_mode = str(tool_args.get("limit_mode", "lines")).lower()
                start_offset = int(tool_args.get("start_offset", 0))
                sample_strategy = str(tool_args.get("sample_strategy", "head")).lower()
                report_path = tool_args.get("report_path") or None
                auth_token = tool_args.get("auth_token", "")

                if not isinstance(mapping, dict) or not mapping:
                    result = {"content": [{"type": "text", "text": "Missing or empty 'mapping' (oldPredicate -> newPredicate)"}]}
                elif (not dry_run) and (not self._is_write_allowed(auth_token)):
                    result = {"content": [{"type": "text", "text": "Write disabled. Set HAKGAL_WRITE_ENABLED=true and provide valid auth_token if configured."}]}
                else:
                    allow_set = set([str(p) for p in (allow or [])]) if allow else None
                    exclude_set = set([str(p) for p in (exclude or [])]) if exclude else None

                    changed_total = 0
                    checked_total = 0
                    per_predicate = {}
                    examples = []

                    def translate_statement(stmt: str):
                        try:
                            pred, args = self._parse_statement(stmt)
                            if not pred or not args:
                                return stmt, None, None
                            if allow_set is not None and pred not in allow_set:
                                return stmt, None, None
                            if exclude_set is not None and pred in exclude_set:
                                return stmt, None, None
                            if pred in mapping:
                                new_pred = str(mapping[pred])
                                new_stmt = f"{new_pred}({', '.join(args)})"
                                if stmt.strip().endswith('.') and not new_stmt.endswith('.'):
                                    new_stmt += '.'
                                return new_stmt, pred, new_pred
                            return stmt, None, None
                        except Exception:
                            return stmt, None, None

                    if dry_run:
                        try:
                            # Build buffer with optional offset
                            lines_buf = []
                            with open(self.kb_path, 'r', encoding='utf-8') as f:
                                for idx, line in enumerate(f):
                                    if not line.strip():
                                        continue
                                    if idx < start_offset:
                                        continue
                                    lines_buf.append(line)
                            # Sampling strategies
                            if sample_strategy == 'tail':
                                sample = lines_buf[-limit_val:] if limit_val else lines_buf
                            elif sample_strategy == 'stratified' and limit_val:
                                step = max(1, len(lines_buf) // limit_val)
                                sample = [lines_buf[i] for i in range(0, len(lines_buf), step)][:limit_val]
                            else:  # head
                                sample = lines_buf[:limit_val] if limit_val else lines_buf

                            for line in sample:
                                try:
                                    obj = json.loads(line)
                                except Exception:
                                    continue
                                stmt = obj.get('statement', '')
                                if not stmt:
                                    continue
                                checked_total += 1
                                new_stmt, old_pred, new_pred = translate_statement(stmt)
                                if old_pred is not None and new_stmt != stmt:
                                    changed_total += 1
                                    per_predicate[old_pred] = per_predicate.get(old_pred, 0) + 1
                                    if len(examples) < 10:
                                        examples.append(f"{old_pred} -> {new_pred}: {stmt} => {new_stmt}")
                            lines = [
                                f"Dry run: {changed_total} changes over {checked_total} checked lines",
                                f"Allowlist: {sorted(list(allow_set)) if allow_set else '<none>'}",
                                f"Excludelist: {sorted(list(exclude_set)) if exclude_set else '<none>'}",
                                "Per-predicate changes:" if per_predicate else "Per-predicate changes: <none>",
                            ]
                            for k,v in sorted(per_predicate.items(), key=lambda x: x[1], reverse=True)[:20]:
                                lines.append(f"- {k}: {v}")
                            if examples:
                                lines.append("Examples:")
                                lines += [f"- {e}" for e in examples]
                            report_text = "\n".join(lines)
                            # Optional report write
                            if report_path:
                                report_written = False
                                report_error = None
                                try:
                                    rp = Path(report_path)
                                    rp.parent.mkdir(parents=True, exist_ok=True)
                                    rp.write_text(report_text, encoding='utf-8')
                                    report_written = True
                                except Exception:
                                    report_error = traceback.format_exc().splitlines()[-1]
                                # Add explicit confirmation line
                                if report_written:
                                    report_text += f"\n\nReport: written to {report_path}"
                                elif report_error:
                                    report_text += f"\n\nReport: failed to write to {report_path} ({report_error})"
                            result = {"content": [{"type": "text", "text": report_text}]}
                        except Exception as e:
                            result = {"content": [{"type": "text", "text": f"Error during dry run: {e}"}]}
                    else:
                        # Write pass supports limit_mode and start_offset
                        try:
                            self._acquire_lock()
                            tmp_path = self.kb_path.with_suffix(self.kb_path.suffix + ".tmp")
                            changes_applied = 0
                            with open(self.kb_path, 'r', encoding='utf-8') as src, open(tmp_path, 'w', encoding='utf-8') as dst:
                                for idx, line in enumerate(src):
                                    if not line.strip():
                                        dst.write(line)
                                        continue
                                    try:
                                        obj = json.loads(line)
                                    except Exception:
                                        dst.write(line)
                                        continue
                                    stmt = obj.get('statement', '')
                                    if not stmt:
                                        dst.write(line)
                                        continue
                                    checked_total += 1
                                    if idx < start_offset:
                                        dst.write(json.dumps(obj, ensure_ascii=False) + "\n")
                                        continue
                                    process_line = True
                                    if limit_mode == 'lines' and limit_val:
                                        process_line = (idx - start_offset) < limit_val
                                    if process_line:
                                        new_stmt, old_pred, new_pred = translate_statement(stmt)
                                        if old_pred is not None and new_stmt != stmt:
                                            obj['statement'] = new_stmt
                                            changed_total += 1
                                            changes_applied += 1
                                            per_predicate[old_pred] = per_predicate.get(old_pred, 0) + 1
                                        if limit_mode == 'changes' and limit_val and changes_applied >= limit_val:
                                            dst.write(json.dumps(obj, ensure_ascii=False) + "\n")
                                            # copy rest unchanged
                                            for rest in src:
                                                dst.write(rest)
                                            break
                                    dst.write(json.dumps(obj, ensure_ascii=False) + "\n")
                            os.replace(tmp_path, self.kb_path)
                            self._append_audit("bulk_translate_predicates", {
                                "mapping": mapping,
                                "allow": sorted(list(allow_set)) if allow_set else None,
                                "exclude": sorted(list(exclude_set)) if exclude_set else None,
                                "checked": checked_total,
                                "changed": changed_total,
                                "per_predicate": per_predicate
                            })
                            text_lines = [
                                f"OK: changed {changed_total} over {checked_total} checked lines\n" +
                                ("Per-predicate changes:\n" + "\n".join([f"- {k}: {v}" for k,v in sorted(per_predicate.items(), key=lambda x: x[1], reverse=True)[:20]]) if per_predicate else "")
                            ]
                            out_text = "".join(text_lines).strip()
                            # Optional live-run report
                            if report_path:
                                try:
                                    rp = Path(report_path)
                                    rp.parent.mkdir(parents=True, exist_ok=True)
                                    rp.write_text(out_text, encoding='utf-8')
                                    out_text += f"\n\nReport: written to {report_path}"
                                except Exception:
                                    err = traceback.format_exc().splitlines()[-1]
                                    out_text += f"\n\nReport: failed to write to {report_path} ({err})"
                            result = {"content": [{"type": "text", "text": out_text}]}
                        except Exception as e:
                            result = {"content": [{"type": "text", "text": f"Error during write: {e}"}]}
                        finally:
                            self._release_lock()
            elif tool_name == "project_list_snapshots":
                hub_path = str(tool_args.get("hub_path", "")).strip() or self.hub_path_env
                limit = int(tool_args.get("limit", 20))
                if not hub_path:
                    result = {"content": [{"type": "text", "text": "Missing 'hub_path'"}]}
                else:
                    try:
                        hub = Path(hub_path)
                        if not hub.exists():
                            result = {"content": [{"type": "text", "text": "<hub not found>"}]}
                        else:
                            snaps = [p for p in hub.iterdir() if p.is_dir() and p.name.startswith('snapshot_')]
                            snaps.sort(key=lambda p: p.name, reverse=True)
                            snaps = snaps[:limit]
                            lines = [str(p) for p in snaps]
                            text = "\n".join(lines) or "<none>"
                            result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            elif tool_name == "project_hub_digest":
                hub_path = str(tool_args.get("hub_path", "")).strip() or self.hub_path_env
                limit_files = int(tool_args.get("limit_files", 3))
                max_chars = int(tool_args.get("max_chars", 20000))
                if not hub_path:
                    result = {"content": [{"type": "text", "text": "Missing 'hub_path'"}]}
                else:
                    try:
                        hub = Path(hub_path)
                        if not hub.exists():
                            result = {"content": [{"type": "text", "text": "<hub not found>"}]}
                        else:
                            snaps = [p for p in hub.iterdir() if p.is_dir() and p.name.startswith('snapshot_')]
                            snaps.sort(key=lambda p: p.name, reverse=True)
                            snaps = snaps[:limit_files]
                            parts = []
                            for s in snaps:
                                md = s / 'SNAPSHOT.md'
                                js = s / 'snapshot.json'
                                if md.exists():
                                    parts.append((md.name, md.read_text(encoding='utf-8')))
                                if js.exists():
                                    parts.append((js.name, js.read_text(encoding='utf-8')))
                            combined = "\n\n---\n\n".join([f"## {n}\n\n{c}" for n,c in parts])
                            text = combined[:max_chars]
                            result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = {"error": str(e)}
            
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": result
        }
        await self.send_response(response)
        
    async def search_knowledge(self, query, limit=10):
        """Search the knowledge base"""
        facts = []
        query_lower = query.lower()
        
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            fact = json.loads(line)
                            statement = fact.get('statement', '')
                            if query_lower in statement.lower():
                                facts.append(statement)
                                if len(facts) >= limit:
                                    break
                        except:
                            pass
        except Exception as e:
            logger.error(f"KB search error: {e}")
            
        return {
            "facts": facts,
            "count": len(facts),
            "query": query
        }
        
    async def get_system_status(self):
        """Get system status"""
        try:
            # Count facts
            fact_count = 0
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        fact_count += 1
                        
            return {
                "status": "operational",
                "kb_facts": fact_count,
                "kb_path": str(self.kb_path),
                "server": "HAK_GAL MCP v1.0"
            }
        except Exception as e:
            return {"error": str(e)}
            
    async def list_recent_facts(self, count=5):
        """List recent facts"""
        facts = []
        
        try:
            with open(self.kb_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
            # Get last N facts
            for line in reversed(lines):
                if line.strip():
                    try:
                        fact = json.loads(line)
                        facts.append(fact.get('statement', ''))
                        if len(facts) >= count:
                            break
                    except:
                        pass
                        
            return {"facts": facts}
        except Exception as e:
            return {"error": str(e)}
            
    async def handle_request(self, request):
        """Main request handler"""
        method = request.get("method", "")
        request_id_present = "id" in request
        
        logger.debug(f"Handling method: {method}")
        
        if method == "notifications/initialized":
            # MCP notification: do not respond
            return
        
        if method == "initialize":
            await self.handle_initialize(request)
        elif method == "tools/list":
            await self.handle_list_tools(request)
        elif method == "tools/call":
            await self.handle_tool_call(request)
        elif method == "resources/list":
            if request_id_present:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "result": {"resources": []}
                }
                await self.send_response(response)
        elif method == "prompts/list":
            if request_id_present:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "result": {"prompts": []}
                }
                await self.send_response(response)
        elif method == "shutdown":
            self.running = False
            if request_id_present:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "result": None
                }
                await self.send_response(response)
        else:
            # Unknown method
            if request_id_present:
                response = {
                    "jsonrpc": "2.0",
                    "id": request.get("id", 1),
                    "error": {
                        "code": -32601,
                        "message": f"Method not found: {method}"
                    }
                }
                await self.send_response(response)
            
    async def run(self):
        """Main server loop"""
        logger.info("HAK_GAL MCP Server starting...")
        logger.info(f"KB Path: {self.kb_path}")
        logger.info(f"KB Exists: {self.kb_path.exists()}")
        
        # Send server info on startup
        startup_info = {
            "jsonrpc": "2.0",
            "method": "server/ready",
            "params": {
                "name": "HAK_GAL MCP",
                "version": "1.0.0"
            }
        }
        await self.send_response(startup_info)
        
        # Main loop
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
                break
            except Exception as e:
                logger.error(f"Server error: {e}")
                logger.error(traceback.format_exc())
                
        logger.info("Server shutting down...")

async def main():
    """Entry point"""
    server = HAKGALMCPServer()
    await server.run()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
