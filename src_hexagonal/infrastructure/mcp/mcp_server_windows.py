#!/usr/bin/env python3
"""
HAK_GAL MCP Server - Windows-kompatible Version
Verfassung-konform nach Artikel 6 (Empirische Validierung) und Artikel 4 (Transparenz)
"""

import json
import sys
import asyncio
import httpx
from typing import Dict, List, Any, Optional
from pathlib import Path
import logging
import os

# Disable buffering for Windows
if os.name == 'nt':
    import msvcrt
    msvcrt.setmode(sys.stdin.fileno(), os.O_BINARY)
    msvcrt.setmode(sys.stdout.fileno(), os.O_BINARY)

# MCP Protocol basics
class MCPServer:
    """Minimal MCP Server für HAK_GAL - Windows-kompatibel"""
    
    def __init__(self, name: str = "hak-gal-knowledge"):
        self.name = name
        self.version = "1.0.0"
        self.hak_gal_api_url = "http://127.0.0.1:5001"  # HAK_GAL API
        
        # Tools registry
        self.tools = {
            "search_knowledge": {
                "description": "Search HAK_GAL knowledge base for facts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Search query"},
                        "limit": {"type": "integer", "default": 5, "minimum": 1, "maximum": 20}
                    },
                    "required": ["query"]
                }
            },
            "get_system_status": {
                "description": "Get HAK_GAL system status and metrics",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            "neural_reasoning": {
                "description": "Perform neural reasoning using HRM engine",
                "inputSchema": {
                    "type": "object", 
                    "properties": {
                        "query": {"type": "string", "description": "Query for reasoning"}
                    },
                    "required": ["query"]
                }
            },
            "list_recent_facts": {
                "description": "List recent facts from knowledge base",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "count": {"type": "integer", "default": 10, "minimum": 1, "maximum": 50}
                    }
                }
            }
        }
        
        # Setup logging to stderr to avoid interfering with stdio
        logging.basicConfig(
            level=logging.INFO, 
            format='%(asctime)s - %(message)s',
            stream=sys.stderr
        )
        self.logger = logging.getLogger(__name__)
        
    async def handle_request(self, request: Dict) -> Dict:
        """Handle incoming MCP request"""
        
        method = request.get("method")
        request_id = request.get("id", 1)
        
        try:
            if method == "initialize":
                return self._create_response(request_id, self._handle_initialize())
            elif method == "tools/list":
                return self._create_response(request_id, self._handle_list_tools())
            elif method == "tools/call":
                params = request.get("params", {})
                result = await self._handle_tool_call(params)
                return self._create_response(request_id, result)
            else:
                return self._create_error_response(request_id, f"Unknown method: {method}")
                
        except Exception as e:
            self.logger.error(f"Error handling request: {e}")
            return self._create_error_response(request_id, str(e))
    
    def _handle_initialize(self) -> Dict:
        """Handle initialize request"""
        return {
            "protocolVersion": "0.1.0",
            "capabilities": {
                "tools": True,
                "resources": False,
                "prompts": False
            },
            "serverInfo": {
                "name": self.name,
                "version": self.version
            }
        }
    
    def _handle_list_tools(self) -> Dict:
        """List available tools"""
        tools_list = []
        for name, config in self.tools.items():
            tools_list.append({
                "name": name,
                "description": config["description"],
                "inputSchema": config["inputSchema"]
            })
        return {"tools": tools_list}
    
    async def _handle_tool_call(self, params: Dict) -> Dict:
        """Execute tool call"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        if tool_name not in self.tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        
        # Route to appropriate handler
        if tool_name == "search_knowledge":
            return await self._search_knowledge(arguments)
        elif tool_name == "get_system_status":
            return await self._get_system_status()
        elif tool_name == "neural_reasoning":
            return await self._neural_reasoning(arguments)
        elif tool_name == "list_recent_facts":
            return await self._list_recent_facts(arguments)
        else:
            raise ValueError(f"Tool not implemented: {tool_name}")
    
    async def _search_knowledge(self, args: Dict) -> Dict:
        """Search knowledge base - READ ONLY"""
        query = args.get("query", "")
        limit = args.get("limit", 5)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.hak_gal_api_url}/api/search",
                    json={"query": query, "limit": limit},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Found {len(data.get('results', []))} facts:\n" + 
                                   "\n".join([f"- {fact}" for fact in data.get('results', [])])
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Search failed with status {response.status_code}"
                        }]
                    }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error searching knowledge base: {str(e)}"
                    }]
                }
    
    async def _get_system_status(self) -> Dict:
        """Get system status - READ ONLY"""
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.hak_gal_api_url}/api/status",
                    params={"light": "1"},
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    status_text = f"""HAK_GAL System Status:
- Architecture: {data.get('architecture', 'unknown')}
- Facts loaded: {data.get('kb_facts_count', 0)}
- Neural reasoning: {data.get('neural_reasoning_available', False)}
- LLM providers: {', '.join(data.get('llm_providers', []))}"""
                    
                    return {
                        "content": [{
                            "type": "text",
                            "text": status_text
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Status check failed with code {response.status_code}"
                        }]
                    }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error getting status: {str(e)}"
                    }]
                }
    
    async def _neural_reasoning(self, args: Dict) -> Dict:
        """Neural reasoning - READ ONLY"""
        query = args.get("query", "")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.hak_gal_api_url}/api/reason",
                    json={"query": query},
                    timeout=15.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    reasoning_text = f"""Neural Reasoning Result:
