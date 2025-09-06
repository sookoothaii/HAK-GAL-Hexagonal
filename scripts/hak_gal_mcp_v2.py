#!/usr/bin/env python3
"""
HAK_GAL MCP Server v2 - Stabilized for Claude Desktop
With proper stdin handling and protocol compliance
"""

import sys
import json
import logging
from pathlib import Path
import os
import shutil
import re
import time
from datetime import datetime

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

            elif tool_name == "agent_delegate":
                task = (args.get("task") or "").strip()
                agents = args.get("agents") or ["generalist"]
                strategy = (args.get("strategy") or "round_robin").strip()
                assignments = []
                for i, agent in enumerate(agents):
                    assignments.append({
                        "agent": agent,
                        "subtask": f"{task} [Teil {i+1}/{len(agents)}]"
                    })
                result = {
                    "task": task,
                    "strategy": strategy,
                    "assignments": assignments,
                    "combined_result": "Stub: Orchestration ausgeführt (simulation)"
                }

            elif tool_name == "llm_consensus":
                prompt = (args.get("prompt") or "").strip()
                providers = args.get("providers") or ["deepseek", "mistral"]
                votes = [{"provider": p, "response": None, "confidence": None} for p in providers]
                result = {
                    "prompt": prompt,
                    "providers": providers,
                    "votes": votes,
                    "consensus": None,
                    "note": "Stub: Externe LLM-Provider nicht angebunden"
                }

            elif tool_name == "jupyter_info":
                jupyter = shutil.which("jupyter")
                lab = shutil.which("jupyter-lab") or shutil.which("jupyter-lab.exe")
                kernels = []
                try:
                    # Best-effort: lese Kernels-Verzeichnis
                    home = Path.home()
                    kdir = home / ".local" / "share" / "jupyter" / "kernels"
                    if kdir.exists():
                        for d in kdir.iterdir():
                            if d.is_dir():
                                kernels.append(d.name)
                except Exception:
                    pass
                result = {
                    "installed": bool(jupyter),
                    "jupyter_path": jupyter,
                    "lab_path": lab,
                    "kernels": kernels[:20]
                }

            elif tool_name == "neovim_info":
                nvim = shutil.which("nvim") or shutil.which("nvim.exe")
                result = {"installed": bool(nvim), "nvim_path": nvim}

            elif tool_name == "package_runner_info":
                npx = shutil.which("npx") or shutil.which("npx.cmd")
                uvx = shutil.which("uvx") or shutil.which("uvx.exe")
                result = {"npx": bool(npx), "uvx": bool(uvx), "paths": {"npx": npx, "uvx": uvx}}

            elif tool_name == "combined_search":
                query = (args.get("query") or "").strip()
                limit = int(args.get("limit", 20))
                base = Path(__file__).resolve().parent  # repo root folder
                matches = []
                exts = {".py", ".ts", ".tsx", ".js", ".json"}
                try:
                    for root, _dirs, files in os.walk(base):
                        for fname in files:
                            if Path(fname).suffix.lower() in exts:
                                p = Path(root) / fname
                                try:
                                    text = p.read_text(encoding='utf-8', errors='ignore')
                                    if query and query.lower() in text.lower():
                                        # Collect a short preview (first line with match)
                                        line_no = None
                                        for idx, line in enumerate(text.splitlines()[:1000]):
                                            if query.lower() in line.lower():
                                                line_no = idx + 1
                                                break
                                        matches.append({"file": str(p.relative_to(base)), "line": line_no})
                                        if len(matches) >= limit:
                                            raise StopIteration
                                except Exception:
                                    continue
                except StopIteration:
                    pass
                result = {"query": query, "count": len(matches), "matches": matches}

            elif tool_name == "symbols_search":
                symbol = (args.get("symbol") or "").strip()
                limit = int(args.get("limit", 50))
                base = Path(__file__).resolve().parent
                patt_py_func = re.compile(r"^\s*def\s+" + re.escape(symbol) + r"\s*\(")
                patt_py_class = re.compile(r"^\s*class\s+" + re.escape(symbol) + r"\b")
                found = []
                for root, _dirs, files in os.walk(base):
                    for fname in files:
                        if Path(fname).suffix.lower() == ".py":
                            p = Path(root) / fname
                            try:
                                for idx, line in enumerate(p.read_text(encoding='utf-8', errors='ignore').splitlines()):
                                    if patt_py_func.search(line) or patt_py_class.search(line):
                                        found.append({"file": str(p.relative_to(base)), "line": idx + 1})
                                        if len(found) >= limit:
                                            raise StopIteration
                            except Exception:
                                continue
                result = {"symbol": symbol, "count": len(found), "locations": found}

            elif tool_name == "vector_search":
                result = {"available": False, "message": "Vector-Index nicht aktiviert"}

            elif tool_name == "watch":
                result = {"supported": False, "message": "File-Watching nicht verfügbar im STDIO-Server"}

            elif tool_name == "processes_list":
                top = int(args.get("limit", 10))
                procs = []
                try:
                    import psutil  # type: ignore
                    for p in psutil.process_iter(attrs=["pid", "name", "cpu_percent", "memory_percent"]):
                        info = p.info
                        procs.append({
                            "pid": info.get("pid"),
                            "name": info.get("name"),
                            "cpu": info.get("cpu_percent"),
                            "mem": info.get("memory_percent")
                        })
                    procs.sort(key=lambda x: (x.get("cpu") or 0), reverse=True)
                    result = {"count": len(procs), "top": procs[:top]}
                except Exception:
                    result = {"error": "psutil nicht verfügbar", "count": None, "top": []}

            elif tool_name == "mcp_manage_servers":
                result = {
                    "supported": False,
                    "current_server": "HAK_GAL MCP v2",
                    "message": "Dynamisches Hinzufügen/Entfernen nicht unterstützt"
                }

            elif tool_name == "palette_config":
                result = {
                    "palettes": [
                        {"name": "dev", "tools": ["combined_search", "symbols_search", "kb_stats"]},
                        {"name": "analysis", "tools": ["quality_metrics", "predicates_top", "project_hub_digest"]}
                    ]
                }

            elif tool_name == "todo_list":
                todo_path = Path("PROJECT_HUB") / "todo.json"
                items = []
                try:
                    if todo_path.exists():
                        items = json.loads(todo_path.read_text(encoding='utf-8', errors='ignore'))
                except Exception:
                    items = []
                result = {"items": items}

            elif tool_name == "todo_add":
                text = (args.get("text") or "").strip()
                if not text:
                    result = {"error": "Missing text"}
                else:
                    todo_path = Path("PROJECT_HUB") / "todo.json"
                    try:
                        items = []
                        if todo_path.exists():
                            items = json.loads(todo_path.read_text(encoding='utf-8', errors='ignore'))
                        item = {"id": int(time.time()*1000), "text": text, "done": False, "ts": datetime.utcnow().isoformat() + "Z"}
                        items.append(item)
                        todo_path.parent.mkdir(parents=True, exist_ok=True)
                        todo_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
                        result = {"added": True, "item": item, "count": len(items)}
                    except Exception as e:
                        result = {"error": str(e)}

            elif tool_name == "todo_done":
                tid = args.get("id")
                todo_path = Path("PROJECT_HUB") / "todo.json"
                try:
                    items = []
                    if todo_path.exists():
                        items = json.loads(todo_path.read_text(encoding='utf-8', errors='ignore'))
                    updated = 0
                    for it in items:
                        if it.get("id") == tid:
                            it["done"] = True
                            updated += 1
                            break
                    todo_path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding='utf-8')
                    result = {"updated": updated}
                except Exception as e:
                    result = {"error": str(e)}

            elif tool_name == "stats_basic":
                p = self.kb_path
                try:
                    stat = p.stat()
                    fact_count = sum(1 for line in open(p, 'r', encoding='utf-8') if line.strip())
                    from collections import Counter
                    cnt = Counter()
                    with open(p, 'r', encoding='utf-8') as f:
                        for i, line in enumerate(f):
                            if i >= 5000:
                                break
                            if not line.strip():
                                continue
                            try:
                                obj = json.loads(line)
                                stmt = obj.get('statement', '')
                                m = re.match(r"^([A-Za-z_][A-Za-z0-9_]*)\(", stmt)
                                if m:
                                    cnt[m.group(1)] += 1
                            except Exception:
                                continue
                    top5 = cnt.most_common(5)
                    result = {"facts": fact_count, "size_bytes": stat.st_size, "top_predicates": top5}
                except Exception as e:
                    result = {"error": str(e)}

            elif tool_name == "batch_ops":
                ops = args.get("operations") or []
                out = []
                for op in ops:
                    try:
                        oname = op.get("name")
                        oargs = op.get("arguments") or {}
                        # Allow a safe subset
                        if oname in {"search_knowledge", "get_system_status", "kb_stats"}:
                            # recursively dispatch by calling handler directly
                            if oname == "search_knowledge":
                                q = oargs.get("query", "")
                                lim = oargs.get("limit", 5)
                                facts = []
                                with open(self.kb_path, 'r', encoding='utf-8') as f:
                                    for line in f:
                                        if line.strip():
                                            try:
                                                obj = json.loads(line)
                                                stmt = obj.get('statement', '')
                                                if q.lower() in stmt.lower():
                                                    facts.append(stmt)
                                                    if len(facts) >= lim:
                                                        break
                                            except Exception:
                                                pass
                                out.append({"name": oname, "result": {"facts": facts, "count": len(facts)}})
                            elif oname == "get_system_status":
                                fact_count = sum(1 for line in open(self.kb_path, 'r', encoding='utf-8') if line.strip())
                                out.append({"name": oname, "result": {"status": "operational", "kb_facts": fact_count}})
                            elif oname == "kb_stats":
                                st = Path(self.kb_path).stat()
                                out.append({"name": oname, "result": {"size_bytes": st.st_size}})
                        else:
                            out.append({"name": oname, "error": "Operation not allowed in batch"})
                    except Exception as e:
                        out.append({"name": op.get("name"), "error": str(e)})
                result = {"results": out}
                
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
                                    },
                                    {
                                        "name": "agent_delegate",
                                        "description": "Delegiere Task an spezialisierte Agenten (Stub)",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "task": {"type": "string"},
                                                "agents": {"type": "array", "items": {"type": "string"}},
                                                "strategy": {"type": "string", "default": "round_robin"}
                                            },
                                            "required": ["task"]
                                        }
                                    },
                                    {
                                        "name": "llm_consensus",
                                        "description": "Multi‑LLM Konsensus (Stub)",
                                        "inputSchema": {
                                            "type": "object",
                                            "properties": {
                                                "prompt": {"type": "string"},
                                                "providers": {"type": "array", "items": {"type": "string"}}
                                            },
                                            "required": ["prompt"]
                                        }
                                    },
                                    {"name": "jupyter_info", "description": "Jupyter/Lab Status", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "neovim_info", "description": "Neovim Status", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "package_runner_info", "description": "npx/uvx Verfügbarkeit", "inputSchema": {"type": "object", "properties": {}}},
                                    {
                                        "name": "combined_search",
                                        "description": "Einfache kombinierte Code‑Suche (Stub)",
                                        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "limit": {"type": "integer", "default": 20}}, "required": ["query"]}
                                    },
                                    {
                                        "name": "symbols_search",
                                        "description": "Symbol‑Suche in Python (Stub)",
                                        "inputSchema": {"type": "object", "properties": {"symbol": {"type": "string"}, "limit": {"type": "integer", "default": 50}}, "required": ["symbol"]}
                                    },
                                    {
                                        "name": "vector_search",
                                        "description": "Vector‑Suche (nicht aktiviert)",
                                        "inputSchema": {"type": "object", "properties": {"query": {"type": "string"}, "top_k": {"type": "integer", "default": 10}}}
                                    },
                                    {"name": "watch", "description": "File‑Watcher (nicht verfügbar im STDIO)", "inputSchema": {"type": "object", "properties": {"paths": {"type": "array", "items": {"type": "string"}}}}},
                                    {"name": "processes_list", "description": "Systemprozesse auflisten", "inputSchema": {"type": "object", "properties": {"limit": {"type": "integer", "default": 10}}}},
                                    {"name": "mcp_manage_servers", "description": "MCP‑Server Orchestrierung (Stub)", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "palette_config", "description": "Tool‑Paletten (Stub)", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "todo_list", "description": "TODO‑Liste anzeigen", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "todo_add", "description": "TODO hinzufügen", "inputSchema": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
                                    {"name": "todo_done", "description": "TODO als erledigt markieren", "inputSchema": {"type": "object", "properties": {"id": {"type": "number"}}, "required": ["id"]}},
                                    {"name": "stats_basic", "description": "Einfache KB‑Statistik", "inputSchema": {"type": "object", "properties": {}}},
                                    {"name": "batch_ops", "description": "Sichere Batch‑Ausführung ausgewählter Tools", "inputSchema": {"type": "object", "properties": {"operations": {"type": "array", "items": {"type": "object"}}}}}
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
