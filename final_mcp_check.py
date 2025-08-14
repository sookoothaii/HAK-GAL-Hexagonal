#!/usr/bin/env python3
"""
Final check for MCP setup with junction
"""

import os
import json
from pathlib import Path

def final_check():
    print("=" * 60)
    print(" FINAL MCP SETUP CHECK")
    print("=" * 60)
    
    # 1. Check junction
    print("\n1. JUNCTION CHECK:")
    junction_path = Path("D:/HAK_GAL")
    if junction_path.exists():
        print(f"✅ Junction exists: D:\\HAK_GAL")
        
        # Check if it points to the right place
        test_file = junction_path / "src_hexagonal" / "infrastructure" / "mcp" / "mcp_server_windows.py"
        if test_file.exists():
            print("✅ Junction points to correct location")
        else:
            print("❌ Junction exists but doesn't point to HAK_GAL_HEXAGONAL")
    else:
        print("❌ Junction D:\\HAK_GAL does NOT exist")
        print("   Run create_junction_fix.bat as Administrator!")
    
    # 2. Check Claude config
    print("\n2. CLAUDE CONFIG CHECK:")
    config_path = Path(os.environ.get('APPDATA', '')) / 'Claude' / 'claude_desktop_config.json'
    
    if config_path.exists():
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        if 'mcpServers' in config and 'hak-gal' in config['mcpServers']:
            server_config = config['mcpServers']['hak-gal']
            command = server_config.get('command', '')
            
            print(f"✅ Claude config exists")
            
            if "HAK_GAL" in command and "MCP Mods" not in command:
                print("✅ Config uses junction path (no spaces)")
                print(f"   Command: {command}")
            else:
                print("⚠️ Config might still use old path with spaces")
                print(f"   Command: {command}")
                print("   Should be: D:\\HAK_GAL\\.venv_hexa\\Scripts\\python.exe")
        else:
            print("❌ No hak-gal server in config")
    else:
        print("❌ Claude config not found")
    
    # 3. Test if server can start
    print("\n3. MCP SERVER TEST:")
    
    python_exe = Path("D:/HAK_GAL/.venv_hexa/Scripts/python.exe")
    mcp_server = Path("D:/HAK_GAL/src_hexagonal/infrastructure/mcp/mcp_server_windows.py")
    
    if python_exe.exists() and mcp_server.exists():
        print("✅ Both Python and MCP server accessible via junction")
        print(f"   Python: {python_exe}")
        print(f"   Server: {mcp_server}")
    else:
        if not python_exe.exists():
            print(f"❌ Python not found at: {python_exe}")
        if not mcp_server.exists():
            print(f"❌ MCP server not found at: {mcp_server}")
    
    # 4. HAK_GAL API check
    print("\n4. HAK_GAL API CHECK:")
    import subprocess
    try:
        result = subprocess.run(
            ["curl", "http://127.0.0.1:5001/health"],
            capture_output=True,
            text=True,
            timeout=2
        )
        if "operational" in result.stdout:
            print("✅ HAK_GAL API is running on port 5001")
        else:
            print("❌ HAK_GAL API not responding correctly")
    except:
        print("⚠️ Could not test API (curl might not be available)")
        print("   Test manually: http://127.0.0.1:5001/health")
    
    print("\n" + "=" * 60)
    print(" SUMMARY")
    print("=" * 60)
    
    if junction_path.exists() and config_path.exists():
        print("\n✅ Setup looks good!")
        print("\nNEXT STEPS:")
        print("1. Make sure HAK_GAL API is running on port 5001")
        print("2. COMPLETELY restart Claude Desktop")
        print("3. Ask Claude: 'What MCP tools do you have available?'")
    else:
        print("\n❌ Setup incomplete!")
        print("\nFIX:")
        print("1. Run create_junction_fix.bat as Administrator")
        print("2. Then run this script again")

if __name__ == "__main__":
    final_check()
