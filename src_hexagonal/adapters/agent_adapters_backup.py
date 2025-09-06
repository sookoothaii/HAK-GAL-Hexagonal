"""
Adapters for Communicating with External AI Agents
"""
import subprocess
import requests
import logging
import shlex
import shutil
import json
import time
import os
import uuid
from pathlib import Path
import urllib.parse
import webbrowser
import socket

logger = logging.getLogger(__name__)

class BaseAgentAdapter:
    def dispatch(self, task_description, context):
        raise NotImplementedError

class CursorAdapter(BaseAgentAdapter):
    """Advanced adapter for communicating with Cursor IDE"""
    
    def __init__(self, socketio=None):
        self.socketio = socketio  # Store socketio instance
        self.websocket_clients = set()  # Track connected Cursor clients
        self.mcp_port = 3000  # Default MCP port for Cursor
        self.file_exchange_dir = Path("cursor_exchange")
        self.file_exchange_dir.mkdir(exist_ok=True)
        
    def dispatch(self, task_description, context):
        logger.info(f"Dispatching task to Cursor: {task_description[:80]}")
        
        # Method 1: Try WebSocket communication (if Cursor clients connected)
        ws_result = self._dispatch_via_websocket(task_description, context)
        if ws_result['status'] != 'error':
            return ws_result
            
        # Method 2: Try MCP Protocol
        mcp_result = self._dispatch_via_mcp(task_description, context)
        if mcp_result['status'] != 'error':
            return mcp_result
            
        # Method 3: File-based communication (most reliable)
        file_result = self._dispatch_via_file(task_description, context)
        if file_result['status'] != 'error':
            return file_result
            
        # Method 4: URL Scheme (opens Cursor with task)
        url_result = self._dispatch_via_url_scheme(task_description, context)
        if url_result['status'] != 'error':
            return url_result
            
        return {
            "status": "pending", 
            "message": "Task queued for Cursor. Multiple communication methods attempted.",
            "methods_tried": ["websocket", "mcp", "file", "url_scheme"]
        }
    
    def _dispatch_via_websocket(self, task_description, context):
        """Send task via WebSocket to connected Cursor clients"""
        try:
            if not self.socketio:
                logger.warning("SocketIO instance not provided to CursorAdapter. Cannot dispatch via WebSocket.")
                return {"status": "error", "message": "SocketIO not configured for CursorAdapter"}

            if not self.websocket_clients:
                return {"status": "error", "message": "No Cursor WebSocket clients connected"}
            
            task_data = {
                "type": "cursor_task",
                "task": task_description,
                "context": context,
                "timestamp": time.time(),
                "id": str(uuid.uuid4())
            }
            
            # Send to all connected Cursor clients
            for client_sid in self.websocket_clients:
                try:
                    self.socketio.emit('cursor_task', task_data, room=client_sid) # Emit to specific client
                    logger.info(f"Sent cursor_task to client {client_sid}")
                except Exception as e:
                    logger.warning(f"Failed to send to Cursor client {client_sid}: {e}")
            
            return {
                "status": "dispatched",
                "message": f"Task sent to {len(self.websocket_clients)} Cursor client(s) via WebSocket",
                "task_id": task_data["id"]
            }
            
        except Exception as e:
            logger.error(f"WebSocket dispatch error: {e}")
            return {"status": "error", "message": f"WebSocket error: {str(e)}"}
    
    def _dispatch_via_mcp(self, task_description, context):
        """Attempt MCP communication with Cursor"""
        try:
            # Try to connect to Cursor's MCP server
            mcp_url = f"http://localhost:{self.mcp_port}/mcp"
            
            # Prepare MCP request
            mcp_request = {
                "jsonrpc": "2.0",
                "method": "tools/call",
                "params": {
                    "name": "execute_task",
                    "arguments": {
                        "task": task_description,
                        "context": context
                    }
                },
                "id": str(uuid.uuid4())
            }
            
            response = requests.post(mcp_url, json=mcp_request, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return {
                    "status": "completed",
                    "result": data.get("result", "Task executed via MCP"),
                    "method": "mcp"
                }
            else:
                return {"status": "error", "message": f"MCP server not available: {response.status_code}"}
                
        except Exception as e:
            logger.debug(f"MCP communication failed: {e}")
            return {"status": "error", "message": "MCP not available"}
    
    def _dispatch_via_file(self, task_description, context):
        """File-based communication with Cursor"""
        try:
            task_id = str(uuid.uuid4())
            task_file = self.file_exchange_dir / f"task_{task_id}.json"
            
            task_data = {
                "id": task_id,
                "task": task_description,
                "context": context,
                "timestamp": time.time(),
                "source": "HAK_GAL_Multi_Agent",
                "status": "pending"
            }
            
            # Write task file
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)
            
            logger.info(f"Task written to {task_file}")
            
            # Poll for response (timeout after 60 seconds)
            response_file = self.file_exchange_dir / f"response_{task_id}.json"
            start_time = time.time()
            
            while time.time() - start_time < 60:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    # Clean up files
                    task_file.unlink(missing_ok=True)
                    response_file.unlink(missing_ok=True)
                    
                    return {
                        "status": "completed",
                        "result": response_data.get('result', 'Task completed'),
                        "method": "file"
                    }
                
                time.sleep(2)
            
            return {
                "status": "timeout",
                "message": "No response from Cursor within 60 seconds",
                "task_file": str(task_file)
            }
            
        except Exception as e:
            logger.error(f"File-based communication error: {e}")
            return {"status": "error", "message": f"File communication error: {str(e)}"}
    
    def _dispatch_via_url_scheme(self, task_description, context):
        """Open Cursor with task via URL scheme"""
        try:
            # Encode task and context
            task_encoded = urllib.parse.quote(task_description)
            context_encoded = urllib.parse.quote(json.dumps(context))
            
            # Try different Cursor URL schemes
            url_schemes = [
                f"cursor://open?task={task_encoded}&context={context_encoded}",
                f"cursor-ide://task?description={task_encoded}",
                f"cursor://new?prompt={task_encoded}"
            ]
            
            for url in url_schemes:
                try:
                    webbrowser.open(url)
                    logger.info(f"Opened Cursor with URL scheme: {url[:50]}...")
                    return {
                        "status": "pending",
                        "message": "Task opened in Cursor via URL scheme",
                        "url_used": url[:100] + "..."
                    }
                except:
                    continue
                    
            return {"status": "error", "message": "URL scheme not supported"}
            
        except Exception as e:
            logger.error(f"URL scheme error: {e}")
            return {"status": "error", "message": f"URL scheme error: {str(e)}"}
    
    def register_websocket_client(self, client):
        """Register a Cursor WebSocket client"""
        self.websocket_clients.add(client)
        logger.info(f"Cursor WebSocket client registered. Total clients: {len(self.websocket_clients)}")
    
    def unregister_websocket_client(self, client):
        """Unregister a Cursor WebSocket client"""
        self.websocket_clients.discard(client)
        logger.info(f"Cursor WebSocket client unregistered. Total clients: {len(self.websocket_clients)}")


