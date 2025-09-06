"""
Adapters for Communicating with External AI Agents
ENHANCED WITH RESPONSE LOGGING SYSTEM
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
import threading
from datetime import datetime

# Response Storage Directory
RESPONSE_DIR = Path("agent_responses")
RESPONSE_DIR.mkdir(exist_ok=True)

# Create subdirectories for organization
(RESPONSE_DIR / "success").mkdir(exist_ok=True)
(RESPONSE_DIR / "error").mkdir(exist_ok=True)
(RESPONSE_DIR / "by_agent").mkdir(exist_ok=True)

logger = logging.getLogger(__name__)

class ResponseLogger:
    """Centralized response logging system"""
    
    @staticmethod
    def save_response(task_id, agent_name, task_description, context, response_data):
        """Save agent response to multiple locations for easy access"""
        try:
            timestamp = datetime.now().isoformat()
            filename = f"{timestamp.replace(':', '-')}_{task_id}_{agent_name}.json"
            
            # Determine status
            status = response_data.get('status', 'unknown')
            status_dir = "success" if status in ['completed', 'dispatched', 'pending'] else "error"
            
            # Full response data
            full_data = {
                "task_id": task_id,
                "agent": agent_name,
                "timestamp": timestamp,
                "request": {
                    "task_description": task_description,
                    "context": context
                },
                "response": response_data
            }
            
            # Save in status directory
            status_path = RESPONSE_DIR / status_dir / filename
            with open(status_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            
            # Save in agent directory
            agent_dir = RESPONSE_DIR / "by_agent" / agent_name
            agent_dir.mkdir(exist_ok=True)
            agent_path = agent_dir / filename
            with open(agent_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            
            # Save as 'latest' for agent
            latest_path = agent_dir / "latest.json"
            with open(latest_path, 'w', encoding='utf-8') as f:
                json.dump(full_data, f, indent=2, ensure_ascii=False)
            
            # Update index
            ResponseLogger.update_index(full_data)
            
            logger.info(f"Response saved to {status_path}")
            
            # If it's a Gemini response with actual content, log it prominently
            if agent_name == "gemini" and status == "completed":
                result = response_data.get('result', '')
                if result:
                    logger.info(f"GEMINI RESPONSE: {result[:200]}...")
                    
                    # Save Gemini response separately for easy access
                    gemini_response_file = RESPONSE_DIR / f"gemini_latest_response.txt"
                    with open(gemini_response_file, 'w', encoding='utf-8') as f:
                        f.write(f"Task: {task_description}\n")
                        f.write(f"Timestamp: {timestamp}\n")
                        f.write(f"Response:\n{result}")
            
            return str(status_path)
            
        except Exception as e:
            logger.error(f"Failed to save response: {e}")
            return None
    
    @staticmethod
    def update_index(response_data):
        """Update response index for quick lookups"""
        try:
            index_path = RESPONSE_DIR / "index.json"
            
            # Load existing index
            if index_path.exists():
                with open(index_path, 'r', encoding='utf-8') as f:
                    index = json.load(f)
            else:
                index = {"responses": [], "by_task_id": {}, "by_agent": {}}
            
            # Create index entry
            entry = {
                "task_id": response_data["task_id"],
                "agent": response_data["agent"],
                "timestamp": response_data["timestamp"],
                "status": response_data["response"].get("status", "unknown"),
                "preview": str(response_data["response"].get("result", ""))[:100] + "..."
            }
            
            # Update index
            index["responses"].insert(0, entry)
            index["by_task_id"][response_data["task_id"]] = entry
            
            agent_name = response_data["agent"]
            if agent_name not in index["by_agent"]:
                index["by_agent"][agent_name] = []
            index["by_agent"][agent_name].insert(0, entry)
            
            # Keep only last 1000 entries
            index["responses"] = index["responses"][:1000]
            
            # Save updated index
            with open(index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            logger.error(f"Failed to update index: {e}")


class BaseAgentAdapter:
    def __init__(self):
        self.response_dir = Path("agent_responses")
        self.response_dir.mkdir(exist_ok=True)
    
    def dispatch(self, task_description, context):
        raise NotImplementedError
    
    def save_response(self, task_id, agent, task_description, context, response):
        """Speichere Agent-Response für Audit und Debugging"""
        try:
            timestamp = datetime.now().isoformat().replace(":", "-")
            filename = f"{timestamp}_{task_id}_{agent}.json"
            filepath = self.response_dir / filename
            
            response_data = {
                "task_id": task_id,
                "agent": agent,
                "timestamp": timestamp,
                "request": {
                    "task_description": task_description,
                    "context": context
                },
                "response": response
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(response_data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Response gespeichert: {filename}")
            
        except Exception as e:
            logger.error(f"Fehler beim Speichern der Response: {e}")


class CursorAdapter(BaseAgentAdapter):
    """Advanced adapter for communicating with Cursor IDE"""
    
    def __init__(self, socketio=None):
        super().__init__()
        self.socketio = socketio  # Store socketio instance
        self.websocket_clients = set()  # Track connected Cursor clients
        self.mcp_port = 3000  # Default MCP port for Cursor
        self.file_exchange_dir = Path("cursor_exchange")
        self.file_exchange_dir.mkdir(exist_ok=True)
        
    def dispatch(self, task_description, context):
        task_id = str(uuid.uuid4())
        logger.info(f"Dispatching task to Cursor: {task_description[:80]}")
        
        result = {"status": "error", "message": "Unknown error during dispatch", "task_id": task_id} # Default error result

        try:
            task_file = self.file_exchange_dir / f"task_{task_id}.json"
            task_data = {
                "task_id": task_id,
                "task": task_description,
                "context": context,
                "timestamp": time.time(),
                "status": "pending"
            }
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2, ensure_ascii=False)
            logger.info(f"Task written to {task_file}")
            
            result = {
                "status": "pending",
                "message": f"Task queued for Cursor in {task_file.name}",
                "task_id": task_id,
                "method": "file_exchange"
            }
            
            # Log timeout after 60 seconds (but don't block)
            import threading
            def log_timeout():
                time.sleep(60)
                timeout_result = {
                    "status": "timeout",
                    "message": "No response from Cursor within 60 seconds",
                    "task_id": task_id
                }
                self.save_response(task_id, "cursor", task_description, context, timeout_result)
            
            timeout_thread = threading.Thread(target=log_timeout, daemon=True)
            timeout_thread.start()
            
        except Exception as e:
            logger.error(f"Failed to dispatch to Cursor: {e}")
            result = {
                "status": "error",
                "message": f"Failed to dispatch: {str(e)}",
                "task_id": task_id
            }
        finally:
            # Ensure response is always saved, regardless of success or failure
            self.save_response(task_id, "cursor", task_description, context, result)
            return result
    
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
            # Fix the error - use task_file instead of request_file
            with open(task_file, 'a') as f:
                f.write(f"\nError: {str(e)}\n{task_file}")
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
    """
    Adapter for Claude CLI using a file-based exchange mechanism.
    Waits for a client-side watcher to process tasks.
    """
    def __init__(self):
        super().__init__()
        self.file_exchange_dir = Path("claude_cli_exchange")
        self.file_exchange_dir.mkdir(exist_ok=True)
        self.timeout = 60  # seconds

    def dispatch(self, task_description, context):
        task_id = str(uuid.uuid4())
        logger.info(f"Dispatching task to Claude CLI via file exchange: {task_description[:80]}")
        
        response = {}
        task_file = self.file_exchange_dir / f"task_{task_id}.json"
        response_file = self.file_exchange_dir / f"response_{task_id}.json"

        try:
            # 1. Write task file
            task_data = {
                "id": task_id,
                "task": task_description,
                "context": context,
                "timestamp": time.time()
            }
            with open(task_file, 'w', encoding='utf-8') as f:
                json.dump(task_data, f, indent=2)
            logger.info(f"Task written to {task_file}")

            # 2. Poll for response file
            start_time = time.time()
            while time.time() - start_time < self.timeout:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    response = {
                        "status": "completed",
                        "result": response_data.get('result', 'Task completed'),
                        "method": "file_exchange"
                    }
                    break
                time.sleep(2)
            
            if not response: # If response is still empty, it timed out
                response = {
                    "status": "timeout",
                    "message": f"No response from watcher within {self.timeout} seconds."
                }

        except Exception as e:
            logger.error(f"Claude CLI file exchange error: {e}")
            response = {"status": "error", "message": f"File exchange error: {str(e)}"}
        
        finally:
            # 3. Clean up files and save the final response log
            task_file.unlink(missing_ok=True)
            response_file.unlink(missing_ok=True)
            self.save_response(task_id, "claude_cli", task_description, context, response)

        return response


class ClaudeDesktopAdapter(BaseAgentAdapter):
    """Multi-method adapter for Claude Desktop integration"""
    
    def __init__(self):
        super().__init__()
        self.mcp_ports = [3000, 3333, 5000, 5555]  # Common MCP ports
        self.file_exchange_dir = Path("claude_desktop_exchange")
        self.file_exchange_dir.mkdir(exist_ok=True)
        
    def dispatch(self, task_description, context):
        task_id = str(uuid.uuid4())
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
                result['task_id'] = task_id
                self.save_response(task_id, "claude_desktop", task_description, context, result)
                return result
            else:
                logger.debug(f"{method_name} failed: {result.get('message', 'Unknown error')}")
        
        response = {
            "status": "pending",
            "message": "Task queued for Claude Desktop. All methods attempted.",
            "methods_tried": [m[0] for m in methods],
            "task_id": task_id
        }
        self.save_response(task_id, "claude_desktop", task_description, context, response)
        return response
    
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
    """Echte Google Gemini AI Integration mit 2.5 Pro und Flash Fallback"""
    
    def __init__(self):
        super().__init__()
        self.api_key = os.environ.get('GOOGLE_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"
        # Gemini 2.5 Pro als primäres Modell, 2.5 Flash als Fallback
        self.primary_model = "gemini-2.5-pro"
        self.fallback_model = "gemini-2.5-flash"
        self.current_model = self.primary_model  # Start mit Pro
        
    def dispatch(self, task_description, context):
        task_id = str(uuid.uuid4())
        logger.info(f"Dispatching task to Gemini: {task_description[:80]}")
        
        if not self.api_key:
            response = {
                "status": "error",
                "message": "GOOGLE_API_KEY nicht gesetzt",
                "task_id": task_id
            }
            self.save_response(task_id, "gemini", task_description, context, response)
            return response
        
        try:
            # Echte Gemini API aufrufen
            result = self._call_gemini_api(task_description, context)
            result['task_id'] = task_id
            self.save_response(task_id, "gemini", task_description, context, result)
            return result
            
        except Exception as e:
            response = {
                "status": "error", 
                "message": f"Gemini API Fehler: {str(e)}",
                "task_id": task_id
            }
            self.save_response(task_id, "gemini", task_description, context, response)
            return response
    
    def _call_gemini_api(self, task_description, context):
        """Echte Google Gemini API aufrufen mit Fallback"""
        # Zuerst mit Primary Model versuchen
        result = self._try_model(self.primary_model, task_description, context)
        
        # Falls Primary fehlschlägt, mit Fallback versuchen
        if result.get("status") == "error" and "Gemini API Fehler: 404" in result.get("message", ""):
            logger.warning(f"Primary model {self.primary_model} nicht verfügbar, verwende Fallback {self.fallback_model}")
            result = self._try_model(self.fallback_model, task_description, context)
            if result.get("status") == "completed":
                result["fallback_used"] = True
                result["attempted_model"] = self.primary_model
        
        return result
    
    def _try_model(self, model_name, task_description, context):
        """Versuche einen spezifischen Gemini Model-Aufruf"""
        url = f"{self.base_url}/{model_name}:generateContent?key={self.api_key}"
        
        # Prompt erstellen
        prompt = f"Task: {task_description}\n"
        if context:
            prompt += f"\nContext: {json.dumps(context, indent=2, ensure_ascii=False)}\n"
        prompt += "\nBitte bearbeite diese Aufgabe und gib eine detaillierte Antwort."
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "topK": 40,
                "topP": 0.95,
                "maxOutputTokens": 2048
            }
        }
        
        start_time = time.time()
        try:
            response = requests.post(url, json=payload, timeout=30)
            duration = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                data = response.json()
                if 'candidates' in data and data['candidates']:
                    content = data['candidates'][0]['content']['parts'][0]['text']
                    
                    return {
                        "status": "completed",
                        "result": content,
                        "method": "gemini_api",
                        "model": model_name,
                        "duration_ms": int(duration),
                        "tokens_used": data.get('usageMetadata', {}).get('totalTokenCount')
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Keine Antwort von Gemini API ({model_name})",
                        "model": model_name,
                        "duration_ms": int(duration)
                    }
            else:
                return {
                    "status": "error",
                    "message": f"Gemini API Fehler: {response.status_code} - {response.text[:200]}",
                    "model": model_name,
                    "duration_ms": int(duration)
                }
        except Exception as e:
            duration = (time.time() - start_time) * 1000
            return {
                "status": "error",
                "message": f"Gemini API Exception ({model_name}): {str(e)}",
                "model": model_name,
                "duration_ms": int(duration)
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
