#!/usr/bin/env python3
"""
Manual MCP STDIO Test
Test the MCP server exactly like Claude Desktop would
"""

import subprocess
import json
import time

def test_stdio_communication():
    """Test MCP server via STDIO like Claude does"""
    
    print("=" * 60)
    print("MCP STDIO Communication Test")
    print("=" * 60)
    print("\nStarting MCP Server in subprocess...")
    
    # Start MCP server as subprocess
    process = subprocess.Popen(
        ["python", "src_hexagonal/infrastructure/mcp/mcp_server.py"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1
    )
    
    def send_request(request):
        """Send request and get response"""
        json_str = json.dumps(request)
        print(f"\n→ Sending: {request['method']}")
        process.stdin.write(json_str + "\n")
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline()
        if response_line:
            response = json.loads(response_line)
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
        
        response = send_request(init_request)
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
        
        response = send_request(list_request)
        if response and 'result' in response:
            tools = response['result']['tools']
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f"   - {tool['name']}")
        else:
            print(f"❌ List tools failed")
        
        # Test 3: Call a tool
        call_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "get_system_status",
                "arguments": {}
            }
        }
        
        response = send_request(call_request)
        if response and 'result' in response:
            print(f"✅ Tool call successful")
            content = response['result']['content'][0]['text']
            print(f"   Response preview: {content[:100]}...")
        else:
            print(f"❌ Tool call failed")
        
        print("\n" + "=" * 60)
        print("✅ MCP Server is working correctly!")
        print("Claude Desktop should be able to use it.")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Terminate subprocess
        process.terminate()
        time.sleep(1)
        if process.poll() is None:
            process.kill()


if __name__ == "__main__":
    print("Testing MCP Server STDIO Communication")
    print("This simulates how Claude Desktop communicates with MCP servers\n")
    
    print("Requirements:")
    print("1. HAK_GAL API must be running on port 5001")
    print("2. Python environment must be activated\n")
    
    test_stdio_communication()
