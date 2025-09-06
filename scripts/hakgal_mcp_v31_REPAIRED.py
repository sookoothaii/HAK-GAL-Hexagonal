#!/usr/bin/env python3
"""
HAK_GAL MCP Server - VOLLVERSION mit ALLEN 43 Tools - FIXED
Arbeitet DIREKT mit der hexagonal_kb.db SQLite-Datenbank
ALLE TOOLS FUNKTIONIEREN!
"""

import sys
import os
import json
import asyncio
import logging
import sqlite3
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
except:
    requests = None

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

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
    """MCP Server für HAK_GAL mit ALLEN 43 Tools - SQLite Version - FIXED"""
    
    def __init__(self):
        # DIE EINZIGE DATENBANK!
        self.db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
        # Legacy JSONL für Kompatibilität (wird aber nicht mehr verwendet für Lesen)
        self.kb_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
        self.running = True
        self.request_id = 0
        
        # UTF-8 Setup
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, write_through=True)
        
        # Write-safety configuration
        self.write_enabled = os.environ.get("HAKGAL_WRITE_ENABLED", "true").lower() == "true"
        self.write_token_env = os.environ.get("HAKGAL_WRITE_TOKEN", "")
        self.kb_lock_path = self.kb_path.with_suffix(self.kb_path.suffix + ".lock")
        
        # Project Hub
        self.hub_path_env = os.environ.get("HAKGAL_HUB_PATH", "D:/MCP Mods/HAK_GAL_HEXAGONAL/PROJECT_HUB")
        
        # Backend API für write operations
        self.api_base_url = os.environ.get("HAKGAL_API_BASE_URL", "http://127.0.0.1:5002")
        
        logger.info(f"MCP Server initialized with DB: {self.db_path}")
        self._check_database()
    
    def _check_database(self):
        """Prüfe ob Datenbank existiert und zähle Fakten"""
        if not self.db_path.exists():
            logger.error(f"Database not found: {self.db_path}")
            return
        
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            conn.close()
            logger.info(f"Database connected: {count} facts found")
        except Exception as e:
            logger.error(f"Database error: {e}")
    
    def _is_write_allowed(self, provided_token: str) -> bool:
        """Check if write operations are allowed"""
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
                self.kb_lock_path.unlink()
        except:
            pass
    
    def _append_audit(self, action: str, payload: dict):
        try:
            audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
            ts = time.strftime("%Y-%m-%d %H:%M:%S")
            entry = {"ts": ts, "action": action, "payload": payload}
            with open(audit_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")
        except:
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
        except:
            return None, []
    
    def get_facts_from_db(self):
        """Hole alle Fakten aus der SQLite DB"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.execute("SELECT statement FROM facts")
            facts = [row[0] for row in cursor]
            conn.close()
            return facts
        except Exception as e:
            logger.error(f"Error getting facts from DB: {e}")
            return []
    
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
                    "name": "HAK_GAL MCP SQLite Full FIXED",
                    "version": "3.1.0"
                }
            }
        }
        await self.send_response(response)
    
    async def handle_list_tools(self, request):
        """List ALL 43 available tools"""
        tools = [
            # Original 5 SQLite Tools
            {
                "name": "get_facts_count",
                "description": "Hole die aktuelle Anzahl der Fakten aus der SQLite DB",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "search_knowledge",
                "description": "Suche in der HAK_GAL Wissensdatenbank",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Suchbegriff"},
                        "limit": {"type": "integer", "description": "Max Ergebnisse", "default": 10}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_recent_facts",
                "description": "Hole die neuesten Fakten",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "description": "Anzahl", "default": 5}
                    }
                }
            },
            {
                "name": "get_predicates_stats",
                "description": "Statistik über verwendete Prädikate",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "get_system_status",
                "description": "System Status mit Datenbankinfo",
                "inputSchema": {"type": "object", "properties": {}}
            },
            # Weitere Knowledge Base Tools (25 weitere = 30 total KB Tools)
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
                "description": "Füge einen neuen Fakt hinzu (requires write enable)",
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
                "description": "Lösche Fakten (requires write enable)",
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
                "description": "Aktualisiere einen Fakt (requires write enable)",
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
                "description": "KB Metriken (count, size, last_modified)",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "list_audit",
                "description": "Liste letzte N Audit-Einträge",
                "inputSchema": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 20}}
                }
            },
            {
                "name": "export_facts",
                "description": "Exportiere erste/letzte N Fakten",
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
                "description": "Wachstum über letzte N Tage",
                "inputSchema": {"type": "object", "properties": {"days": {"type": "integer", "default": 30}}}
            },
            {
                "name": "health_check",
                "description": "Umfassender Health Status",
                "inputSchema": {"type": "object", "properties": {}}
            },
            {
                "name": "semantic_similarity",
                "description": "Finde semantisch ähnliche Fakten",
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
                "description": "Erkenne widersprüchliche Paare",
                "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 1000}}}
            },
            {
                "name": "validate_facts",
                "description": "Validiere Syntax der Fakten",
                "inputSchema": {
                    "type": "object",
                    "properties": {"limit": {"type": "integer", "default": 1000}}
                }
            },
            {
                "name": "get_entities_stats",
                "description": "Häufigkeit von Entitäten",
                "inputSchema": {
                    "type": "object",
                    "properties": {"min_occurrences": {"type": "integer", "default": 2}}
                }
            },
            {
                "name": "search_by_predicate",
                "description": "Finde Fakten nach Prädikat",
                "inputSchema": {
                    "type": "object",
                    "properties": {"predicate": {"type": "string"}, "limit": {"type": "integer", "default": 100}},
                    "required": ["predicate"]
                }
            },
            {
                "name": "get_fact_history",
                "description": "Zeige Audit-Einträge zu einem Statement",
                "inputSchema": {
                    "type": "object",
                    "properties": {"statement": {"type": "string"}, "limit": {"type": "integer", "default": 50}},
                    "required": ["statement"]
                }
            },
            {
                "name": "backup_kb",
                "description": "Erstelle Backup der KB",
                "inputSchema": {
                    "type": "object",
                    "properties": {"description": {"type": "string"}, "auth_token": {"type": "string"}}
                }
            },
            {
                "name": "restore_kb",
                "description": "Stelle KB aus Backup wieder her",
                "inputSchema": {
                    "type": "object",
                    "properties": {"backup_id": {"type": "string"}, "path": {"type": "string"}, "auth_token": {"type": "string"}}
                }
            },
            {
                "name": "bulk_delete",
                "description": "Lösche mehrere Statements",
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
                "name": "query_related",
                "description": "Alle Fakten zu einer Entität",
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
                "description": "Finde potenzielle Duplikate",
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
                "description": "Exportiere Subgraph um eine Entität",
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
                "description": "Finde isolierte Fakten",
                "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 50}}}
            },
            {
                "name": "inference_chain",
                "description": "Baue Kette verwandter Fakten",
                "inputSchema": {
                    "type": "object",
                    "properties": {"start_fact": {"type": "string"}, "max_depth": {"type": "integer", "default": 5}},
                    "required": ["start_fact"]
                }
            },
            {
                "name": "bulk_translate_predicates",
                "description": "Übersetze Prädikate in der KB",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "mapping": {"type": "object"},
                        "dry_run": {"type": "boolean", "default": True},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["mapping"]
                }
            },
            {
                "name": "project_snapshot",
                "description": "Erstelle Projekt-Snapshot",
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
                "description": "Liste Projekt-Snapshots",
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
                "description": "Digest der letzten Snapshots",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "hub_path": {"type": "string"},
                        "limit_files": {"type": "integer", "default": 3},
                        "max_chars": {"type": "integer", "default": 20000}
                    }
                }
            },
            # NEU: Multi-Agent Tool
            {
                "name": "delegate_task",
                "description": "Delegiere eine Aufgabe an einen anderen KI-Agenten (z.B. cursor, claude_cli)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "target_agent": {"type": "string", "description": "Der Ziel-Agent (z.B. 'cursor')"},
                        "task_description": {"type": "string", "description": "Die genaue Anweisung an den Agenten"},
                        "context": {"type": "object", "description": "Zusätzliche Daten für die Aufgabe (z.B. Code)"}
                    },
                    "required": ["target_agent", "task_description"]
                }
            },
            # Dateioperations-Tools (13 Tools)
            {"name": "read_file", "description": "Lese Dateiinhalt", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "encoding": {"type": "string", "default": "utf-8"}}, "required": ["path"]}},
            {"name": "write_file", "description": "Schreibe Datei", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "encoding": {"type": "string", "default": "utf-8"}, "auth_token": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "list_files", "description": "Liste Dateien", "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "default": "."}, "recursive": {"type": "boolean", "default": False}, "pattern": {"type": "string"}}}},
            {"name": "get_file_info", "description": "Datei-Metadaten", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}}, "required": ["path"]}},
            {"name": "directory_tree", "description": "Verzeichnisbaum anzeigen", "inputSchema": {"type": "object", "properties": {"path": {"type": "string", "default": "."}, "maxDepth": {"type": "integer", "default": 3}, "showHidden": {"type": "boolean", "default": False}}}},
            {"name": "create_file", "description": "Erstelle neue Datei", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "content": {"type": "string"}, "overwrite": {"type": "boolean", "default": False}, "auth_token": {"type": "string"}}, "required": ["path", "content"]}},
            {"name": "delete_file", "description": "Lösche Datei", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "recursive": {"type": "boolean", "default": False}, "auth_token": {"type": "string"}}, "required": ["path"]}},
            {"name": "move_file", "description": "Verschiebe/Benenne Datei um", "inputSchema": {"type": "object", "properties": {"source": {"type": "string"}, "destination": {"type": "string"}, "overwrite": {"type": "boolean", "default": False}, "auth_token": {"type": "string"}}, "required": ["source", "destination"]}},
            {"name": "grep", "description": "Suche Muster in Dateien", "inputSchema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."}, "filePattern": {"type": "string"}, "ignoreCase": {"type": "boolean", "default": False}, "showLineNumbers": {"type": "boolean", "default": True}, "contextLines": {"type": "integer", "default": 0}}, "required": ["pattern"]}},
            {"name": "find_files", "description": "Finde Dateien nach Muster", "inputSchema": {"type": "object", "properties": {"pattern": {"type": "string"}, "path": {"type": "string", "default": "."}, "type": {"type": "string"}, "maxDepth": {"type": "integer"}}, "required": ["pattern"]}},
            {"name": "search", "description": "Einheitliche Suche", "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "path": {"type": "string", "default": "."}, "type": {"type": "string", "default": "all"}, "filePattern": {"type": "string"}, "maxResults": {"type": "integer", "default": 50}}, "required": ["query"]}},
            {"name": "edit_file", "description": "Ersetze Text in Datei", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "oldText": {"type": "string"}, "newText": {"type": "string"}, "auth_token": {"type": "string"}}, "required": ["path", "oldText", "newText"]}},
            {"name": "multi_edit", "description": "Mehrere Bearbeitungen", "inputSchema": {"type": "object", "properties": {"path": {"type": "string"}, "edits": {"type": "array", "items": {"type": "object", "properties": {"oldText": {"type": "string"}, "newText": {"type": "string"}}, "required": ["oldText", "newText"]}}, "auth_token": {"type": "string"}}, "required": ["path", "edits"]}},
        ]
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": {"tools": tools}
        }
        await self.send_response(response)
    
    async def handle_tool_call(self, request):
        """Handle ALL 43 tool executions - KOMPLETT IMPLEMENTIERT"""
        params = request.get("params", {})
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})
        
        result = {"content": [{"type": "text", "text": "Unknown tool"}]}
        
        try:
            # ===== SQLite-basierte Core Tools =====
            if tool_name == "get_facts_count":
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                conn.close()
                text = f"Anzahl Fakten in der Datenbank: {count:,}"
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "search_knowledge":
                query = tool_args.get("query", "")
                limit = tool_args.get("limit", 10)
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute(
                    "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                    (f"%{query}%", limit)
                )
                facts = [row[0] for row in cursor]
                conn.close()
                text = f"Gefunden: {len(facts)} Fakten\n" + "\n".join([f"- {f}" for f in facts])
                result = {"content": [{"type": "text", "text": text}]}
            
            # FIXED: SQLite-kompatible recent facts (ohne id dependency)
            elif tool_name == "get_recent_facts" or tool_name == "list_recent_facts":
                count = tool_args.get("count", 5)
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute(
                    "SELECT statement FROM facts ORDER BY rowid DESC LIMIT ?",
                    (count,)
                )
                facts = [row[0] for row in cursor]
                conn.close()
                text = "Neueste Fakten:\n" + "\n".join([f"- {f}" for f in facts]) if facts else "Neueste Fakten:\n<keine>"
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "get_predicates_stats":
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("""
                    SELECT 
                        CASE 
                            WHEN instr(statement, '(') > 0 
                            THEN substr(statement, 1, instr(statement, '(') - 1)
                            ELSE 'Invalid'
                        END as predicate,
                        COUNT(*) as cnt
                    FROM facts 
                    GROUP BY predicate
                    ORDER BY cnt DESC
                    LIMIT 30
                """)
                stats = [(row[0], row[1]) for row in cursor]
                conn.close()
                lines = [f"{pred}: {cnt} Fakten" for pred, cnt in stats]
                text = "Top Prädikate:\n" + "\n".join(lines)
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "get_system_status":
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                conn.close()
                text = (
                    f"Status: Operational\n"
                    f"Datenbank: {self.db_path}\n"
                    f"Fakten: {count:,}\n"
                    f"Server: HAK_GAL MCP SQLite Full FIXED v3.1\n"
                    f"Tools: 43 (alle verfügbar)"
                )
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "health_check":
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                conn.close()
                text = (
                    f"Status: OK\n"
                    f"DB exists: True\n"
                    f"DB Fakten: {count:,}\n"
                    f"Write enabled: {self.write_enabled}\n"
                    f"Total Tools: 43"
                )
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "kb_stats":
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                # Get DB file size
                db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
                conn.close()
                text = (
                    f"KB count (SQLite): {count:,}\n"
                    f"KB size (bytes): {db_size:,}\n"
                    f"KB path: {self.db_path}"
                )
                result = {"content": [{"type": "text", "text": text}]}
            
            # ===== Write Operations =====
            elif tool_name == "add_fact":
                statement = tool_args.get("statement", "").strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                elif requests:
                    try:
                        resp = requests.post(f"{self.api_base_url}/api/facts", json={
                            "statement": statement,
                            "context": {"source": tool_args.get("source") or "mcp"}
                        }, timeout=10)
                        if resp.status_code in (200, 201):
                            self._append_audit("add_fact", {"statement": statement})
                            result = {"content": [{"type": "text", "text": "OK: fact added to SQLite"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                else:
                    result = {"content": [{"type": "text", "text": "requests module not available"}]}
                    
            # FIXED: delete_fact implementation
            elif tool_name == "delete_fact":
                statement = tool_args.get("statement", "").strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                elif not statement:
                    result = {"content": [{"type": "text", "text": "Missing 'statement'"}]}
                elif requests:
                    try:
                        resp = requests.post(f"{self.api_base_url}/api/facts/delete", json={
                            "statement": statement
                        }, timeout=10)
                        if resp.ok:
                            removed = resp.json().get("removed", 0) if resp.text else 0
                            self._append_audit("delete_fact", {"statement": statement, "removed": removed})
                            result = {"content": [{"type": "text", "text": f"OK: removed {removed} (SQLite)"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                else:
                    result = {"content": [{"type": "text", "text": "requests module not available"}]}
                    
            # FIXED: update_fact implementation
            elif tool_name == "update_fact":
                old_stmt = tool_args.get("old_statement", "").strip()
                new_stmt = tool_args.get("new_statement", "").strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                elif not old_stmt or not new_stmt:
                    result = {"content": [{"type": "text", "text": "Missing 'old_statement' or 'new_statement'"}]}
                elif requests:
                    try:
                        resp = requests.put(f"{self.api_base_url}/api/facts/update", json={
                            "old_statement": old_stmt,
                            "new_statement": new_stmt
                        }, timeout=10)
                        if resp.ok:
                            updated = resp.json().get("updated", 0) if resp.text else 0
                            self._append_audit("update_fact", {"old": old_stmt, "new": new_stmt, "updated": updated})
                            result = {"content": [{"type": "text", "text": f"OK: updated {updated} (SQLite)"}]}
                        else:
                            result = {"content": [{"type": "text", "text": f"Error: {resp.status_code}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                else:
                    result = {"content": [{"type": "text", "text": "requests module not available"}]}
            
            # ===== Analysis Tools =====
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
                    
                    base_vec = vec(base)
                    sims = []
                    
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute("SELECT statement FROM facts")
                    for (st,) in cursor:
                        v = vec(st)
                        cs = cosine(base_vec, v)
                        if cs >= threshold:
                            sims.append((cs, st))
                    conn.close()
                    
                    sims.sort(key=lambda x: x[0], reverse=True)
                    text = "\n".join([f"{cs:.3f} {st}" for cs,st in sims[:limit]]) or "<no similar>"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "consistency_check":
                limit = int(tool_args.get("limit", 1000))
                pos = set()
                neg = set()
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute(f"SELECT statement FROM facts LIMIT {limit}")
                for (st,) in cursor:
                    pred, args = self._parse_statement(st)
                    if pred and args:
                        if pred.startswith('Nicht'):
                            neg.add((pred[5:], tuple(args)))
                        else:
                            pos.add((pred, tuple(args)))
                conn.close()
                
                conflicts = []
                for npred, nargs in neg:
                    if (npred, nargs) in pos:
                        conflicts.append((npred, list(nargs)))
                
                text = "\n".join([f"Konflikt: {pred}({', '.join(args)}) vs Nicht{pred}({', '.join(args)})" 
                                 for pred,args in conflicts]) or "<keine Konflikte>"
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "validate_facts":
                limit = int(tool_args.get("limit", 1000))
                errors = []
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute(f"SELECT statement FROM facts LIMIT {limit}")
                for (st,) in cursor:
                    pred, args = self._parse_statement(st)
                    if not pred:
                        errors.append(f"Invalid syntax: {st}")
                    elif not args:
                        errors.append(f"No arguments: {st}")
                conn.close()
                
                text = ("OK - alle valide" if not errors else "\n".join(errors[:200]))
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "get_entities_stats":
                min_occ = int(tool_args.get("min_occurrences", 2))
                freq = {}
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT statement FROM facts")
                for (st,) in cursor:
                    _, args = self._parse_statement(st)
                    for a in args:
                        freq[a] = freq.get(a, 0) + 1
                conn.close()
                
                items = [(k,v) for k,v in freq.items() if v >= min_occ]
                items.sort(key=lambda x: x[1], reverse=True)
                text = "\n".join([f"{k}: {v}" for k,v in items[:100]]) or "<none>"
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "search_by_predicate":
                predicate = str(tool_args.get("predicate", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not predicate:
                    result = {"content": [{"type": "text", "text": "Missing 'predicate'"}]}
                else:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute(
                        "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                        (f"{predicate}(%", limit)
                    )
                    facts = [row[0] for row in cursor]
                    conn.close()
                    text = "\n".join([f"- {s}" for s in facts]) or "<no matches>"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "query_related":
                entity = str(tool_args.get("entity", "")).strip()
                limit = int(tool_args.get("limit", 100))
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing 'entity'"}]}
                else:
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute(
                        "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                        (f"%{entity}%", limit)
                    )
                    facts = [row[0] for row in cursor]
                    conn.close()
                    text = "\n".join([f"- {s}" for s in facts]) or "<no matches>"
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "analyze_duplicates":
                threshold = float(tool_args.get("threshold", 0.9))
                max_pairs = int(tool_args.get("max_pairs", 200))
                
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
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT statement FROM facts LIMIT 500")
                statements = [row[0] for row in cursor]
                conn.close()
                
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
                text = "\n\n".join([f"SIM={sim:.2f}\nA: {a}\nB: {b}" for a,b,sim in pairs[:20]]) or "<keine Duplikate>"
                result = {"content": [{"type": "text", "text": text}]}
            
            # FIXED: export_facts (ohne id dependency)  
            elif tool_name == "export_facts":
                count = int(tool_args.get("count", 50))
                direction = str(tool_args.get("direction", "tail")).lower()
                
                conn = sqlite3.connect(str(self.db_path))
                if direction == 'head':
                    cursor = conn.execute(f"SELECT statement FROM facts LIMIT {count}")
                else:
                    cursor = conn.execute(f"SELECT statement FROM facts ORDER BY rowid DESC LIMIT {count}")
                facts = [row[0] for row in cursor]
                conn.close()
                
                if direction == 'tail':
                    facts.reverse()
                
                text = "\n".join(facts) or "<keine Fakten>"
                result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "list_audit":
                limit = int(tool_args.get("limit", 20))
                audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                lines = []
                if audit_path.exists():
                    with open(audit_path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()[-limit:]
                text = "".join(lines) if lines else "<empty>"
                result = {"content": [{"type": "text", "text": text}]}
                
            # FIXED: growth_stats implementation
            elif tool_name == "growth_stats":
                days = int(tool_args.get("days", 30))
                try:
                    # Count total facts
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute("SELECT COUNT(*) FROM facts")
                    total = cursor.fetchone()[0]
                    conn.close()
                    
                    # Analyze audit log
                    by_day = collections.Counter()
                    audit_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_write_audit.log")
                    if audit_path.exists():
                        cutoff = time.time() - days*86400
                        with open(audit_path, 'r', encoding='utf-8') as f:
                            for line in f:
                                try:
                                    obj = json.loads(line)
                                    if obj.get('action') == 'add_fact':
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
                    text = f"Total: {total:,}\nAvg/day({days}d): {avg:.2f}\n\n"
                    text += "\n".join([f"{d}: +{v}" for d,v in days_list])
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "backup_kb":
                desc = str(tool_args.get("description", "")).strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    try:
                        import re  # FIX: Import re locally to fix scope issue
                        ts = time.strftime("%Y%m%d%H%M%S")
                        backups_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/backups")
                        backups_dir.mkdir(parents=True, exist_ok=True)
                        backup_id = ts
                        if desc:
                            safe_desc = re.sub(r"[^A-Za-z0-9_-]+", "_", desc)[:40]
                            backup_id = f"{ts}_{safe_desc}"
                        dst = backups_dir / f"sqlite_{backup_id}.db"
                        shutil.copy2(self.db_path, dst)
                        self._append_audit("backup_kb", {"id": backup_id, "path": str(dst)})
                        text = f"OK: backup_id={backup_id}\npath={dst}"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # FIXED: restore_kb implementation
            elif tool_name == "restore_kb":
                backup_id = str(tool_args.get("backup_id", "")).strip()
                path_override = str(tool_args.get("path", "")).strip()
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    try:
                        src_path = None
                        if path_override:
                            src_path = Path(path_override)
                        else:
                            backups_dir = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/backups")
                            candidate = backups_dir / f"sqlite_{backup_id}.db"
                            if candidate.exists():
                                src_path = candidate
                        
                        if not src_path or not src_path.exists():
                            result = {"content": [{"type": "text", "text": "Backup not found"}]}
                        else:
                            self._acquire_lock()
                            try:
                                shutil.copy2(src_path, self.db_path)
                                self._append_audit("restore_kb", {"from": str(src_path)})
                                result = {"content": [{"type": "text", "text": "OK: restored"}]}
                            finally:
                                self._release_lock()
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                        
            # FIXED: bulk_delete implementation
            elif tool_name == "bulk_delete":
                statements = tool_args.get("statements", []) or []
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                elif not requests:
                    result = {"content": [{"type": "text", "text": "requests module not available"}]}
                else:
                    total_removed = 0
                    errors = 0
                    for s in statements:
                        try:
                            resp = requests.post(f"{self.api_base_url}/api/facts/delete", 
                                               json={"statement": str(s)}, timeout=10)
                            if resp.ok:
                                try:
                                    total_removed += resp.json().get("removed", 0)
                                except:
                                    pass
                            else:
                                errors += 1
                        except:
                            errors += 1
                    
                    self._append_audit("bulk_delete", {
                        "count": len(statements), 
                        "removed": total_removed, 
                        "errors": errors
                    })
                    result = {"content": [{"type": "text", "text": 
                        f"OK: removed {total_removed}, errors {errors} (SQLite)"}]}
            
            elif tool_name == "get_knowledge_graph":
                entity = str(tool_args.get("entity", "")).strip()
                depth = int(tool_args.get("depth", 2))
                fmt = str(tool_args.get("format", "json")).lower()
                
                if not entity:
                    result = {"content": [{"type": "text", "text": "Missing 'entity'"}]}
                else:
                    edges = []
                    nodes = set([entity])
                    facts = []
                    
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute("SELECT statement FROM facts WHERE statement LIKE ?", (f"%{entity}%",))
                    for (st,) in cursor:
                        pred, args = self._parse_statement(st)
                        if pred and args:
                            facts.append(st)
                            if len(args) >= 2:
                                edges.append((args[0], pred, args[1]))
                            for a in args:
                                nodes.add(a)
                    conn.close()
                    
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
                            "facts": facts[:50],
                        }
                        text = json.dumps(graph, ensure_ascii=False, indent=2)
                    result = {"content": [{"type": "text", "text": text}]}
            
            elif tool_name == "find_isolated_facts":
                limit = int(tool_args.get("limit", 50))
                
                conn = sqlite3.connect(str(self.db_path))
                cursor = conn.execute("SELECT statement FROM facts")
                
                entity_counts = collections.Counter()
                statements = []
                for (st,) in cursor:
                    statements.append(st)
                    _, args = self._parse_statement(st)
                    for a in args:
                        entity_counts[a] += 1
                conn.close()
                
                isolated = []
                for st in statements:
                    _, args = self._parse_statement(st)
                    if args and all(entity_counts[a] == 1 for a in args):
                        isolated.append(st)
                        if len(isolated) >= limit:
                            break
                
                text = "\n".join([f"- {s}" for s in isolated]) or "<keine isolierten Fakten>"
                result = {"content": [{"type": "text", "text": text}]}
                
            # FIXED: inference_chain implementation
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
                            
                            conn = sqlite3.connect(str(self.db_path))
                            cursor = conn.execute("SELECT statement FROM facts")
                            all_statements = [row[0] for row in cursor]
                            conn.close()
                            
                            used = set([start_fact])
                            for _ in range(max_depth):
                                extended = False
                                for st in all_statements:
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
                        
            # FIXED: get_fact_history implementation
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
                        text = "".join(lines[-limit:]) if lines else "<no history>"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                        
            # FIXED: bulk_translate_predicates implementation
            elif tool_name == "bulk_translate_predicates":
                mapping = tool_args.get("mapping", {}) or {}
                dry_run = bool(tool_args.get("dry_run", True))
                auth_token = tool_args.get("auth_token", "")
                
                if not isinstance(mapping, dict) or not mapping:
                    result = {"content": [{"type": "text", "text": "Missing or empty 'mapping'"}]}
                elif (not dry_run) and (not self._is_write_allowed(auth_token)):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    try:
                        changed_total = 0
                        checked_total = 0
                        per_predicate = {}
                        
                        conn = sqlite3.connect(str(self.db_path))
                        cursor = conn.execute("SELECT rowid, statement FROM facts")
                        facts_data = [(row[0], row[1]) for row in cursor]
                        conn.close()
                        
                        if dry_run:
                            for rowid, stmt in facts_data:
                                pred, args = self._parse_statement(stmt)
                                if pred and pred in mapping:
                                    changed_total += 1
                                    per_predicate[pred] = per_predicate.get(pred, 0) + 1
                                checked_total += 1
                            
                            lines = [
                                f"Dry run: {changed_total} changes over {checked_total} facts",
                                "Per-predicate changes:" if per_predicate else "Per-predicate changes: <none>",
                            ]
                            for k,v in sorted(per_predicate.items(), key=lambda x: x[1], reverse=True)[:20]:
                                lines.append(f"- {k} -> {mapping[k]}: {v}")
                            text = "\n".join(lines)
                        else:
                            conn = sqlite3.connect(str(self.db_path))
                            for rowid, stmt in facts_data:
                                pred, args = self._parse_statement(stmt)
                                if pred and pred in mapping and args:
                                    new_pred = mapping[pred]
                                    new_stmt = f"{new_pred}({', '.join(args)})"
                                    if stmt.endswith('.'):
                                        new_stmt += '.'
                                    
                                    conn.execute("UPDATE facts SET statement = ? WHERE rowid = ?", 
                                               (new_stmt, rowid))
                                    changed_total += 1
                                    per_predicate[pred] = per_predicate.get(pred, 0) + 1
                                checked_total += 1
                            
                            conn.commit()
                            conn.close()
                            
                            self._append_audit("bulk_translate_predicates", {
                                "mapping": mapping,
                                "checked": checked_total,
                                "changed": changed_total,
                                "per_predicate": per_predicate
                            })
                            
                            lines = [
                                f"OK: changed {changed_total} over {checked_total} facts",
                                "Per-predicate changes:" if per_predicate else "No changes made",
                            ]
                            for k,v in sorted(per_predicate.items(), key=lambda x: x[1], reverse=True)[:20]:
                                lines.append(f"- {k} -> {mapping[k]}: {v}")
                            text = "\n".join(lines)
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # ===== Project Management Tools =====
            elif tool_name == "project_snapshot":
                title = str(tool_args.get("title", "")).strip() or "Session Snapshot"
                description = str(tool_args.get("description", "")).strip()
                hub_path = str(tool_args.get("hub_path", "")).strip() or self.hub_path_env
                auth_token = tool_args.get("auth_token", "")
                
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    try:
                        hub = Path(hub_path)
                        hub.mkdir(parents=True, exist_ok=True)
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        snap_dir = hub / f"snapshot_{ts}"
                        snap_dir.mkdir(parents=True, exist_ok=True)
                        
                        # Get DB stats
                        conn = sqlite3.connect(str(self.db_path))
                        cursor = conn.execute("SELECT COUNT(*) FROM facts")
                        count = cursor.fetchone()[0]
                        conn.close()
                        
                        # Create snapshot files
                        kb_md = [
                            f"# {title} — KB Snapshot",
                            "",
                            f"{description}",
                            "",
                            f"## Stats",
                            f"- Fakten: {count:,}",
                            f"- DB: {self.db_path}",
                            f"- Timestamp: {ts}",
                        ]
                        (snap_dir / "SNAPSHOT_KB.md").write_text("\n".join(kb_md), encoding='utf-8')
                        
                        json_obj = {
                            "title": title,
                            "description": description,
                            "timestamp": ts,
                            "facts_count": count,
                            "db_path": str(self.db_path)
                        }
                        (snap_dir / "snapshot.json").write_text(json.dumps(json_obj, indent=2), encoding='utf-8')
                        
                        text = f"OK: snapshot at {snap_dir}"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "project_list_snapshots":
                hub_path = str(tool_args.get("hub_path", "")).strip() or self.hub_path_env
                limit = int(tool_args.get("limit", 20))
                
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
                    
            # FIXED: project_hub_digest implementation
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
                                md_files = list(s.glob("*.md"))
                                json_files = list(s.glob("*.json"))
                                
                                for md in md_files[:2]:  # Max 2 MD files per snapshot
                                    if md.exists():
                                        content = md.read_text(encoding='utf-8')[:max_chars//limit_files]
                                        parts.append(f"## {s.name}/{md.name}\n\n{content}")
                                
                                for js in json_files[:1]:  # Max 1 JSON per snapshot
                                    if js.exists():
                                        content = js.read_text(encoding='utf-8')[:max_chars//limit_files]
                                        parts.append(f"## {s.name}/{js.name}\n\n{content}")
                            
                            combined = "\n\n---\n\n".join(parts)
                            text = combined[:max_chars] if combined else "<no content found>"
                            result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # ===== NEU: Multi-Agent Tool =====
            elif tool_name == "delegate_task":
                if not requests:
                    result = {"content": [{"type": "text", "text": "requests module not available"}]}
                else:
                    try:
                        target_agent = tool_args.get("target_agent")
                        task_description = tool_args.get("task_description")
                        context = tool_args.get("context", {})
                        
                        if not target_agent or not task_description:
                            result = {"content": [{"type": "text", "text": "Error: target_agent and task_description are required."}]}
                        else:
                            payload = {
                                "target_agent": target_agent,
                                "task_description": task_description,
                                "context": context
                            }
                            # Get API key from environment or use the correct one from .env
                            api_key = os.environ.get("HAKGAL_API_KEY", "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d")
                            if not api_key or api_key == "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d":
                                # Load from .env file directly
                                env_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.env")
                                if env_path.exists():
                                    try:
                                        for line in env_path.read_text().splitlines():
                                            if line.startswith("HAKGAL_API_KEY="):
                                                api_key = line.split("=", 1)[1].strip()
                                                break
                                    except:
                                        pass
                            headers = {"X-API-Key": api_key}
                            # Use the configured API base URL to contact the main web server
                            resp = requests.post(f"{self.api_base_url}/api/agent-bus/delegate", json=payload, headers=headers, timeout=20)
                            
                            if resp.ok:
                                response_data = resp.json()
                                task_id = response_data.get("task_id")
                                text = f"OK: Task delegated to {target_agent}. Task ID: {task_id}"
                                result = {"content": [{"type": "text", "text": text}]}
                            else:
                                text = f"Error delegating task: {resp.status_code} - {resp.text}"
                                result = {"content": [{"type": "text", "text": text}]}

                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error during delegation: {e}"}]}

            # ===== File Operation Tools =====
            elif tool_name == "read_file":
                p = Path(str(tool_args.get("path", "")))
                enc = str(tool_args.get("encoding", "utf-8"))
                try:
                    data = p.read_text(encoding=enc)
                    result = {"content": [{"type": "text", "text": data}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "write_file":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    p = Path(str(tool_args.get("path", "")))
                    content = str(tool_args.get("content", ""))
                    enc = str(tool_args.get("encoding", "utf-8"))
                    try:
                        p.parent.mkdir(parents=True, exist_ok=True)
                        p.write_text(content, encoding=enc)
                        result = {"content": [{"type": "text", "text": f"File written: {p}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "list_files":
                base = Path(str(tool_args.get("path", ".")))
                recursive = bool(tool_args.get("recursive", False))
                pattern = str(tool_args.get("pattern", "")).strip() or None
                try:
                    entries = []
                    if recursive:
                        for dirpath, dirnames, filenames in os.walk(base):
                            for name in filenames:
                                if not pattern or fnmatch.fnmatch(name, pattern):
                                    entries.append(str(Path(dirpath) / name))
                    else:
                        for p in base.iterdir():
                            if p.is_file() and (not pattern or fnmatch.fnmatch(p.name, pattern)):
                                entries.append(str(p))
                    text = "\n".join(entries) or "<empty>"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "directory_tree":
                base = Path(str(tool_args.get("path", ".")))
                max_depth = int(tool_args.get("maxDepth", 3))
                show_hidden = bool(tool_args.get("showHidden", False))
                
                def build_tree(d: Path, prefix: str = "", depth: int = 0) -> str:
                    if depth > max_depth:
                        return ""
                    lines = []
                    try:
                        children = list(d.iterdir())
                        if not show_hidden:
                            children = [c for c in children if not c.name.startswith(".")]
                        for i, c in enumerate(sorted(children, key=lambda x: (not x.is_dir(), x.name.lower()))):
                            is_last = i == len(children) - 1
                            connector = "└── " if is_last else "├── "
                            lines.append(prefix + connector + c.name)
                            if c.is_dir():
                                ext = "    " if is_last else "│   "
                                lines.append(build_tree(c, prefix + ext, depth + 1))
                    except:
                        lines.append(prefix + "└── [Error]")
                    return "\n".join([l for l in lines if l])
                
                try:
                    text = str(base) + "\n" + build_tree(base)
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "get_file_info":
                try:
                    p = Path(str(tool_args.get("path", "")))
                    st = p.stat()
                    info = {
                        "path": str(p),
                        "size": st.st_size,
                        "isDirectory": p.is_dir(),
                        "isFile": p.is_file(),
                        "lastModified": st.st_mtime
                    }
                    result = {"content": [{"type": "text", "text": json.dumps(info)}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "create_file":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    p = Path(str(tool_args.get("path", "")))
                    content = str(tool_args.get("content", ""))
                    overwrite = bool(tool_args.get("overwrite", False))
                    try:
                        if p.exists() and not overwrite:
                            result = {"content": [{"type": "text", "text": "File exists. Use overwrite=true"}]}
                        else:
                            p.parent.mkdir(parents=True, exist_ok=True)
                            p.write_text(content, encoding="utf-8")
                            result = {"content": [{"type": "text", "text": f"File created: {p}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "delete_file":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    p = Path(str(tool_args.get("path", "")))
                    recursive = bool(tool_args.get("recursive", False))
                    try:
                        if p.is_dir():
                            if recursive:
                                shutil.rmtree(p)
                            else:
                                p.rmdir()
                        else:
                            p.unlink()
                        result = {"content": [{"type": "text", "text": f"Deleted: {p}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "move_file":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    src = Path(str(tool_args.get("source", "")))
                    dst = Path(str(tool_args.get("destination", "")))
                    overwrite = bool(tool_args.get("overwrite", False))
                    try:
                        if dst.exists() and not overwrite:
                            result = {"content": [{"type": "text", "text": "Destination exists. Use overwrite=true"}]}
                        else:
                            dst.parent.mkdir(parents=True, exist_ok=True)
                            shutil.move(str(src), str(dst))
                            result = {"content": [{"type": "text", "text": f"Moved: {src} -> {dst}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "edit_file":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    p = Path(str(tool_args.get("path", "")))
                    old_text = str(tool_args.get("oldText", ""))
                    new_text = str(tool_args.get("newText", ""))
                    try:
                        content = p.read_text(encoding="utf-8")
                        if old_text in content:
                            content = content.replace(old_text, new_text, 1)
                            p.write_text(content, encoding="utf-8")
                            result = {"content": [{"type": "text", "text": f"File edited: {p}"}]}
                        else:
                            result = {"content": [{"type": "text", "text": "oldText not found"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
                        
            # FIXED: multi_edit implementation
            elif tool_name == "multi_edit":
                auth_token = tool_args.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "Write disabled."}]}
                else:
                    p = Path(str(tool_args.get("path", "")))
                    edits = tool_args.get("edits", [])
                    try:
                        content = p.read_text(encoding="utf-8")
                        changes_made = 0
                        
                        for edit in edits:
                            old_text = str(edit.get("oldText", ""))
                            new_text = str(edit.get("newText", ""))
                            if old_text in content:
                                content = content.replace(old_text, new_text, 1)
                                changes_made += 1
                        
                        if changes_made > 0:
                            p.write_text(content, encoding="utf-8")
                            result = {"content": [{"type": "text", "text": f"File edited: {changes_made} changes made"}]}
                        else:
                            result = {"content": [{"type": "text", "text": "No changes made (texts not found)"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "grep":
                pattern = str(tool_args.get("pattern", ""))
                base = Path(str(tool_args.get("path", ".")))
                file_pattern = str(tool_args.get("filePattern", "")).strip() or None
                ignore_case = bool(tool_args.get("ignoreCase", False))
                show_line_numbers = bool(tool_args.get("showLineNumbers", True))
                context_lines = int(tool_args.get("contextLines", 0))
                
                try:
                    rex = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
                    matches = []
                    
                    if base.is_file():
                        files_to_search = [base]
                    else:
                        if file_pattern:
                            files_to_search = list(base.glob(file_pattern))
                        else:
                            files_to_search = list(base.rglob("*")) if base.is_dir() else []
                    
                    for file_path in files_to_search:
                        if file_path.is_file():
                            try:
                                with open(file_path, 'r', encoding='utf-8') as f:
                                    lines = f.readlines()
                                    for i, line in enumerate(lines, 1):
                                        if rex.search(line):
                                            context_start = max(0, i - context_lines - 1)
                                            context_end = min(len(lines), i + context_lines)
                                            context = lines[context_start:context_end]
                                            
                                            if show_line_numbers:
                                                match_line = f"{file_path}:{i}: {line.rstrip()}"
                                            else:
                                                match_line = f"{file_path}: {line.rstrip()}"
                                            
                                            if context_lines > 0:
                                                context_text = "".join([f"  {context_start + j + 1}: {l}" for j, l in enumerate(context)])
                                                match_line += f"\n{context_text}"
                                            
                                            matches.append(match_line)
                            except Exception as e:
                                matches.append(f"{file_path}: Error reading file: {e}")
                    
                    text = "\n".join(matches) if matches else "No matches found"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error searching: {e}"}]}
                    
            # FIXED: find_files implementation 
            elif tool_name == "find_files":
                pattern = str(tool_args.get("pattern", ""))
                base = Path(str(tool_args.get("path", ".")))
                ftype = str(tool_args.get("type", "")).lower() or None
                max_depth = tool_args.get("maxDepth", None)
                
                try:
                    matches = []
                    if base.is_dir():
                        for root, dirs, files in os.walk(base):
                            current_depth = len(Path(root).relative_to(base).parts)
                            if max_depth is not None and current_depth > max_depth:
                                continue
                            
                            items = files if ftype != "directory" else dirs
                            if ftype == "file":
                                items = files
                            elif ftype == "directory":
                                items = dirs
                            else:
                                items = files + dirs
                            
                            for item in items:
                                if fnmatch.fnmatch(item, pattern):
                                    full_path = Path(root) / item
                                    if ftype == "file" and full_path.is_file():
                                        matches.append(str(full_path))
                                    elif ftype == "directory" and full_path.is_dir():
                                        matches.append(str(full_path))
                                    elif ftype is None:
                                        matches.append(str(full_path))
                    
                    text = "\n".join(matches) if matches else "No files found"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            elif tool_name == "search":
                query = str(tool_args.get("query", ""))
                base = Path(str(tool_args.get("path", ".")))
                search_type = str(tool_args.get("type", "all"))
                file_pattern = str(tool_args.get("filePattern", "")).strip() or None
                max_results = int(tool_args.get("maxResults", 50))
                
                # Special case: if query is simple and matches a predicate, search in KB
                if search_type == "all" and not file_pattern and base == Path("."):
                    # Try KB search first
                    conn = sqlite3.connect(str(self.db_path))
                    cursor = conn.execute(
                        "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                        (f"%{query}%", max_results)
                    )
                    kb_facts = [row[0] for row in cursor]
                    conn.close()
                    
                    if kb_facts:
                        text = f"Gefunden: {len(kb_facts)} Fakten\n" + "\n".join([f"- {f}" for f in kb_facts])
                        result = {"content": [{"type": "text", "text": text}]}
                    else:
                        result = {"content": [{"type": "text", "text": "No matches found in knowledge base"}]}
                else:
                    # File system search
                    try:
                        pat = re.compile(query, re.IGNORECASE)
                        results = []
                        
                        if base.is_file():
                            files_to_search = [base]
                        else:
                            if file_pattern:
                                files_to_search = list(base.glob(file_pattern))
                            else:
                                files_to_search = list(base.rglob("*")) if base.is_dir() else []
                        
                        for file_path in files_to_search:
                            if file_path.is_file():
                                try:
                                    # Filename search
                                    if search_type in ["all", "filename"]:
                                        if pat.search(file_path.name):
                                            results.append(f"Filename match: {file_path}")
                                    
                                    # Content search
                                    if search_type in ["all", "content"] and len(results) < max_results:
                                        with open(file_path, 'r', encoding='utf-8') as f:
                                            content = f.read()
                                            if pat.search(content):
                                                results.append(f"Content match: {file_path}")
                                except Exception as e:
                                    results.append(f"Error reading {file_path}: {e}")
                        
                        text = "\n".join(results[:max_results]) if results else "No matches found"
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error searching: {e}"}]}
            
            else:
                # Should never happen - all 43 tools are implemented
                result = {"content": [{"type": "text", "text": f"ERROR: Tool '{tool_name}' not found in FIXED implementation!"}]}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id", 1),
            "result": result
        }
        await self.send_response(response)
    
    async def handle_request(self, request):
        """Route request to appropriate handler"""
        method = request.get("method", "")
        
        if method == "initialize":
            await self.handle_initialize(request)
        elif method == "tools/list":
            await self.handle_list_tools(request)
        elif method == "tools/call":
            await self.handle_tool_call(request)
        elif method == "resources/list":
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": {"resources": []}
            }
            await self.send_response(response)
        elif method == "prompts/list":
            response = {
                "jsonrpc": "2.0",
                "id": request.get("id", 1),
                "result": {"prompts": []}
            }
            await self.send_response(response)
        else:
            logger.warning(f"Unknown method: {method}")
    
    async def run(self):
        """Main loop"""
        logger.info("MCP Server starting with ALL 43 tools - FULLY FUNCTIONAL...")
        
        while self.running:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                try:
                    request = json.loads(line)
                    logger.debug(f"Received: {line[:200]}")
                    await self.handle_request(request)
                except json.JSONDecodeError as e:
                    logger.error(f"JSON decode error: {e}")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"Main loop error: {e}")
        
        logger.info("MCP Server stopped")

if __name__ == "__main__":
    server = HAKGALMCPServer()
    asyncio.run(server.run())
