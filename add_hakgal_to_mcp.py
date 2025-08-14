#!/usr/bin/env python3
"""
Add HAK_GAL MCP Server to existing Claude configuration
WITHOUT breaking existing MCP servers
"""

import json
import shutil
from pathlib import Path
from datetime import datetime
import sys
import os

def main():
    print("=" * 60)
    print("HAK_GAL MCP Server - Config Updater")
    print("=" * 60)
    
    # Find config path
    appdata = os.environ.get('APPDATA', '')
    if not appdata:
        print("❌ ERROR: APPDATA environment variable not found")
        sys.exit(1)
        
    config_path = Path(appdata) / "Claude" / "claude_desktop_config.json"
    
    print(f"\n📁 Config path: {config_path}")
    
    # Check if config exists
    if not config_path.exists():
        print("❌ Config file not found!")
        print("\nCreating new config with HAK_GAL server...")
        
        new_config = {
            "mcpServers": {
                "hak-gal": {
                    "command": ["python"],
                    "args": ["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py"]
                }
            }
        }
        
        # Create directory if needed
        config_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_path, 'w') as f:
            json.dump(new_config, f, indent=2)
            
        print("✅ Created new config with HAK_GAL server")
        sys.exit(0)
    
    # Read existing config
    print("📖 Reading existing config...")
    
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ ERROR: Invalid JSON in config: {e}")
        sys.exit(1)
    
    # Backup existing config
    backup_name = f"claude_desktop_config.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    backup_path = config_path.parent / backup_name
    
    print(f"💾 Creating backup: {backup_name}")
    shutil.copy2(config_path, backup_path)
    print("✅ Backup created")
    
    # Check current servers
    if 'mcpServers' not in config:
        config['mcpServers'] = {}
        
    servers = config['mcpServers']
    
    print(f"\n📋 Current MCP servers: {len(servers)}")
    for name in servers.keys():
        print(f"  • {name}")
    
    # Check if HAK_GAL already exists
    if 'hak-gal' in servers:
        print("\n⚠️  HAK_GAL server already in config!")
        print("Current configuration:")
        print(json.dumps(servers['hak-gal'], indent=2))
        
        response = input("\nOverwrite? (y/n): ").lower()
        if response != 'y':
            print("❌ Aborted")
            sys.exit(0)
    
    # Add HAK_GAL server
    print("\n➕ Adding HAK_GAL MCP server...")
    
    servers['hak-gal'] = {
        "command": ["python"],
        "args": ["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py"]
    }
    
    # Alternative with full path to Python (more robust)
    # Uncomment if needed:
    # servers['hak-gal'] = {
    #     "command": ["C:\\Python310\\python.exe"],
    #     "args": ["D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hak_gal_mcp_v2.py"]
    # }
    
    # Save updated config
    print("💾 Saving updated config...")
    
    with open(config_path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print("✅ Config updated successfully!")
    
    # Show final config
    print("\n📋 Final MCP servers configuration:")
    for name, server_config in servers.items():
        cmd = server_config.get('command', [])
        if isinstance(cmd, list):
            cmd_str = ' '.join(cmd)
        else:
            cmd_str = str(cmd)
        print(f"  • {name}: {cmd_str}")
    
    # Instructions
    print("\n" + "=" * 60)
    print("✅ SUCCESS! HAK_GAL MCP Server added to config")
    print("=" * 60)
    
    print("\n🚀 NEXT STEPS:")
    print("1. Close Claude completely (check System Tray)")
    print("2. Verify no Claude.exe in Task Manager")
    print("3. Start Claude Desktop")
    print("4. Wait for full initialization")
    print("5. Test: 'What MCP tools do you have?'")
    print("\nExpected new tools:")
    print("  • search_knowledge - Search HAK_GAL knowledge base")
    print("  • get_system_status - Get HAK_GAL system status")
    
    print(f"\n📁 Backup saved as: {backup_name}")
    print("   (in case you need to restore)")
    
if __name__ == "__main__":
    main()
