"""
ClaudeDesktopAdapter Implementation Proposal
===========================================

Here's a production-ready implementation for the ClaudeDesktopAdapter dispatch method.
"""

import subprocess
import requests
import logging
import json
import time
import os
from pathlib import Path

class ClaudeDesktopAdapter(BaseAgentAdapter):
    """Adapter for communicating with Claude Desktop application"""
    
    def __init__(self):
        self.mcp_ports = [3000, 3333, 5000, 5555]  # Common MCP server ports
        self.mcp_endpoint = None
        self.timeout = 60
        
    def discover_mcp_endpoint(self):
        """Auto-discover Claude Desktop MCP endpoint"""
        for port in self.mcp_ports:
            try:
                url = f"http://localhost:{port}/mcp/status"
                response = requests.get(url, timeout=1)
                if response.status_code == 200:
                    data = response.json()
                    if 'claude' in data.get('name', '').lower():
                        logger.info(f"Found Claude Desktop MCP server on port {port}")
                        return f"http://localhost:{port}"
            except:
                continue
        return None
    
    def dispatch(self, task_description, context):
        logger.info("Dispatching task to Claude Desktop...")
        
        # Method 1: Try MCP Protocol (Recommended)
        mcp_result = self._dispatch_via_mcp(task_description, context)
        if mcp_result['status'] != 'error':
            return mcp_result
            
        # Method 2: Try URL Scheme (Opens Claude with prompt)
        url_result = self._dispatch_via_url_scheme(task_description, context)
        if url_result['status'] != 'error':
            return url_result
            
        # Method 3: File-based communication fallback
        file_result = self._dispatch_via_file(task_description, context)
        if file_result['status'] != 'error':
            return file_result
            
        return {
            "status": "error", 
            "message": "All communication methods failed. Ensure Claude Desktop is running and accessible."
        }
    
    def _dispatch_via_mcp(self, task_description, context):
        """Attempt to communicate via MCP protocol"""
        try:
            # Discover endpoint if not cached
            if not self.mcp_endpoint:
                self.mcp_endpoint = self.discover_mcp_endpoint()
                
            if not self.mcp_endpoint:
                return {"status": "error", "message": "MCP endpoint not found"}
            
            # Prepare MCP request
            payload = {
                "jsonrpc": "2.0",
                "method": "completion",
                "params": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "You are part of the HAK/GAL Multi-Agent System. Respond concisely."
                        },
                        {
                            "role": "user",
                            "content": f"{task_description}\n\nContext: {json.dumps(context)}"
                        }
                    ],
                    "max_tokens": 2000
                },
                "id": f"hakgal_{int(time.time())}"
            }
            
            response = requests.post(
                f"{self.mcp_endpoint}/mcp/invoke",
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "completed",
                    "result": result.get('result', {}).get('content', 'No content in response')
                }
            else:
                return {
                    "status": "error",
                    "message": f"MCP request failed with status {response.status_code}"
                }
                
        except Exception as e:
            logger.error(f"MCP communication error: {e}")
            return {"status": "error", "message": f"MCP error: {str(e)}"}
    
    def _dispatch_via_url_scheme(self, task_description, context):
        """Attempt to open Claude Desktop with a pre-filled prompt"""
        try:
            import urllib.parse
            import webbrowser
            
            # Prepare prompt with context
            full_prompt = f"{task_description}\n\nContext:\n{json.dumps(context, indent=2)}"
            encoded_prompt = urllib.parse.quote(full_prompt)
            
            # Try different URL schemes
            url_schemes = [
                f"claude://new?prompt={encoded_prompt}",
                f"anthropic-claude://chat?message={encoded_prompt}",
                f"claude-desktop://new-chat?text={encoded_prompt}"
            ]
            
            for url in url_schemes:
                try:
                    webbrowser.open(url)
                    logger.info(f"Opened Claude Desktop with URL scheme: {url[:50]}...")
                    return {
                        "status": "pending",
                        "message": "Task opened in Claude Desktop. Manual intervention required.",
                        "url_used": url[:100] + "..."
                    }
                except:
                    continue
                    
            return {"status": "error", "message": "URL scheme not supported"}
            
        except Exception as e:
            logger.error(f"URL scheme error: {e}")
            return {"status": "error", "message": f"URL scheme error: {str(e)}"}
    
    def _dispatch_via_file(self, task_description, context):
        """File-based communication as last resort"""
        try:
            # Create exchange directory
            exchange_dir = Path("claude_desktop_exchange")
            exchange_dir.mkdir(exist_ok=True)
            
            # Write request file
            request_id = f"request_{int(time.time() * 1000)}"
            request_file = exchange_dir / f"{request_id}.json"
            
            request_data = {
                "id": request_id,
                "timestamp": time.time(),
                "task": task_description,
                "context": context,
                "source": "HAK_GAL_Multi_Agent"
            }
            
            with open(request_file, 'w', encoding='utf-8') as f:
                json.dump(request_data, f, indent=2)
            
            logger.info(f"Request written to {request_file}")
            
            # Poll for response (timeout after 30 seconds)
            response_file = exchange_dir / f"{request_id}_response.json"
            start_time = time.time()
            
            while time.time() - start_time < 30:
                if response_file.exists():
                    with open(response_file, 'r', encoding='utf-8') as f:
                        response_data = json.load(f)
                    
                    # Clean up files
                    request_file.unlink()
                    response_file.unlink()
                    
                    return {
                        "status": "completed",
                        "result": response_data.get('response', 'No response content')
                    }
                
                time.sleep(1)
            
            return {
                "status": "timeout",
                "message": "No response received within 30 seconds",
                "request_file": str(request_file)
            }
            
        except Exception as e:
            logger.error(f"File-based communication error: {e}")
            return {"status": "error", "message": f"File communication error: {str(e)}"}