class ClaudeCliAdapter(BaseAgentAdapter):
    """Adapter for communicating with Claude CLI tool"""
    
    def dispatch(self, task_description, context):
        logger.info(f"Dispatching task to Claude CLI: {task_description[:80]}")
        
        try:
            # Prepare the prompt
            prompt = task_description
            if context:
                prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            # Try different command variations
            cmd_variations = [
                ["claude", prompt],  # Standard
                ["claude", "-m", prompt],  # Mit message flag
                ["claude", "chat", prompt],  # Chat subcommand
            ]
            
            # Try to find claude in common locations
            import shutil
            claude_path = shutil.which("claude")
            if claude_path:
                logger.info(f"Found claude at: {claude_path}")
            else:
                # Try common installation paths
                common_paths = [
                    r"C:\Users\%USERNAME%\AppData\Local\Programs\claude\claude.exe",
                    r"C:\Program Files\claude\claude.exe",
                    r"C:\Program Files (x86)\claude\claude.exe",
                    os.path.expanduser("~/.local/bin/claude"),
                    "/usr/local/bin/claude",
                    "/usr/bin/claude"
                ]
                
                for path in common_paths:
                    expanded_path = os.path.expandvars(path)
                    if os.path.exists(expanded_path):
                        claude_path = expanded_path
                        logger.info(f"Found claude at: {claude_path}")
                        break
            
            # Try each command variation
            for cmd in cmd_variations:
                try:
                    # If we found a specific path, use it
                    if claude_path and cmd[0] == "claude":
                        cmd[0] = claude_path
                    
                    logger.debug(f"Trying command: {cmd[0]} [prompt]")
                    
                    # Execute the command
                    result = subprocess.run(
                        cmd,
                        capture_output=True,
                        text=True,
                        timeout=30,
                        shell=False,
                        env={**os.environ, "ANTHROPIC_API_KEY": os.environ.get("ANTHROPIC_API_KEY", "")}
                    )
                    
                    if result.returncode == 0:
                        output = result.stdout.strip()
                        if output:  # Only return if we got actual output
                            logger.info("Claude CLI completed successfully")
                            return {
                                "status": "completed",
                                "result": output,
                                "method": "claude_cli"
                            }
                    else:
                        error = result.stderr.strip() or f"Return code: {result.returncode}"
                        logger.debug(f"Command failed: {error}")
                        
                        # Check for specific error messages
                        if "api key" in error.lower():
                            return {
                                "status": "error",
                                "message": "Claude CLI error: ANTHROPIC_API_KEY not set or invalid",
                                "hint": "Set ANTHROPIC_API_KEY environment variable"
                            }
                        elif "usage limit" in error.lower() or "quota" in error.lower():
                            return {
                                "status": "error",
                                "message": "Claude CLI error: API usage limit exceeded",
                                "hint": "Check your Anthropic account for usage limits"
                            }
                        
                except subprocess.TimeoutExpired:
                    logger.warning(f"Command timed out: {cmd[0]}")
                    continue
                except Exception as e:
                    logger.debug(f"Command failed with exception: {e}")
                    continue
            
            # If all variations failed
            return {
                "status": "error",
                "message": "Claude CLI not working. Ensure 'claude' is installed and ANTHROPIC_API_KEY is set",
                "tried_commands": [cmd[0] for cmd in cmd_variations],
                "hint": "Install with: pip install anthropic-claude-cli"
            }
                
        except Exception as e:
            logger.error(f"Claude CLI dispatch error: {e}")
            return {"status": "error", "message": f"Claude CLI error: {str(e)}"}


