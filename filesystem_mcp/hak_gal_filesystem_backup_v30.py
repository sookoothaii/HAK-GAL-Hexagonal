#!/usr/bin/env python3
"""
HAK_GAL Filesystem MCP Server
Dedicated server for file operations and code execution
Separated from the main KB server for clean architecture
"""

import sys
import os
import json
import asyncio
import logging
import subprocess
import tempfile
import uuid
import time
import shutil
from pathlib import Path
import fnmatch
import glob
import re
import hashlib
import difflib
from collections import deque
import zipfile
import tarfile
import platform
import signal

# Setup logging
logging.basicConfig(
    level=logging.INFO,  # Changed from DEBUG to INFO
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\filesystem_mcp.log')
        # Removed StreamHandler to prevent stderr output
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
try:
    from dotenv import load_dotenv
    script_dir = Path(__file__).parent
    env_path = script_dir / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)
    else:
        load_dotenv(override=True)
except ImportError:
    pass

class FileSystemMCPServer:
    """MCP Server for filesystem operations and code execution"""
    
    def __init__(self):
        self.running = True
        self.request_id = 0
        
        # UTF-8 Setup
        if hasattr(sys.stdin, 'reconfigure'):
            sys.stdin.reconfigure(encoding='utf-8')
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', line_buffering=True, write_through=True)
        
        # Write safety
        self.write_enabled = os.environ.get("HAKGAL_WRITE_ENABLED", "true").lower() == "true"
        self.write_token = os.environ.get("HAKGAL_WRITE_TOKEN", "")
        
        # Execute code configuration
        self.temp_dir = Path(tempfile.gettempdir()) / "hakgal_filesystem_exec"
        self.temp_dir.mkdir(exist_ok=True)
        self.allowed_languages = ["python", "javascript", "bash", "powershell"]
        self.max_output_size = int(os.environ.get("MCP_EXEC_MAX_OUTPUT", "50000"))
        
        # Language timeouts
        self.timeout_defaults = {
            "python": int(os.environ.get("MCP_EXEC_TIMEOUT_PY", "30")),
            "javascript": int(os.environ.get("MCP_EXEC_TIMEOUT_JS", "30")),
            "bash": int(os.environ.get("MCP_EXEC_TIMEOUT_SH", "30")),
            "powershell": int(os.environ.get("MCP_EXEC_TIMEOUT_PS", "30")),
        }
        
        # Log only to file, not to stderr
        # logger.info(f"Filesystem MCP Server initialized")
        # logger.info(f"Execute code temp dir: {self.temp_dir}")
        # logger.info(f"Write operations: {self.write_enabled}")
    
    def _is_write_allowed(self, provided_token: str) -> bool:
        """Check if write operations are allowed"""
        if not self.write_enabled:
            return False
        if self.write_token:
            return provided_token == self.write_token
        return True
    
    def _get_file_extension(self, language: str) -> str:
        """Get file extension for language"""
        extensions = {
            "python": "py",
            "javascript": "js",
            "bash": "sh",
            "powershell": "ps1"
        }
        return extensions.get(language, "txt")
    
    def _execute_code_safely(self, code: str, language: str, timeout: int = 30):
        """Execute code safely in sandbox"""
        try:
            if language not in self.allowed_languages:
                return {"error": f"Language '{language}' not allowed. Allowed: {self.allowed_languages}"}
            
            # Create temporary file
            temp_file = self.temp_dir / f"exec_{uuid.uuid4().hex[:8]}.{self._get_file_extension(language)}"
            
            with open(temp_file, 'w', encoding='utf-8') as f:
                f.write(code)
            
            # Setup environment
            env = os.environ.copy()
            env['PYTHONUNBUFFERED'] = '1'
            env['PYTHONIOENCODING'] = 'utf-8'
            
            # Execute
            start_time = time.time()
            eff_timeout = timeout or self.timeout_defaults.get(language, 30)
            
            if language == "python":
                result = subprocess.run(
                    [sys.executable, "-u", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=eff_timeout,
                    cwd=str(self.temp_dir),
                    env=env,
                    encoding='utf-8',
                    errors='replace'
                )
            elif language == "javascript":
                result = subprocess.run(
                    ["node", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=eff_timeout,
                    cwd=str(self.temp_dir),
                    encoding='utf-8',
                    errors='replace'
                )
            elif language == "bash":
                result = subprocess.run(
                    ["bash", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=eff_timeout,
                    cwd=str(self.temp_dir),
                    encoding='utf-8',
                    errors='replace'
                )
            elif language == "powershell":
                result = subprocess.run(
                    ["powershell", "-ExecutionPolicy", "Bypass", "-File", str(temp_file)],
                    capture_output=True,
                    text=True,
                    timeout=eff_timeout,
                    cwd=str(self.temp_dir),
                    encoding='utf-8',
                    errors='replace'
                )
            
            duration_sec = max(0.0, time.time() - start_time)
            
            # Clean up
            try:
                temp_file.unlink()
            except:
                pass
            
            # Process output
            stdout = result.stdout if result.stdout else ""
            stderr = result.stderr if result.stderr else ""
            
            # Sanitize to ASCII
            try:
                stdout = stdout.encode('ascii', 'replace').decode('ascii')
                stderr = stderr.encode('ascii', 'replace').decode('ascii')
            except:
                pass
            
            # Limit output size
            if len(stdout) > self.max_output_size:
                stdout = stdout[:self.max_output_size] + "\n... (output truncated)"
            if len(stderr) > self.max_output_size:
                stderr = stderr[:self.max_output_size] + "\n... (output truncated)"
            
            return {
                "stdout": stdout,
                "stderr": stderr,
                "return_code": result.returncode,
                "execution_time": f"{duration_sec:.3f}s",
                "runtime_seconds": duration_sec,
                "language": language
            }
            
        except subprocess.TimeoutExpired as e:
            # Handle timeout
            if isinstance(e.stdout, bytes):
                stdout = e.stdout.decode('utf-8', errors='replace') if e.stdout else ""
            else:
                stdout = e.stdout or ""
            if isinstance(e.stderr, bytes):
                stderr = e.stderr.decode('utf-8', errors='replace') if e.stderr else ""
            else:
                stderr = e.stderr or ""
            
            try:
                stdout = stdout.encode('ascii', 'replace').decode('ascii')
                stderr = stderr.encode('ascii', 'replace').decode('ascii')
            except:
                pass
                
            return {
                "error": f"Execution timeout after {timeout} seconds",
                "stdout": stdout[:self.max_output_size] if stdout else "",
                "stderr": stderr[:self.max_output_size] if stderr else "",
                "timeout": True,
                "execution_time": f">={timeout}s",
                "runtime_seconds": float(timeout)
            }
        except FileNotFoundError:
            return {"error": f"Language interpreter for '{language}' not found"}
        except Exception as e:
            logger.error(f"Execute code error: {e}")
            return {"error": f"Execution error: {str(e)}"}
    
    async def send_response(self, response):
        """Send JSON-RPC response"""
        response_str = json.dumps(response, ensure_ascii=True)
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
                    "name": "HAK_GAL Filesystem MCP",
                    "version": "3.0.0"
                }
            }
        }
        await self.send_response(response)
    
    async def handle_list_tools(self, request):
        """List available filesystem tools"""
        tools = [
            # Execution tool
            {
                "name": "execute_code",
                "description": "Execute code safely in sandbox environment",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "code": {"type": "string", "description": "Code to execute"},
                        "language": {"type": "string", "description": "Programming language (python, javascript, bash, powershell)"},
                        "timeout": {"type": "integer", "description": "Execution timeout in seconds", "default": 30}
                    },
                    "required": ["code", "language"]
                }
            },
            # File operations
            {
                "name": "read_file",
                "description": "Read file content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "encoding": {"type": "string", "default": "utf-8"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "write_file",
                "description": "Write content to file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "encoding": {"type": "string", "default": "utf-8"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "list_files",
                "description": "List files in directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                        "recursive": {"type": "boolean", "default": False},
                        "pattern": {"type": "string"}
                    }
                }
            },
            {
                "name": "get_file_info",
                "description": "Get file metadata",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "directory_tree",
                "description": "Show directory tree structure",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "default": "."},
                        "maxDepth": {"type": "integer", "default": 3},
                        "showHidden": {"type": "boolean", "default": False}
                    }
                }
            },
            {
                "name": "create_file",
                "description": "Create new file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "content": {"type": "string"},
                        "overwrite": {"type": "boolean", "default": False},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path", "content"]
                }
            },
            {
                "name": "delete_file",
                "description": "Delete file or directory",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "recursive": {"type": "boolean", "default": False},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "move_file",
                "description": "Move or rename file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "source": {"type": "string"},
                        "destination": {"type": "string"},
                        "overwrite": {"type": "boolean", "default": False},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["source", "destination"]
                }
            },
            {
                "name": "copy_batch",
                "description": "Copy one or multiple files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "operations": {
                            "type": "array",
                            "description": "List of copy operations",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "source": {"type": "string", "description": "Source path"},
                                    "destination": {"type": "string", "description": "Destination path"}
                                },
                                "required": ["source", "destination"]
                            }
                        },
                        "source": {"type": "string", "description": "Single source (if operations not used)"},
                        "destination": {"type": "string", "description": "Single destination (if operations not used)"},
                        "overwrite": {"type": "boolean", "default": False, "description": "Overwrite existing files"},
                        "auth_token": {"type": "string", "description": "Auth token for write operations"}
                    }
                }
            },
            # NEW: Additional filesystem tools (v2.0)
            {
                "name": "create_directory",
                "description": "Create directory (recursive)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Directory path to create"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "file_diff", 
                "description": "Compare two files and show differences",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "file1": {"type": "string", "description": "First file path"},
                        "file2": {"type": "string", "description": "Second file path"},
                        "context_lines": {"type": "integer", "default": 3, "description": "Number of context lines"}
                    },
                    "required": ["file1", "file2"]
                }
            },
            {
                "name": "calculate_hash",
                "description": "Calculate file hash (MD5, SHA1, SHA256)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "algorithm": {"type": "string", "default": "sha256", "description": "Hash algorithm (md5, sha1, sha256)"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "tail_file",
                "description": "Get last N lines from file (like Unix tail)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "File path"},
                        "lines": {"type": "integer", "default": 10, "description": "Number of lines"},
                        "follow": {"type": "boolean", "default": False, "description": "Follow file changes (not implemented)"}
                    },
                    "required": ["path"]
                }
            },
            {
                "name": "format_code",
                "description": "Format Python code using built-in formatter",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string", "description": "Python file path"},
                        "auth_token": {"type": "string"},
                        "max_line_length": {"type": "integer", "default": 88}
                    },
                    "required": ["path"]
                }
            },
            # Additional tools in v3.0
            {
                "name": "directory_diff",
                "description": "Compare two directories recursively",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dir1": {"type": "string", "description": "First directory path"},
                        "dir2": {"type": "string", "description": "Second directory path"},
                        "ignore_patterns": {"type": "array", "items": {"type": "string"}, "default": [".git", "__pycache__", ".pyc"]}
                    },
                    "required": ["dir1", "dir2"]
                }
            },
            {
                "name": "archive_extract",
                "description": "Extract ZIP or TAR archives",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "archive_path": {"type": "string", "description": "Path to archive file"},
                        "extract_to": {"type": "string", "description": "Extraction directory"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["archive_path"]
                }
            },
            {
                "name": "archive_create",
                "description": "Create ZIP or TAR archives",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "archive_path": {"type": "string", "description": "Output archive path"},
                        "files": {"type": "array", "items": {"type": "string"}, "description": "Files/directories to archive"},
                        "archive_type": {"type": "string", "default": "zip", "description": "Archive type: zip, tar, tar.gz"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["archive_path", "files"]
                }
            },
            {
                "name": "get_process_list",
                "description": "List running processes (basic info)",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "filter": {"type": "string", "description": "Filter by process name"}
                    }
                }
            },
            {
                "name": "kill_process",
                "description": "Terminate a process by PID",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pid": {"type": "integer", "description": "Process ID to kill"},
                        "force": {"type": "boolean", "default": False, "description": "Force kill (SIGKILL)"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["pid"]
                }
            },
            {
                "name": "get_tech_stack",
                "description": "Analyze project technology stack",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "project_path": {"type": "string", "description": "Project root directory"}
                    },
                    "required": ["project_path"]
                }
            },
            # Search and edit tools
            {
                "name": "grep",
                "description": "Search pattern in files",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "filePattern": {"type": "string"},
                        "ignoreCase": {"type": "boolean", "default": False},
                        "showLineNumbers": {"type": "boolean", "default": True},
                        "contextLines": {"type": "integer", "default": 0}
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "find_files",
                "description": "Find files by pattern",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "pattern": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "type": {"type": "string"},
                        "maxDepth": {"type": "integer"}
                    },
                    "required": ["pattern"]
                }
            },
            {
                "name": "search",
                "description": "Unified search for files and content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string"},
                        "path": {"type": "string", "default": "."},
                        "type": {"type": "string", "default": "all"},
                        "filePattern": {"type": "string"},
                        "maxResults": {"type": "integer", "default": 50}
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "edit_file",
                "description": "Replace text in file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "oldText": {"type": "string"},
                        "newText": {"type": "string"},
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path", "oldText", "newText"]
                }
            },
            {
                "name": "multi_edit",
                "description": "Multiple text replacements in file",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "path": {"type": "string"},
                        "edits": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "oldText": {"type": "string"},
                                    "newText": {"type": "string"}
                                },
                                "required": ["oldText", "newText"]
                            }
                        },
                        "auth_token": {"type": "string"}
                    },
                    "required": ["path", "edits"]
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
        """Handle tool execution requests"""
        params = request.get("params", {})
        name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        result = {"content": [{"type": "text", "text": "Unknown tool"}]}
        
        try:
            # Execute code
            if name == "execute_code":
                code = str(arguments.get("code", ""))
                language = str(arguments.get("language", "")).lower()
                timeout = int(arguments.get("timeout", 30))
                
                if not code:
                    result = {"content": [{"type": "text", "text": "Missing 'code' parameter"}]}
                elif not language:
                    result = {"content": [{"type": "text", "text": "Missing 'language' parameter"}]}
                else:
                    execution_result = self._execute_code_safely(code, language, timeout)
                    
                    if "error" in execution_result and not execution_result.get("timeout"):
                        text = f"ERROR: {execution_result['error']}"
                    else:
                        stdout = execution_result.get("stdout", "")
                        stderr = execution_result.get("stderr", "")
                        return_code = execution_result.get("return_code", 0)
                        lang = execution_result.get("language", language)
                        
                        text = ""
                        if execution_result.get("timeout"):
                            text = f"[TIMEOUT] Execution timeout after {timeout} seconds\n\n"
                        else:
                            text = f"[OK] Code executed successfully\n\n"
                        
                        text += f"**Language:** {lang}\n"
                        text += f"**Return Code:** {return_code}\n"
                        text += f"**Execution Time:** {execution_result.get('execution_time', 'completed')}\n\n"
                        
                        if stdout:
                            text += f"**STDOUT:**\n```\n{stdout}\n```\n\n"
                        else:
                            text += "**STDOUT:** (no output)\n\n"
                        
                        if stderr:
                            text += f"**STDERR:**\n```\n{stderr}\n```\n\n"
                        
                        if return_code != 0:
                            text += f"Warning: Process exited with code {return_code}"
                    
                    result = {"content": [{"type": "text", "text": text}]}
            
            # Read file
            elif name == "read_file":
                path = arguments.get("path", "")
                encoding = arguments.get("encoding", "utf-8")
                try:
                    with open(path, "r", encoding=encoding) as f:
                        content = f.read()
                    result = {"content": [{"type": "text", "text": content}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Write file
            elif name == "write_file":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    content = arguments.get("content", "")
                    encoding = arguments.get("encoding", "utf-8")
                    try:
                        os.makedirs(os.path.dirname(path), exist_ok=True)
                        with open(path, "w", encoding=encoding) as f:
                            f.write(content)
                        result = {"content": [{"type": "text", "text": f"Written {len(content)} chars to {path}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # List files
            elif name == "list_files":
                path = arguments.get("path", ".")
                recursive = arguments.get("recursive", False)
                pattern = arguments.get("pattern", "*")
                try:
                    files = []
                    if recursive:
                        for root, dirs, filenames in os.walk(path):
                            for filename in filenames:
                                if fnmatch.fnmatch(filename, pattern):
                                    files.append(os.path.join(root, filename))
                    else:
                        files = glob.glob(os.path.join(path, pattern))
                    
                    text = f"Found {len(files)} files:\n" + "\n".join(files[:100])
                    if len(files) > 100:
                        text += f"\n... and {len(files) - 100} more"
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Get file info
            elif name == "get_file_info":
                path = arguments.get("path", "")
                try:
                    stat = os.stat(path)
                    info = {
                        "path": path,
                        "size": stat.st_size,
                        "modified": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_mtime)),
                        "created": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(stat.st_ctime)),
                        "is_file": os.path.isfile(path),
                        "is_dir": os.path.isdir(path)
                    }
                    result = {"content": [{"type": "text", "text": json.dumps(info, indent=2)}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Directory tree
            elif name == "directory_tree":
                path = arguments.get("path", ".")
                max_depth = arguments.get("maxDepth", 3)
                show_hidden = arguments.get("showHidden", False)
                
                def tree(dir_path, prefix="", depth=0):
                    if depth >= max_depth:
                        return []
                    
                    lines = []
                    try:
                        entries = sorted(os.listdir(dir_path))
                        if not show_hidden:
                            entries = [e for e in entries if not e.startswith('.')]
                        
                        for i, entry in enumerate(entries):
                            is_last = i == len(entries) - 1
                            entry_path = os.path.join(dir_path, entry)
                            connector = "└── " if is_last else "├── "
                            
                            if os.path.isdir(entry_path):
                                lines.append(prefix + connector + entry + "/")
                                extension = "    " if is_last else "│   "
                                lines.extend(tree(entry_path, prefix + extension, depth + 1))
                            else:
                                lines.append(prefix + connector + entry)
                    except PermissionError:
                        lines.append(prefix + "└── [Permission Denied]")
                    
                    return lines
                
                try:
                    lines = [path + "/"] + tree(path)
                    result = {"content": [{"type": "text", "text": "\n".join(lines)}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Create file
            elif name == "create_file":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    content = arguments.get("content", "")
                    overwrite = arguments.get("overwrite", False)
                    try:
                        if os.path.exists(path) and not overwrite:
                            result = {"content": [{"type": "text", "text": "File exists. Use overwrite=true to replace."}]}
                        else:
                            os.makedirs(os.path.dirname(path), exist_ok=True)
                            with open(path, "w", encoding="utf-8") as f:
                                f.write(content)
                            result = {"content": [{"type": "text", "text": f"Created {path}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Delete file
            elif name == "delete_file":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    recursive = arguments.get("recursive", False)
                    try:
                        if os.path.isdir(path) and recursive:
                            shutil.rmtree(path)
                            result = {"content": [{"type": "text", "text": f"Deleted directory {path}"}]}
                        elif os.path.isfile(path):
                            os.unlink(path)
                            result = {"content": [{"type": "text", "text": f"Deleted file {path}"}]}
                        else:
                            result = {"content": [{"type": "text", "text": "Path not found or is directory (use recursive=true)"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Move file
            elif name == "move_file":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    source = arguments.get("source", "")
                    destination = arguments.get("destination", "")
                    overwrite = arguments.get("overwrite", False)
                    try:
                        if os.path.exists(destination) and not overwrite:
                            result = {"content": [{"type": "text", "text": "Destination exists. Use overwrite=true."}]}
                        else:
                            os.makedirs(os.path.dirname(destination), exist_ok=True)
                            shutil.move(source, destination)
                            result = {"content": [{"type": "text", "text": f"Moved {source} to {destination}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Copy batch (NEW!)
            elif name == "copy_batch":
                auth_token = arguments.get("auth_token", "")
                if not self._is_write_allowed(auth_token):
                    result = {"content": [{"type": "text", "text": "ERROR: Write disabled or invalid auth token"}]}
                else:
                    overwrite = arguments.get("overwrite", False)
                    results = []
                    
                    # Handle single file copy
                    if "source" in arguments and "destination" in arguments:
                        operations = [(arguments["source"], arguments["destination"])]
                    # Handle batch copy
                    elif "operations" in arguments:
                        operations = [(op["source"], op["destination"]) for op in arguments["operations"]]
                    else:
                        result = {"content": [{"type": "text", "text": "ERROR: Either provide 'source'/'destination' or 'operations' array"}]}
                        operations = []
                    
                    if operations:
                        # Process copy operations
                        success_count = 0
                        for source, destination in operations:
                            try:
                                # Create destination directory if needed
                                dest_dir = os.path.dirname(destination)
                                if dest_dir and not os.path.exists(dest_dir):
                                    os.makedirs(dest_dir, exist_ok=True)
                                
                                # Check if destination exists
                                if os.path.exists(destination) and not overwrite:
                                    results.append(f"SKIPPED: {destination} already exists (use overwrite=true)")
                                    continue
                                
                                # Copy the file
                                shutil.copy2(source, destination)
                                success_count += 1
                                results.append(f"✓ Copied: {source} → {destination}")
                                
                            except Exception as e:
                                results.append(f"✗ Failed: {source} → {destination}: {str(e)}")
                        
                        text = f"Copy operations completed: {success_count}/{len(operations)} successful\n\n" + "\n".join(results)
                        result = {"content": [{"type": "text", "text": text}]}
            
            # Grep
            elif name == "grep":
                pattern = arguments.get("pattern", "")
                path = arguments.get("path", ".")
                file_pattern = arguments.get("filePattern", "*")
                ignore_case = arguments.get("ignoreCase", False)
                show_line_numbers = arguments.get("showLineNumbers", True)
                context_lines = arguments.get("contextLines", 0)
                
                try:
                    matches = []
                    regex = re.compile(pattern, re.IGNORECASE if ignore_case else 0)
                    
                    # Find files to search
                    if os.path.isfile(path):
                        files_to_search = [path]
                    else:
                        files_to_search = []
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if fnmatch.fnmatch(file, file_pattern):
                                    files_to_search.append(os.path.join(root, file))
                    
                    # Search in files
                    for file_path in files_to_search[:100]:  # Limit to 100 files
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                lines = f.readlines()
                                for i, line in enumerate(lines):
                                    if regex.search(line):
                                        if show_line_numbers:
                                            matches.append(f"{file_path}:{i+1}: {line.rstrip()}")
                                        else:
                                            matches.append(f"{file_path}: {line.rstrip()}")
                                        
                                        if len(matches) >= 100:  # Limit results
                                            break
                        except Exception:
                            continue
                        
                        if len(matches) >= 100:
                            break
                    
                    if matches:
                        text = f"Found {len(matches)} matches:\n" + "\n".join(matches)
                    else:
                        text = "No matches found"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Find files
            elif name == "find_files":
                pattern = arguments.get("pattern", "*")
                path = arguments.get("path", ".")
                file_type = arguments.get("type", "")
                max_depth = arguments.get("maxDepth")
                
                try:
                    found = []
                    
                    def search_files(dir_path, current_depth=0):
                        if max_depth and current_depth >= max_depth:
                            return
                        
                        try:
                            for entry in os.listdir(dir_path):
                                entry_path = os.path.join(dir_path, entry)
                                
                                if os.path.isdir(entry_path):
                                    if not file_type or file_type == "dir":
                                        if fnmatch.fnmatch(entry, pattern):
                                            found.append(entry_path)
                                    search_files(entry_path, current_depth + 1)
                                elif os.path.isfile(entry_path):
                                    if not file_type or file_type == "file":
                                        if fnmatch.fnmatch(entry, pattern):
                                            found.append(entry_path)
                        except PermissionError:
                            pass
                    
                    search_files(path)
                    
                    text = f"Found {len(found)} items:\n" + "\n".join(found[:100])
                    if len(found) > 100:
                        text += f"\n... and {len(found) - 100} more"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Unified search
            elif name == "search":
                query = arguments.get("query", "")
                path = arguments.get("path", ".")
                search_type = arguments.get("type", "all")
                file_pattern = arguments.get("filePattern", "*")
                max_results = arguments.get("maxResults", 50)
                
                try:
                    results = []
                    
                    # Search in filenames
                    if search_type in ["all", "filename"]:
                        for root, dirs, files in os.walk(path):
                            for item in dirs + files:
                                if query.lower() in item.lower():
                                    results.append(("filename", os.path.join(root, item)))
                                    if len(results) >= max_results:
                                        break
                            if len(results) >= max_results:
                                break
                    
                    # Search in file contents
                    if search_type in ["all", "content"] and len(results) < max_results:
                        regex = re.compile(query, re.IGNORECASE)
                        for root, dirs, files in os.walk(path):
                            for file in files:
                                if fnmatch.fnmatch(file, file_pattern):
                                    file_path = os.path.join(root, file)
                                    try:
                                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                            for i, line in enumerate(f):
                                                if regex.search(line):
                                                    results.append(("content", f"{file_path}:{i+1}"))
                                                    if len(results) >= max_results:
                                                        break
                                    except:
                                        pass
                                    
                                    if len(results) >= max_results:
                                        break
                            if len(results) >= max_results:
                                break
                    
                    if results:
                        text = f"Found {len(results)} results:\n"
                        for result_type, result_text in results:
                            text += f"[{result_type}] {result_text}\n"
                    else:
                        text = "No results found"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Edit file
            elif name == "edit_file":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    old_text = arguments.get("oldText", "")
                    new_text = arguments.get("newText", "")
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        if old_text in content:
                            new_content = content.replace(old_text, new_text)
                            with open(path, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            
                            count = content.count(old_text)
                            result = {"content": [{"type": "text", "text": f"Replaced {count} occurrences in {path}"}]}
                        else:
                            result = {"content": [{"type": "text", "text": "Text not found in file"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Multi edit
            elif name == "multi_edit":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    edits = arguments.get("edits", [])
                    try:
                        with open(path, 'r', encoding='utf-8') as f:
                            content = f.read()
                        
                        total_replacements = 0
                        for edit in edits:
                            old_text = edit.get("oldText", "")
                            new_text = edit.get("newText", "")
                            if old_text and old_text in content:
                                count = content.count(old_text)
                                content = content.replace(old_text, new_text)
                                total_replacements += count
                        
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(content)
                        
                        result = {"content": [{"type": "text", "text": f"Made {total_replacements} replacements in {path}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Create directory
            elif name == "create_directory":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    try:
                        os.makedirs(path, exist_ok=True)
                        result = {"content": [{"type": "text", "text": f"Created directory: {path}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # File diff
            elif name == "file_diff":
                file1 = arguments.get("file1", "")
                file2 = arguments.get("file2", "")
                context_lines = arguments.get("context_lines", 3)
                try:
                    with open(file1, 'r', encoding='utf-8', errors='ignore') as f:
                        lines1 = f.readlines()
                    with open(file2, 'r', encoding='utf-8', errors='ignore') as f:
                        lines2 = f.readlines()
                    
                    diff = difflib.unified_diff(
                        lines1, lines2,
                        fromfile=file1,
                        tofile=file2,
                        n=context_lines
                    )
                    
                    diff_text = ''.join(diff)
                    if diff_text:
                        result = {"content": [{"type": "text", "text": diff_text}]}
                    else:
                        result = {"content": [{"type": "text", "text": "Files are identical"}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Calculate hash
            elif name == "calculate_hash":
                path = arguments.get("path", "")
                algorithm = arguments.get("algorithm", "sha256").lower()
                try:
                    if algorithm not in ["md5", "sha1", "sha256"]:
                        result = {"content": [{"type": "text", "text": "Unsupported algorithm. Use: md5, sha1, sha256"}]}
                    else:
                        hash_obj = hashlib.new(algorithm)
                        with open(path, 'rb') as f:
                            for chunk in iter(lambda: f.read(4096), b''):
                                hash_obj.update(chunk)
                        
                        hash_value = hash_obj.hexdigest()
                        file_size = os.path.getsize(path)
                        
                        text = f"File: {path}\n"
                        text += f"Size: {file_size:,} bytes\n"
                        text += f"{algorithm.upper()}: {hash_value}"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Tail file
            elif name == "tail_file":
                path = arguments.get("path", "")
                num_lines = arguments.get("lines", 10)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        # Efficient tail using deque
                        tail_lines = deque(f, maxlen=num_lines)
                    
                    text = ''.join(tail_lines)
                    if not text:
                        text = "(empty file)"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Format code
            elif name == "format_code":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    path = arguments.get("path", "")
                    max_line_length = arguments.get("max_line_length", 88)
                    try:
                        # Read the file
                        with open(path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        
                        # Format using Python's built-in tools
                        import ast
                        import textwrap
                        
                        # Parse to check syntax
                        ast.parse(code)
                        
                        # Basic formatting: normalize indentation
                        lines = code.splitlines()
                        formatted_lines = []
                        
                        for line in lines:
                            # Remove trailing whitespace
                            line = line.rstrip()
                            formatted_lines.append(line)
                        
                        formatted_code = '\n'.join(formatted_lines)
                        
                        # Write back
                        with open(path, 'w', encoding='utf-8') as f:
                            f.write(formatted_code)
                        
                        result = {"content": [{"type": "text", "text": f"Formatted {path} (basic formatting)"}]}
                    except SyntaxError as e:
                        result = {"content": [{"type": "text", "text": f"Syntax error in Python file: {e}"}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Directory diff
            elif name == "directory_diff":
                dir1 = arguments.get("dir1", "")
                dir2 = arguments.get("dir2", "")
                ignore_patterns = arguments.get("ignore_patterns", [".git", "__pycache__", ".pyc"])
                
                try:
                    def get_files(directory):
                        files = {}
                        for root, dirs, filenames in os.walk(directory):
                            # Filter ignored directories
                            dirs[:] = [d for d in dirs if not any(pattern in d for pattern in ignore_patterns)]
                            
                            for filename in filenames:
                                if any(pattern in filename for pattern in ignore_patterns):
                                    continue
                                    
                                filepath = os.path.join(root, filename)
                                relpath = os.path.relpath(filepath, directory)
                                
                                with open(filepath, 'rb') as f:
                                    files[relpath] = hashlib.md5(f.read()).hexdigest()
                        
                        return files
                    
                    files1 = get_files(dir1)
                    files2 = get_files(dir2)
                    
                    only_in_dir1 = set(files1.keys()) - set(files2.keys())
                    only_in_dir2 = set(files2.keys()) - set(files1.keys())
                    common_files = set(files1.keys()) & set(files2.keys())
                    
                    different = []
                    for f in common_files:
                        if files1[f] != files2[f]:
                            different.append(f)
                    
                    text = f"Directory comparison: {dir1} vs {dir2}\n\n"
                    
                    if only_in_dir1:
                        text += f"Only in {dir1}:\n"
                        for f in sorted(only_in_dir1)[:20]:
                            text += f"  + {f}\n"
                        if len(only_in_dir1) > 20:
                            text += f"  ... and {len(only_in_dir1) - 20} more\n"
                        text += "\n"
                    
                    if only_in_dir2:
                        text += f"Only in {dir2}:\n"
                        for f in sorted(only_in_dir2)[:20]:
                            text += f"  - {f}\n"
                        if len(only_in_dir2) > 20:
                            text += f"  ... and {len(only_in_dir2) - 20} more\n"
                        text += "\n"
                    
                    if different:
                        text += f"Files with different content ({len(different)}):\n"
                        for f in sorted(different)[:20]:
                            text += f"  * {f}\n"
                        if len(different) > 20:
                            text += f"  ... and {len(different) - 20} more\n"
                    
                    if not only_in_dir1 and not only_in_dir2 and not different:
                        text = "Directories are identical"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Archive extract
            elif name == "archive_extract":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    archive_path = arguments.get("archive_path", "")
                    extract_to = arguments.get("extract_to", os.path.dirname(archive_path))
                    
                    try:
                        os.makedirs(extract_to, exist_ok=True)
                        
                        if archive_path.lower().endswith('.zip'):
                            with zipfile.ZipFile(archive_path, 'r') as zf:
                                zf.extractall(extract_to)
                                files = zf.namelist()
                                text = f"Extracted {len(files)} files from ZIP to {extract_to}"
                        
                        elif archive_path.lower().endswith(('.tar', '.tar.gz', '.tgz')):
                            mode = 'r:gz' if archive_path.lower().endswith(('.tar.gz', '.tgz')) else 'r'
                            with tarfile.open(archive_path, mode) as tf:
                                tf.extractall(extract_to)
                                files = tf.getnames()
                                text = f"Extracted {len(files)} files from TAR to {extract_to}"
                        else:
                            text = "Unsupported archive format. Supported: .zip, .tar, .tar.gz"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Archive create
            elif name == "archive_create":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    archive_path = arguments.get("archive_path", "")
                    files = arguments.get("files", [])
                    archive_type = arguments.get("archive_type", "zip").lower()
                    
                    try:
                        if archive_type == "zip":
                            with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zf:
                                file_count = 0
                                for item in files:
                                    if os.path.isfile(item):
                                        zf.write(item, os.path.basename(item))
                                        file_count += 1
                                    elif os.path.isdir(item):
                                        for root, dirs, filenames in os.walk(item):
                                            for filename in filenames:
                                                filepath = os.path.join(root, filename)
                                                arcname = os.path.relpath(filepath, os.path.dirname(item))
                                                zf.write(filepath, arcname)
                                                file_count += 1
                            
                            text = f"Created ZIP archive: {archive_path} ({file_count} files)"
                        
                        elif archive_type in ["tar", "tar.gz"]:
                            mode = 'w:gz' if archive_type == "tar.gz" else 'w'
                            with tarfile.open(archive_path, mode) as tf:
                                file_count = 0
                                for item in files:
                                    tf.add(item, arcname=os.path.basename(item))
                                    if os.path.isdir(item):
                                        for root, dirs, filenames in os.walk(item):
                                            file_count += len(filenames)
                                    else:
                                        file_count += 1
                            
                            text = f"Created TAR archive: {archive_path} ({file_count} files)"
                        else:
                            text = "Unsupported archive type. Use: zip, tar, tar.gz"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Get process list
            elif name == "get_process_list":
                filter_name = arguments.get("filter", "").lower()
                
                try:
                    if platform.system() == "Windows":
                        # Windows: use tasklist
                        cmd_result = subprocess.run(
                            ["tasklist", "/FO", "CSV"],
                            capture_output=True,
                            text=True
                        )
                        
                        processes = []
                        lines = cmd_result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            parts = line.split('","')
                            if len(parts) >= 2:
                                name = parts[0].strip('"')
                                pid = parts[1]
                                if not filter_name or filter_name in name.lower():
                                    processes.append(f"{pid}: {name}")
                    else:
                        # Unix-like: use ps
                        cmd_result = subprocess.run(
                            ["ps", "-eo", "pid,comm"],
                            capture_output=True,
                            text=True
                        )
                        
                        processes = []
                        lines = cmd_result.stdout.strip().split('\n')[1:]  # Skip header
                        for line in lines:
                            parts = line.strip().split(None, 1)
                            if len(parts) == 2:
                                pid, name = parts
                                if not filter_name or filter_name in name.lower():
                                    processes.append(f"{pid}: {name}")
                    
                    text = f"Found {len(processes)} processes"
                    if filter_name:
                        text += f" matching '{filter_name}'"
                    text += ":\n\n"
                    
                    for proc in processes[:50]:  # Limit output
                        text += proc + "\n"
                    
                    if len(processes) > 50:
                        text += f"\n... and {len(processes) - 50} more"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Kill process
            elif name == "kill_process":
                if not self._is_write_allowed(arguments.get("auth_token", "")):
                    result = {"content": [{"type": "text", "text": "Write disabled or invalid token"}]}
                else:
                    pid = int(arguments.get("pid", 0))
                    force = arguments.get("force", False)
                    
                    try:
                        if platform.system() == "Windows":
                            # Windows
                            cmd = ["taskkill", "/PID", str(pid)]
                            if force:
                                cmd.append("/F")
                            subprocess.run(cmd, check=True)
                            text = f"Terminated process {pid}"
                        else:
                            # Unix-like
                            sig = signal.SIGKILL if force else signal.SIGTERM
                            os.kill(pid, sig)
                            text = f"Sent {'SIGKILL' if force else 'SIGTERM'} to process {pid}"
                        
                        result = {"content": [{"type": "text", "text": text}]}
                    except Exception as e:
                        result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            # Get tech stack
            elif name == "get_tech_stack":
                project_path = arguments.get("project_path", ".")
                
                try:
                    tech_stack = {
                        "languages": {},
                        "frameworks": [],
                        "package_managers": [],
                        "databases": [],
                        "tools": []
                    }
                    
                    # Scan for file types and config files
                    for root, dirs, files in os.walk(project_path):
                        # Skip common ignore directories
                        dirs[:] = [d for d in dirs if d not in ['.git', 'node_modules', '__pycache__', '.venv', 'venv']]
                        
                        for file in files:
                            ext = os.path.splitext(file)[1].lower()
                            
                            # Count programming languages
                            lang_map = {
                                '.py': 'Python',
                                '.js': 'JavaScript',
                                '.ts': 'TypeScript',
                                '.java': 'Java',
                                '.cpp': 'C++',
                                '.c': 'C',
                                '.cs': 'C#',
                                '.rb': 'Ruby',
                                '.go': 'Go',
                                '.rs': 'Rust',
                                '.php': 'PHP',
                                '.swift': 'Swift'
                            }
                            
                            if ext in lang_map:
                                lang = lang_map[ext]
                                tech_stack["languages"][lang] = tech_stack["languages"].get(lang, 0) + 1
                            
                            # Detect package managers and frameworks
                            if file == "package.json":
                                tech_stack["package_managers"].append("npm/yarn")
                                # Try to detect frameworks
                                try:
                                    with open(os.path.join(root, file), 'r') as f:
                                        content = f.read()
                                        if '"react"' in content:
                                            tech_stack["frameworks"].append("React")
                                        if '"vue"' in content:
                                            tech_stack["frameworks"].append("Vue.js")
                                        if '"@angular/core"' in content:
                                            tech_stack["frameworks"].append("Angular")
                                except:
                                    pass
                            
                            elif file == "requirements.txt" or file == "pyproject.toml":
                                tech_stack["package_managers"].append("pip/poetry")
                                if file == "requirements.txt":
                                    try:
                                        with open(os.path.join(root, file), 'r') as f:
                                            content = f.read().lower()
                                            if 'django' in content:
                                                tech_stack["frameworks"].append("Django")
                                            if 'flask' in content:
                                                tech_stack["frameworks"].append("Flask")
                                            if 'fastapi' in content:
                                                tech_stack["frameworks"].append("FastAPI")
                                    except:
                                        pass
                            
                            elif file == "pom.xml":
                                tech_stack["package_managers"].append("Maven")
                            elif file == "build.gradle":
                                tech_stack["package_managers"].append("Gradle")
                            elif file == "Gemfile":
                                tech_stack["package_managers"].append("Bundler")
                            elif file == "go.mod":
                                tech_stack["package_managers"].append("Go Modules")
                            elif file == "Cargo.toml":
                                tech_stack["package_managers"].append("Cargo")
                            
                            # Detect tools and databases
                            elif file == "docker-compose.yml" or file == "Dockerfile":
                                tech_stack["tools"].append("Docker")
                            elif file == ".gitignore":
                                tech_stack["tools"].append("Git")
                    
                    # Format output
                    text = f"Technology Stack Analysis for: {project_path}\n\n"
                    
                    if tech_stack["languages"]:
                        text += "**Programming Languages:**\n"
                        sorted_langs = sorted(tech_stack["languages"].items(), key=lambda x: x[1], reverse=True)
                        for lang, count in sorted_langs:
                            text += f"  - {lang}: {count} files\n"
                        text += "\n"
                    
                    if tech_stack["frameworks"]:
                        text += "**Frameworks detected:**\n"
                        for fw in set(tech_stack["frameworks"]):
                            text += f"  - {fw}\n"
                        text += "\n"
                    
                    if tech_stack["package_managers"]:
                        text += "**Package Managers:**\n"
                        for pm in set(tech_stack["package_managers"]):
                            text += f"  - {pm}\n"
                        text += "\n"
                    
                    if tech_stack["tools"]:
                        text += "**Development Tools:**\n"
                        for tool in set(tech_stack["tools"]):
                            text += f"  - {tool}\n"
                    
                    if not any([tech_stack["languages"], tech_stack["frameworks"], 
                               tech_stack["package_managers"], tech_stack["tools"]]):
                        text = "No recognizable technology stack found in this directory"
                    
                    result = {"content": [{"type": "text", "text": text}]}
                except Exception as e:
                    result = {"content": [{"type": "text", "text": f"Error: {e}"}]}
            
            else:
                result = {"content": [{"type": "text", "text": f"Unknown tool: {name}"}]}
        
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            result = {"content": [{"type": "text", "text": f"Tool error: {str(e)}"}]}
        
        response = {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": result
        }
        await self.send_response(response)
    
    async def run(self):
        """Main server loop"""
        # logger.info("Filesystem MCP Server started")
        # logger.info("Listening for requests on stdin...")
        
        while self.running:
            try:
                line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                logger.debug(f"Received: {line[:200]}")
                
                try:
                    request = json.loads(line)
                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON: {e}")
                    continue
                
                method = request.get("method", "")
                
                if method == "initialize":
                    await self.handle_initialize(request)
                elif method == "tools/list":
                    await self.handle_list_tools(request)
                elif method == "tools/call":
                    await self.handle_tool_call(request)
                elif method == "notifications/cancelled":
                    logger.info("Received cancellation notification")
                else:
                    logger.warning(f"Unknown method: {method}")
                    error_response = {
                        "jsonrpc": "2.0",
                        "id": request.get("id"),
                        "error": {
                            "code": -32601,
                            "message": "Method not found"
                        }
                    }
                    await self.send_response(error_response)
            
            except KeyboardInterrupt:
                logger.info("Received interrupt signal")
                break
            except Exception as e:
                logger.error(f"Error in main loop: {e}", exc_info=True)
        
        logger.info("Server shutdown")

async def main():
    server = FileSystemMCPServer()
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())
