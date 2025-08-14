#!/usr/bin/env python3
"""
Direct MCP Server Test
Simulates Claude Desktop communication
"""

import json
import asyncio
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_mcp_server():
    """Test MCP server with simulated requests"""
    
    # Import the MCP server
    from src_hexagonal.infrastructure.mcp.mcp_server import MCPServer
    
    server = MCPServer()
    
    print("=" * 60)
    print("Direct MCP Server Test")
    print("=" * 60)
    
    # Test 1: Initialize
    print("\n1. Testing Initialize...")
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    }
    
    response = await server.handle_request(init_request)
    print(f"Response: {json.dumps(response, indent=2)}")
    
    # Test 2: List tools
    print("\n2. Testing List Tools...")
    list_request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    }
    
    response = await server.handle_request(list_request)
    print(f"Available tools: {len(response['result']['tools'])}")
    for tool in response['result']['tools']:
        print(f"  - {tool['name']}: {tool['description']}")
    
    # Test 3: Search knowledge
    print("\n3. Testing Search Knowledge...")
    search_request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "search_knowledge",
            "arguments": {
                "query": "neural",
                "limit": 3
            }
        }
    }
    
    response = await server.handle_request(search_request)
    if 'result' in response:
        content = response['result']['content'][0]['text']
        print(f"Search result:\n{content}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
    
    # Test 4: Get system status
    print("\n4. Testing System Status...")
    status_request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "tools/call",
        "params": {
            "name": "get_system_status",
            "arguments": {}
        }
    }
    
    response = await server.handle_request(status_request)
    if 'result' in response:
        content = response['result']['content'][0]['text']
        print(f"Status:\n{content}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
    
    # Test 5: Neural reasoning
    print("\n5. Testing Neural Reasoning...")
    reasoning_request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {
            "name": "neural_reasoning",
            "arguments": {
                "query": "What is machine learning?"
            }
        }
    }
    
    response = await server.handle_request(reasoning_request)
    if 'result' in response:
        content = response['result']['content'][0]['text']
        print(f"Reasoning:\n{content}")
    else:
        print(f"Error: {response.get('error', 'Unknown error')}")
    
    print("\n" + "=" * 60)
    print("MCP Server Test Complete")
    print("=" * 60)


if __name__ == "__main__":
    print("Starting MCP Server Test...")
    print("\nMake sure HAK_GAL API is running on port 5001!\n")
    
    asyncio.run(test_mcp_server())
