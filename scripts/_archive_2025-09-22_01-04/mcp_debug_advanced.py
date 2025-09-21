#!/usr/bin/env python3
"""
Advanced MCP Debug Script for HAK_GAL Integration
Research Project: Getting MCP to work with Claude Desktop
"""

import json
import subprocess
import sys
import time
from pathlib import Path
import socket
import psutil
import os

def check_port(port):
    """Check if port is in use"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result == 0
    except:
        return False

def find_claude_processes():
    """Find all Claude-related processes"""
    claude_procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            if 'claude' in name or 'electron' in name:
                claude_procs.append({
                    'pid': proc.info['pid'],
                    'name': proc.info['name'],
                    'cmdline': ' '.join(proc.info['cmdline'] or [])[:100]
                })
        except:
            pass
    return claude_procs

def test_mcp_server():
    """Test if MCP server responds correctly"""
    print("\n🔬 Testing MCP Server Response...")
    
    # Test with minimal request
    test_cmd = [
        sys.executable,
        "-m", "hak_gal_mcp",
        "--test-mode"
    ]
    
    try:
        # Set environment for test
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path.cwd())
        
        result = subprocess.run(
            test_cmd,
            capture_output=True,
            text=True,
            timeout=5,
            env=env,
            cwd="D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
        )
        
        print(f"Return code: {result.returncode}")
        if result.stdout:
            print(f"Output preview: {result.stdout[:200]}")
        if result.stderr:
            print(f"Errors: {result.stderr[:200]}")
            
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def check_config_format():
    """Verify MCP config format"""
    config_path = Path(r"C:\Users\bunya\AppData\Roaming\Claude\claude_desktop_config.json")
    
    if not config_path.exists():
        print("❌ Config file not found!")
        return False
        
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
            
        print("\n📋 Config Structure:")
        print(json.dumps(config, indent=2)[:500])
        
        # Check for MCP servers
        if 'mcpServers' in config:
            servers = config['mcpServers']
            if 'hak-gal' in servers:
                server_config = servers['hak-gal']
                print("\n✅ HAK-GAL server found in config")
                print(f"Command: {server_config.get('command', [])[:2]}")
                print(f"Args: {server_config.get('args', [])}")
                
                # Validate structure
                issues = []
                if not isinstance(server_config.get('command'), list):
                    issues.append("Command should be a list")
                if 'env' in server_config and not isinstance(server_config['env'], dict):
                    issues.append("Env should be a dict")
                    
                if issues:
                    print(f"⚠️ Config issues: {', '.join(issues)}")
                    return False
                    
                return True
            else:
                print("❌ hak-gal server not in mcpServers")
        else:
            print("❌ No mcpServers section in config")
            
    except Exception as e:
        print(f"❌ Config parse error: {e}")
        return False
        
    return False

def create_test_server():
    """Create a minimal test MCP server"""
    test_server = '''#!/usr/bin/env python3
"""Minimal MCP Test Server"""
import sys
import json

# Send capabilities
capabilities = {
    "jsonrpc": "2.0",
    "id": 1,
    "result": {
        "capabilities": {
            "tools": {
                "test_tool": {
                    "description": "Test tool",
                    "inputSchema": {
                        "type": "object",
                        "properties": {}
                    }
                }
            }
        }
    }
}

sys.stdout.write(json.dumps(capabilities) + "\\n")
sys.stdout.flush()

# Keep alive
while True:
    line = sys.stdin.readline()
    if not line:
        break
'''
    
    test_path = Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\mcp_test_minimal.py")
    test_path.write_text(test_server)
    print(f"✅ Created minimal test server: {test_path}")
    return test_path

def suggest_fixes():
    """Suggest specific fixes based on diagnosis"""
    print("\n🔧 EMPFOHLENE FIXES:")
    print("=" * 60)
    
    print("""
1. MCP Server Start-Script erstellen:
   Erstellen Sie 'start_mcp.bat':
   ```
   @echo off
   cd /d "D:\\MCP Mods\\HAK_GAL_HEXAGONAL"
   python -m hak_gal_mcp
   ```

2. Alternative Config-Format testen:
   ```json
   {
     "mcpServers": {
       "hak-gal": {
         "command": ["python"],
         "args": ["-m", "hak_gal_mcp"],
         "cwd": "D:\\\\MCP Mods\\\\HAK_GAL_HEXAGONAL"
       }
     }
   }
   ```

3. Debug-Logging aktivieren:
   - Claude neu starten mit: claude.exe --enable-logging --v=1
   - Logs prüfen in: %APPDATA%\\Claude\\logs\\

4. Python PATH sicherstellen:
   - Systemvariable PATH prüfen
   - 'where python' in CMD ausführen
   
5. MCP Development Mode:
   Falls verfügbar in Claude Settings:
   Settings → Developer → Enable MCP Development Mode
""")

def main():
    print("=" * 60)
    print("HAK_GAL MCP Integration Debug - Research Mode")
    print("=" * 60)
    
    # 1. Check ports
    print("\n📡 Port Status:")
    print(f"Port 5000 (alte API): {'✅ Active' if check_port(5000) else '❌ Inactive'}")
    print(f"Port 5001 (HexBackend): {'✅ Active' if check_port(5001) else '❌ Inactive'}")
    
    # 2. Check Claude processes
    print("\n🔍 Claude Processes:")
    procs = find_claude_processes()
    for proc in procs[:3]:  # Show max 3
        print(f"  PID {proc['pid']}: {proc['name']}")
    
    # 3. Test Python environment
    print("\n🐍 Python Environment:")
    print(f"Python: {sys.executable}")
    print(f"Version: {sys.version.split()[0]}")
    print(f"CWD: {os.getcwd()}")
    
    # 4. Check config
    print("\n📁 Config Check:")
    config_ok = check_config_format()
    
    # 5. Test MCP server
    if not test_mcp_server():
        print("\n⚠️ Creating minimal test server...")
        test_path = create_test_server()
        
    # 6. Suggest fixes
    suggest_fixes()
    
    print("\n" + "=" * 60)
    print("NEXT STEPS:")
    print("1. Run this script: python mcp_debug_advanced.py")
    print("2. Share the output for analysis")
    print("3. Try the suggested fixes")
    print("4. Restart Claude completely after each change")
    print("=" * 60)

if __name__ == "__main__":
    main()
