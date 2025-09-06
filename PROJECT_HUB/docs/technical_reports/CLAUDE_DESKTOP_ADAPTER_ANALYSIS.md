"""
ClaudeDesktopAdapter Implementation Analysis
==========================================

## Problem Statement
The ClaudeDesktopAdapter needs a dispatch method implementation to communicate with Claude Desktop application.

## Integration Options Analysis

### 1. MCP Protocol (RECOMMENDED)
Claude Desktop supports MCP (Model Context Protocol). Since HAK_GAL already uses MCP, this is the most natural integration path.

**Advantages:**
- Native support in both systems
- Standardized protocol
- Async-capable
- Full feature support

**Implementation sketch:**
```python
def dispatch(self, task_description, context):
    # Check if Claude Desktop MCP server is running
    mcp_ports = [3000, 3333, 5555]  # Common MCP ports
    
    for port in mcp_ports:
        try:
            response = requests.get(f"http://localhost:{port}/mcp/status", timeout=1)
            if response.status_code == 200:
                # Found Claude Desktop MCP server
                invoke_response = requests.post(
                    f"http://localhost:{port}/mcp/invoke",
                    json={
                        "method": "completion",
                        "params": {
                            "messages": [{"role": "user", "content": task_description}],
                            "context": context
                        }
                    },
                    timeout=60
                )
                return {"status": "completed", "result": invoke_response.json()}
        except:
            continue
    
    return {"status": "error", "message": "Claude Desktop MCP server not found"}
```

### 2. File-based IPC
Create a shared directory where requests/responses are exchanged.

**Advantages:**
- Simple to implement
- Works across all platforms
- No network dependencies

**Disadvantages:**
- Requires file system polling
- Slower than direct communication
- Needs cleanup mechanism

### 3. Named Pipes (Windows) / Unix Sockets (Linux/Mac)
Platform-specific IPC mechanisms.

**Advantages:**
- Fast
- Secure (local only)
- Real-time communication

**Disadvantages:**
- Platform-specific code needed
- More complex implementation

### 4. Local WebSocket Server
If Claude Desktop exposes a WebSocket endpoint.

**Advantages:**
- Real-time bidirectional communication
- Standard web technology
- Event-driven

**Implementation requires:**
- Discovery of WebSocket endpoint
- Authentication mechanism
- Message protocol documentation

## Recommendation

Start with MCP integration as it's the most aligned with both systems' architectures. The implementation should:

1. Auto-discover Claude Desktop MCP endpoint
2. Implement retry logic
3. Handle authentication if required
4. Provide fallback to CLI if MCP fails

## Next Steps

1. Research Claude Desktop's MCP implementation details
2. Test connection to Claude Desktop MCP server
3. Implement the dispatch method with proper error handling
4. Add configuration options for custom ports/endpoints
"""