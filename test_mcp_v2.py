#!/usr/bin/env python3
"""
MCP Integration Test - Verify HAK_GAL MCP Server v2
"""

import subprocess
import json
import sys
import time
from pathlib import Path

def test_mcp_server():
    """Test the MCP server with various requests"""
    
    print("=" * 60)
    print("HAK_GAL MCP Server Test Suite")
    print("=" * 60)
    
    # Start server process
    server_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hak_gal_mcp_v2.py")
    
    print(f"\n1. Starting server: {server_path}")
    proc = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    time.sleep(0.5)  # Give server time to start
    
    # Test 1: Initialize
    print("\n2. Testing INITIALIZE...")
    init_request = {
        "jsonrpc": "2.0",
        "method": "initialize",
        "id": 1,
        "params": {}
    }
    
    proc.stdin.write(json.dumps(init_request) + "\n")
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    try:
        response = json.loads(response_line)
        if "result" in response and "capabilities" in response["result"]:
            print("   [OK] Initialize successful")
            print(f"   Tools: {len(response['result']['capabilities'].get('tools', []))} available")
        else:
            print(f"   [ERR] Initialize failed: {response}")
    except Exception as e:
        print(f"   [ERR] Parse error: {e}")
    
    # Test 2: Get System Status
    print("\n3. Testing GET_SYSTEM_STATUS...")
    status_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 2,
        "params": {
            "name": "get_system_status",
            "arguments": {}
        }
    }
    
    proc.stdin.write(json.dumps(status_request) + "\n")
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    try:
        response = json.loads(response_line)
        if "result" in response:
            result = response["result"]
            print("   [OK] Status call successful")
            print(f"   KB Facts: {result.get('kb_facts', 'unknown')}")
            print(f"   Policy: {result.get('policy_version', 'unknown')}")
        else:
            print(f"   [ERR] Status failed: {response}")
    except Exception as e:
        print(f"   [ERR] Parse error: {e}")
    
    # Test 3: Search Knowledge
    print("\n4. Testing SEARCH_KNOWLEDGE...")
    search_request = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "id": 3,
        "params": {
            "name": "search_knowledge",
            "arguments": {
                "query": "Kant",
                "limit": 3
            }
        }
    }
    
    proc.stdin.write(json.dumps(search_request) + "\n")
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    try:
        response = json.loads(response_line)
        if "result" in response:
            result = response["result"]
            print("   [OK] Search successful")
            print(f"   Found: {result.get('count', 0)} facts")
            facts = result.get('facts', [])
            for i, fact in enumerate(facts[:3], 1):
                print(f"   {i}. {fact[:80]}...")
        else:
            print(f"   [ERR] Search failed: {response}")
    except Exception as e:
        print(f"   [ERR] Parse error: {e}")
    
    # Test 4: Shutdown
    print("\n5. Testing SHUTDOWN...")
    shutdown_request = {
        "jsonrpc": "2.0",
        "method": "shutdown",
        "id": 4
    }
    
    proc.stdin.write(json.dumps(shutdown_request) + "\n")
    proc.stdin.flush()
    
    response_line = proc.stdout.readline()
    try:
        response = json.loads(response_line)
        if "result" in response:
            print("   [OK] Shutdown acknowledged")
    except:
        pass
    
    # Wait for process to end
    proc.wait(timeout=2)
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE")
    print("=" * 60)
    
    # Check log file
    log_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/mcp_server_v2.log")
    if log_path.exists():
        print(f"\nServer log exists: {log_path}")
        print("Last 5 log lines:")
        with open(log_path, 'r') as f:
            lines = f.readlines()
            for line in lines[-5:]:
                print(f"  {line.strip()}")
    
    print("\n[OK] If all tests passed, the MCP server is ready for Claude!")
    print("\nNext steps:")
    print("1. Copy claude_config_final.json to %APPDATA%\\Claude\\claude_desktop_config.json")
    print("2. Completely restart Claude Desktop")
    print("3. Check if MCP tools are available in Claude")
    
if __name__ == "__main__":
    test_mcp_server()