class ClaudeDesktopAdapter(BaseAgentAdapter):
    """Multi-method adapter for Claude Desktop integration"""
    
    def __init__(self):
        self.mcp_ports = [3000, 3333, 5000, 5555]  # Common MCP ports
        self.file_exchange_dir = Path("claude_desktop_exchange")
        self.file_exchange_dir.mkdir(exist_ok=True)
        
    def dispatch(self, task_description, context):
        logger.info(f"Dispatching task to Claude Desktop: {task_description[:80]}")
        
        # Try methods in order of preference
        methods = [
            ("MCP Protocol", self._dispatch_via_mcp),
            ("URL Scheme", self._dispatch_via_url_scheme),
            ("File Exchange", self._dispatch_via_file)
        ]
        
        for method_name, method_func in methods:
            result = method_func(task_description, context)
            if result['status'] != 'error':
                logger.info(f"Claude Desktop dispatch successful via {method_name}")
                return result
            else:
                logger.debug(f"{method_name} failed: {result.get('message', 'Unknown error')}")
        
        return {
            "status": "pending",
            "message": "Task queued for Claude Desktop. All methods attempted.",
            "methods_tried": [m[0] for m in methods]
        }
    
    def _dispatch_via_mcp(self, task_description, context):
        """Try MCP protocol on various ports"""
        for port in self.mcp_ports:
            try:
                # Test if port is open
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result != 0:
                    continue
                
                # Port is open, try MCP
                mcp_url = f"http://localhost:{port}/mcp"
                mcp_request = {
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": "execute_task",
                        "arguments": {
                            "task": task_description,
                            "context": context
                        }
                    },
                    "id": str(uuid.uuid4())
                }
                
                response = requests.post(mcp_url, json=mcp_request, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "status": "completed",
                        "result": data.get("result", "Task executed via MCP"),
                        "method": f"mcp_port_{port}"
                    }
                    
            except Exception as e:
                logger.debug(f"MCP on port {port} failed: {e}")
                continue
                
        return {"status": "error", "message": "No MCP server found on common ports"}
    
    def _dispatch_via_url_scheme(self, task_description, context):
        """Open Claude Desktop with task via URL scheme"""
        try:
            # Prepare prompt
            full_prompt = f"Task: {task_description}"
            if context:
                full_prompt += f"\n\nContext: {json.dumps(context, indent=2)}"
            
            # Encode for URL
            prompt_encoded = urllib.parse.quote(full_prompt)
            
            # Try different URL schemes
            url_schemes = [
                f"claude://new?prompt={prompt_encoded}",
                f"claude-desktop://prompt?text={prompt_encoded}",
                f"claude://chat?message={prompt_encoded}"
            ]
            
            for url in url_schemes:
                try:
                    webbrowser.open(url)
                    logger.info(f"Opened Claude Desktop with URL scheme")
                    return {
                        "status": "pending",
                        "message": "Task opened in Claude Desktop",
                        "method": "url_scheme"
                    }
                except:
                    continue
                    
            return {"status": "error", "message": "Claude Desktop URL scheme not supported"}
            
        except Exception as e:
            logger.error(f"URL scheme error: {e}")
            return {"status": "error", "message": f"URL scheme error: {str(e)}"}
    
    def _dispatch_via_file(self, task_description, context):
        """File-based exchange with Claude Desktop"""
        try:
            task_id = str(uuid.uuid4())
            task_file = self.file_exchange_dir / f"claude_task_{task_id}.json"
            
            task_data = {
                "id": task_id,
                "task": task_description,
                "context": context,
                "timestamp": time.time(),
                "source": "HAK_GAL_Multi_Agent"
            }
            
            # Write task file
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)
            
            logger.info(f"Task written to {task_file}")
            
            # Poll for response (30 second timeout)
            response_file = self.file_exchange_dir / f"claude_response_{task_id}.json"
            start_time = time.time()
            
            while time.time() - start_time < 30:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    # Clean up
                    task_file.unlink(missing_ok=True)
                    response_file.unlink(missing_ok=True)
                    
                    return {
                        "status": "completed",
                        "result": response_data.get('result', 'Task completed'),
                        "method": "file_exchange"
                    }
                
                time.sleep(1)
            
            return {
                "status": "timeout",
                "message": "No response from Claude Desktop within 30 seconds",
                "task_file": str(task_file)
            }
            
        except Exception as e:
            logger.error(f"File exchange error: {e}")
            return {"status": "error", "message": f"File exchange error: {str(e)}"}