Query: {query}
Confidence: {data.get('confidence', 0):.4f}
Result: {data.get('result', 'No result')}"""
                    
                    return {
                        "content": [{
                            "type": "text",
                            "text": reasoning_text
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Reasoning failed with status {response.status_code}"
                        }]
                    }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error in neural reasoning: {str(e)}"
                    }]
                }
    
    async def _list_recent_facts(self, args: Dict) -> Dict:
        """List recent facts - READ ONLY"""
        count = args.get("count", 10)
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.hak_gal_api_url}/api/facts",
                    params={"limit": count},
                    timeout=10.0
                )
                
                if response.status_code == 200:
                    data = response.json()
                    facts = data.get('facts', [])
                    facts_text = f"Recent {len(facts)} facts from knowledge base:\n"
                    facts_text += "\n".join([f"{i+1}. {fact}" for i, fact in enumerate(facts)])
                    
                    return {
                        "content": [{
                            "type": "text",
                            "text": facts_text
                        }]
                    }
                else:
                    return {
                        "content": [{
                            "type": "text",
                            "text": f"Failed to get facts with status {response.status_code}"
                        }]
                    }
            except Exception as e:
                return {
                    "content": [{
                        "type": "text",
                        "text": f"Error listing facts: {str(e)}"
                    }]
                }
    
    def _create_response(self, request_id: Any, result: Any) -> Dict:
        """Create JSON-RPC response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result
        }
    
    def _create_error_response(self, request_id: Any, error_message: str) -> Dict:
        """Create JSON-RPC error response"""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": error_message
            }
        }
    
    def run_stdio_sync(self):
        """Synchronous STDIO handler for Windows compatibility"""
        self.logger.info("HAK_GAL MCP Server starting (Windows STDIO mode)...")
        
        # Use synchronous I/O for Windows
        stdin = sys.stdin.buffer if hasattr(sys.stdin, 'buffer') else sys.stdin
        stdout = sys.stdout.buffer if hasattr(sys.stdout, 'buffer') else sys.stdout
        
        buffer = b""
        
        while True:
            try:
                # Read chunks from stdin
                chunk = stdin.read(1)
                if not chunk:
                    break
                    
                buffer += chunk
                
                # Look for newline
                if b'\n' in buffer:
                    line, buffer = buffer.split(b'\n', 1)
                    
                    # Parse JSON request
                    request = json.loads(line.decode('utf-8'))
                    self.logger.info(f"Received request: {request.get('method')}")
                    
                    # Handle request asynchronously
                    loop = asyncio.new_event_loop()
                    response = loop.run_until_complete(self.handle_request(request))
                    loop.close()
                    
                    # Write response
                    response_bytes = (json.dumps(response) + '\n').encode('utf-8')
                    stdout.write(response_bytes)
                    stdout.flush()
                    
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON decode error: {e}")
                error_response = self._create_error_response(None, f"Invalid JSON: {str(e)}")
                response_bytes = (json.dumps(error_response) + '\n').encode('utf-8')
                stdout.write(response_bytes)
                stdout.flush()
                buffer = b""  # Clear buffer after error
                
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                error_response = self._create_error_response(None, str(e))
                response_bytes = (json.dumps(error_response) + '\n').encode('utf-8')
                stdout.write(response_bytes)
                stdout.flush()


def main():
    """Main entry point - Windows compatible"""
    server = MCPServer()
    
    # Use synchronous mode for Windows
    if os.name == 'nt':
        server.run_stdio_sync()
    else:
        # Use async for Unix-like systems
        asyncio.run(server.run_stdio())


if __name__ == "__main__":
    # Disable output buffering
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 1)
    sys.stderr = os.fdopen(sys.stderr.fileno(), 'w', 1)
    
    # Run the server
    main()
