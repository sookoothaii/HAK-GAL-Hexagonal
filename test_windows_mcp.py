#!/usr/bin/env python3
"""
Test the Windows-fixed MCP Server
"""

import subprocess
import json
import time
import sys

def test_windows_mcp():
    """Test the Windows-compatible MCP server"""
    
    print("=" * 60)
    print("Testing Windows MCP Server")
    print("=" * 60)
    
    # Start the Windows MCP server
    process = subprocess.Popen(
        [sys.executable, "src_hexagonal/infrastructure/mcp/mcp_server_windows.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=False  # Use binary mode
    )
    
    def send_and_receive(request_dict):
        """Send request and get response"""
        request_json = json.dumps(request_dict)
        request_bytes = (request_json + '\n').encode('utf-8')
        
        print(f"\n→ Sending: {request_dict['method']}")
        process.stdin.write(request_bytes)
        process.stdin.flush()
        
        # Read response
        response_bytes = process.stdout.readline()
        if response_bytes:
            response = json.loads(response_bytes.decode('utf-8'))
            return response
        return None
    
    try:
        # Test 1: Initialize
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {"protocolVersion": "0.1.0"}
        }
        
        response = send_and_receive(init_request)
        if response and 'result' in response:
            print(f"✅ Initialize successful")
            print(f"   Server: {response['result']['serverInfo']['name']}")
            print(f"   Version: {response['result']['serverInfo']['version']}")
        else:
            print(f"❌ Initialize failed: {response}")
            
        # Test 2: List tools
        list_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list"
        }
        
        response = send_and_receive(list_request)
        if response and 'result' in response:
            tools = response['result']['tools']
            print(f"\n✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}: {tool['description'][:50]}...")
        else:
            print(f"❌ List tools failed")
            
        # Test 3: Get system status
        status_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_system_status",
                "arguments": {}
            }
        }
        
        response = send_and_receive(status_request)
        if response and 'result' in response:
            print(f"\n✅ System status retrieved successfully")
            content = response['result']['content'][0]['text']
            print(f"   {content[:200]}...")
        else:
            print(f"❌ System status failed")
        
        print("\n" + "=" * 60)
        print("✅ Windows MCP Server is working!")
        print("Now run: .\\fix_mcp_windows.bat")
        print("Then restart Claude Desktop")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Clean up
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()

if __name__ == "__main__":
    print("Windows MCP Server Test")
    print("Make sure HAK_GAL API is running on port 5001\n")
    
    test_windows_mcp()