class GeminiAdapter(BaseAgentAdapter):
    """Adapter for Google Gemini AI"""
    
    def dispatch(self, task_description, context):
        logger.info(f"Dispatching task to Gemini: {task_description[:80]}")
        
        try:
            # Import MultiLLMProvider for Gemini access
            from adapters.llm_providers import MultiLLMProvider
            
            # Initialize Gemini provider
            gemini = MultiLLMProvider()
            
            if not gemini.is_available():
                return {
                    "status": "error",
                    "message": "Gemini API key not configured. Please set GOOGLE_API_KEY environment variable."
                }
            
            # Prepare prompt
            prompt = f"Task: {task_description}\n"
            if context:
                prompt += f"\nContext: {json.dumps(context, indent=2)}\n"
            prompt += "\nPlease complete this task and provide a detailed response."
            
            # Get response from Gemini
            response = gemini.generate_response(prompt)
            
            if response and not response.lower().startswith("error"):
                logger.info("Gemini completed task successfully")
                return {
                    "status": "completed",
                    "result": response,
                    "method": "gemini_api",
                    "model": "gemini-1.5-flash"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Gemini error: {response or 'No response'}"
                }
                
        except ImportError:
            logger.error("MultiLLMProvider not available")
            return {
                "status": "error",
                "message": "Gemini provider not available. Please ensure llm_providers module is installed."
            }
        except Exception as e:
            logger.error(f"Gemini dispatch error: {e}")
            return {
                "status": "error",
                "message": f"Gemini error: {str(e)}"
            }


def get_agent_adapter(agent_name: str, socketio=None):
    if agent_name == 'cursor':
        return CursorAdapter(socketio=socketio)
    elif agent_name == 'claude_cli':
        return ClaudeCliAdapter()
    elif agent_name == 'claude_desktop':
        return ClaudeDesktopAdapter()
    elif agent_name == 'gemini':
        return GeminiAdapter()
    else:
        return None