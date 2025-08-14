#!/usr/bin/env python3
"""
Debug why Claude Desktop can't load MCP server
Check all potential issues
"""

import os
import sys
import json
import subprocess
from pathlib import Path

def check_issue():
    """Comprehensive MCP debugging"""
    
    print("=" * 70)
    print(" MCP DEBUGGING - Finding why Claude can't load the server")
    print("=" * 70)
    
    # 1. Check Python paths
    print("\n1. PYTHON PATHS:")
    print("-" * 40)
    
    venv_python = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\.venv_hexa\Scripts\python.exe")
    if venv_python.exists():
        print(f"✅ Venv Python exists: {venv_python}")
        
        # Test if it works
        try:
            result = subprocess.run(
                [str(venv_python), "--version"],
                capture_output=True,
                text=True
            )
            print(f"   Version: {result.stdout.strip()}")
        except Exception as e:
            print(f"❌ Can't run venv Python: {e}")
    else:
        print(f"❌ Venv Python NOT found at: {venv_python}")
    
    # 2. Check MCP server file
    print("\n2. MCP SERVER FILES:")
    print("-" * 40)
    
    mcp_server = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\mcp\mcp_server_windows.py")
    if mcp_server.exists():
        print(f"✅ MCP server exists: {mcp_server}")
        print(f"   Size: {mcp_server.stat().st_size} bytes")
    else:
        print(f"❌ MCP server NOT found")
    
    # 3. Check Claude config
    print("\n3. CLAUDE CONFIG:")
    print("-" * 40)
    
    config_path = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json'
    if config_path.exists():
        print(f"✅ Config exists: {config_path}")
        
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        if 'mcpServers' in config:
            print("   MCP Servers configured:")
            for name, server_config in config['mcpServers'].items():
                print(f"   - {name}:")
                print(f"     Command: {server_config.get('command', 'N/A')}")
                if 'args' in server_config:
                    print(f"     Args: {server_config['args'][0] if server_config['args'] else 'N/A'}")
        else:
            print("   ❌ No mcpServers section in config!")
    else:
        print(f"❌ Config NOT found at: {config_path}")
    
    # 4. Test manual server start
    print("\n4. MANUAL SERVER TEST:")
    print("-" * 40)
    
    if venv_python.exists() and mcp_server.exists():
        print("Testing if server can start...")
        
        # Create test command
        cmd = [str(venv_python), str(mcp_server)]
        
        print(f"Command: {' '.join(cmd)}")
        
        try:
            # Start process
            process = subprocess.Popen(
                cmd,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send initialize
            init_request = '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}\n'
            stdout, stderr = process.communicate(input=init_request, timeout=5)
            
            if stdout:
                print("✅ Server responds!")
                print(f"   Response: {stdout[:100]}...")
            else:
                print("❌ No response from server")
                if stderr:
                    print(f"   Error: {stderr[:200]}")
                    
            process.terminate()
            
        except subprocess.TimeoutExpired:
            print("❌ Server timeout")
            process.terminate()
        except Exception as e:
            print(f"❌ Can't start server: {e}")
    
    # 5. Space in path issue
    print("\n5. PATH ISSUES:")
    print("-" * 40)
    
    if " " in str(venv_python):
        print("⚠️  WARNING: Path contains spaces!")
        print("   This can cause issues with Claude Desktop")
        print("   Path: " + str(venv_python))
        print("\n   SOLUTION OPTIONS:")
        print("   a) Use 8.3 short names (if enabled)")
        
        # Try to get short path
        try:
            import ctypes
            from ctypes import wintypes
            
            GetShortPathName = ctypes.windll.kernel32.GetShortPathNameW
            GetShortPathName.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
            GetShortPathName.restype = wintypes.DWORD
            
            long_path = str(venv_python)
            short_length = GetShortPathName(long_path, None, 0)
            
            if short_length > 0:
                short_path = ctypes.create_unicode_buffer(short_length)
                GetShortPathName(long_path, short_path, short_length)
                print(f"      Short path: {short_path.value}")
            else:
                print("      8.3 names not available")
                
        except Exception as e:
            print(f"      Can't get short path: {e}")
            
        print("   b) Create a symlink without spaces")
        print("   c) Move project to path without spaces")
    else:
        print("✅ No spaces in Python path")
    
    # 6. Recommendations
    print("\n" + "=" * 70)
    print(" RECOMMENDATIONS:")
    print("=" * 70)
    
    print("\n1. Run: .\\install_full_path_config.bat")
    print("2. Completely restart Claude Desktop")
    print("3. Check Claude logs at: %APPDATA%\\Claude\\logs\\")
    print("4. Look for 'spawn' or 'error' messages in logs")
    
    if " " in str(venv_python):
        print("\n⚠️  SPECIAL NOTE: The space in 'MCP Mods' might be the issue!")
        print("Consider creating a junction without spaces:")
        print('   mklink /J "D:\\HAK_GAL" "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"')
        print("Then use D:\\HAK_GAL in the config instead")

if __name__ == "__main__":
    check_issue()
