#!/usr/bin/env python3
"""
HAK_GAL MCP Server v2 - Stabilized for Claude Desktop
With proper stdin handling and protocol compliance
"""

import sys
import json
import logging
from pathlib import Path

# Configure logging to file only (not stderr/stdout)
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\mcp_server_v2.log', mode='a')
    ]
)
logger = logging.getLogger(__name__)

class HAKGALMCPServerV2:
    def __init__(self):
        self.kb_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
        logger.info(f"Server initialized. KB exists: {self.kb_path.exists()}")
        
    def send_message(self, msg):
        """Send JSON-RPC message via stdout"""
        msg_str = json.dumps(msg, separators=(',', ':'))  # Compact JSON
        sys.stdout.write(msg_str + '\n')
        sys.stdout.flush()
        logger.debug(f"Sent: {msg_str[:200]}")
        
    def handle_initialize(self, req_id):
        """Respond to initialize request"""
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2025-06-18",
                "capabilities": {
                    # Advertise that tools can be listed and may change
                    "tools": {"listChanged": True},
                    # Explicitly advertise empty capabilities for optional areas
                    "resources": {},
                    "prompts": {}
                },
                "serverInfo": {
                    "name": "HAK_GAL MCP",
                    "version": "2.0"
                }
            }
        }
        self.send_message(response)
        
    def handle_tool_call(self, req_id, tool_name, args):
        """Execute tool and return result"""
        result = {}
        
        try:
            if tool_name == "search_knowledge":
                query = args.get("query", "").lower()
                limit = args.get("limit", 10)
                facts = []
                
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            try:
                                fact_obj = json.loads(line)
                                statement = fact_obj.get('statement', '')
                                if query in statement.lower():
                                    facts.append(statement)
                                    if len(facts) >= limit:
                                        break
                            except:
                                pass
                                
                result = {"facts": facts, "count": len(facts)}
                
            elif tool_name == "get_system_status":
                fact_count = sum(1 for line in open(self.kb_path, 'r') if line.strip())
                result = {
                    "status": "operational",
                    "kb_facts": fact_count,
                    "policy_version": "v2.2",
                    "port": 5001
                }
            elif tool_name == "list_recent_facts":
                count = int(args.get("count", 5))
                facts = []
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                for line in reversed(lines):
                    if line.strip():
                        try:
                            fact_obj = json.loads(line)
                            stmt = fact_obj.get('statement', '')
                            if stmt:
                                facts.append(stmt)
                                if len(facts) >= count:
                                    break
                        except Exception:
                            pass
                result = {"facts": facts, "count": len(facts)}
            elif tool_name == "kb_stats":
                p = self.kb_path
                stat = p.stat()
                fact_count = sum(1 for line in open(p, 'r', encoding='utf-8') if line.strip())
                result = {
                    "facts": fact_count,
                    "size_bytes": stat.st_size,
                    "modified": __import__("datetime").datetime.fromtimestamp(stat.st_mtime).isoformat()
                }
            elif tool_name == "get_predicates_stats":
                from collections import Counter
                counts = Counter()
                with open(self.kb_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if not line.strip():
                            continue
                        try:
                            obj = json.loads(line)
                            stmt = obj.get('statement', '')
                            idx = stmt.find('(')
                            if idx > 0:
                                pred = stmt[:idx]
                                counts[pred] += 1
                        except Exception:
                            pass
                result = {"predicates": counts.most_common()}
            elif tool_name == "search_by_predicate":
                predicate = args.get("predicate", "")
                limit = int(args.get("limit", 100))
                out = []
                if predicate:
                    prefix = predicate + "("
                    with open(self.kb_path, 'r', encoding='utf-8') as f:
                        for line in f:
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                stmt = obj.get('statement', '')
                                if stmt.startswith(prefix):
                                    out.append(stmt)
                                    if len(out) >= limit:
                                        break
                            except Exception:
                                pass
                result = {"results": out, "count": len(out)}
            elif tool_name == "project_list_snapshots":
                from pathlib import Path
                hub_path = Path(args.get("hub_path", ""))
                limit = int(args.get("limit", 20))
                if not hub_path or not hub_path.exists():
                    raise FileNotFoundError(f"hub_path not found: {hub_path}")
                entries = []
                for child in hub_path.iterdir():
                    if child.is_dir() and child.name.startswith("snapshot_"):
                        try:
                            entries.append((child.name, child.stat().st_mtime))
                        except Exception:
                            pass
                entries.sort(key=lambda x: x[1], reverse=True)
                result = {"snapshots": [name for name, _ in entries[:limit]]}
            elif tool_name == "project_hub_digest":
                from pathlib import Path
                hub_path = Path(args.get("hub_path", ""))
                limit_files = int(args.get("limit_files", 3))
                max_chars = int(args.get("max_chars", 20000))
                if not hub_path or not hub_path.exists():
                    raise FileNotFoundError(f"hub_path not found: {hub_path}")
                # Collect newest snapshot dirs
                dirs = []
                for child in hub_path.iterdir():
                    if child.is_dir() and child.name.startswith("snapshot_"):
                        try:
                            dirs.append((child, child.stat().st_mtime))
                        except Exception:
                            pass
                dirs.sort(key=lambda x: x[1], reverse=True)
                content_parts = []
                for (d, _) in dirs[:limit_files]:
                    files_order = [
                        ("SNAPSHOT.md", "markdown"),
                        ("SNAPSHOT_TECH.md", "markdown"),
                        ("SNAPSHOT_KB.md", "markdown"),
                        ("manifest.json", "json"),
                        ("snapshot_kb.json", "json"),
                        ("snapshot.json", "json")
                    ]
                    chunk = f"# {d.name}\n"
                    for filename, ftype in files_order:
                        try:
                            p = d / filename
                            if not p.exists():
                                continue
                            if ftype == "markdown":
                                chunk += f"\n\n## {filename}\n\n"
                                chunk += p.read_text(encoding='utf-8', errors='ignore')
                            else:
                                # JSON: parse and re-dump compactly to avoid huge blobs
                                chunk += f"\n\n## {filename}\n\n"
                                try:
                                    obj = json.loads(p.read_text(encoding='utf-8', errors='ignore'))
                                    chunk += json.dumps(obj, ensure_ascii=False, indent=2)[:max(0, max_chars // 3)]
                                except Exception:
                                    chunk += p.read_text(encoding='utf-8', errors='ignore')[:max(0, max_chars // 3)]
                        except Exception:
                            continue
                    content_parts.append(chunk)
                digest = "\n\n---\n\n".join(content_parts)
                if len(digest) > max_chars:
                    digest = digest[:max_chars]
                result = {"digest": digest, "length": len(digest)}
                
        except Exception as e:
            logger.error(f"Tool error: {e}")
            result = {"error": str(e)}
            
        response = {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": result
        }
        self.send_message(response)
        
    def run(self):
        """Main server loop"""
        logger.info("HAK_GAL MCP Server v2 starting...")
        
        # Don't send anything on startup - wait for initialize
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:  # EOF
                    logger.info("EOF received, shutting down")
                    break
                    
                line = line.strip()
                if not line:
                    continue
                    
                logger.debug(f"Received: {line[:200]}")
                
                try:
                    request = json.loads(line)
                    method = request.get("method")
                    req_id = request.get("id")
                    
                    if method == "initialize":
                        self.handle_initialize(req_id)
                        
                    elif method == "tools/call":
                        params = request.get("params", {})
                        tool_name = params.get("name")
                        args = params.get("arguments", {})
                        self.handle_tool_call(req_id, tool_name, args)
                        
                    elif method == "tools/list":
                        # Return available tools with full schemas
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {
                                "tools": [
                                    {
                                        "name": "search_knowledge",
                                        "description": "Search HAK_GAL knowledge base",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "query": {"type": "string"},
                                                "limit": {"type": "integer", "default": 10}
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
                                        "description": "List recent facts from KB",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "count": {"type": "integer", "default": 5}
                                            }
                                        }
                                    },
                                    {
                                        "name": "kb_stats",
                                        "description": "Show KB statistics",
                                        "inputSchema": {"type": "object", "properties": {}}
                                    },
                                    {
                                        "name": "get_predicates_stats",
                                        "description": "Frequency of all predicates",
                                        "inputSchema": {"type": "object", "properties": {}}
                                    },
                                    {
                                        "name": "search_by_predicate",
                                        "description": "Search facts by predicate",
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
                                        "name": "project_list_snapshots",
                                        "description": "List available project snapshots",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "hub_path": {"type": "string"},
                                                "limit": {"type": "integer", "default": 20}
                                            },
                                            "required": ["hub_path"]
                                        }
                                    },
                                    {
                                        "name": "project_hub_digest",
                                        "description": "Build compact digest from latest snapshots",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "hub_path": {"type": "string"},
                                                "limit_files": {"type": "integer", "default": 3},
                                                "max_chars": {"type": "integer", "default": 20000}
                                            },
                                            "required": ["hub_path"]
                                        }
                                    }
                                ]
                            }
                        }
                        self.send_message(response)

                    elif method == "resources/list":
                        # No resources exposed
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {"resources": []}
                        }
                        self.send_message(response)

                    elif method == "prompts/list":
                        # No prompts exposed
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {"prompts": []}
                        }
                        self.send_message(response)
                        
                    elif method == "shutdown":
                        response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "result": {}
                        }
                        self.send_message(response)
                        break
                        
                    else:
                        # Unknown method
                        error_response = {
                            "jsonrpc": "2.0",
                            "id": req_id,
                            "error": {
                                "code": -32601,
                                "message": f"Method not found: {method}"
                            }
                        }
                        self.send_message(error_response)
                        
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parse error: {e}")
                    # Send parse error
                    error = {
                        "jsonrpc": "2.0",
                        "id": None,
                        "error": {
                            "code": -32700,
                            "message": "Parse error"
                        }
                    }
                    self.send_message(error)
                    
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt")
                break
            except Exception as e:
                logger.error(f"Fatal error: {e}")
                break
                
        logger.info("Server shutdown complete")

if __name__ == "__main__":
    server = HAKGALMCPServerV2()
    server.run()
