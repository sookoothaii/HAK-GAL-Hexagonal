#!/usr/bin/env python3
"""
Generate exact MCP configuration for Claude Desktop
Shows exactly what to enter in the settings
"""

import sys
import os
from pathlib import Path
import shutil

def get_python_executable():
    """Find the correct Python executable"""
    
    # Option 1: Virtual environment Python
    venv_python_hexa = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv_hexa/Scripts/python.exe")
    venv_python = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.venv/Scripts/python.exe")
    
    if venv_python_hexa.exists():
        return str(venv_python_hexa).replace('/', '\\')
    elif venv_python.exists():
        return str(venv_python).replace('/', '\\')
    else:
        # Option 2: System Python
        python_path = shutil.which("python")
        if python_path:
            return python_path
        else:
            return sys.executable

def main():
    """Generate configuration instructions"""
    
    print("=" * 70)
    print(" CLAUDE DESKTOP MCP SERVER CONFIGURATION")
    print("=" * 70)
    
    python_exe = get_python_executable()
    mcp_server_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\src_hexagonal\infrastructure\mcp\mcp_server.py"
    
    print("\n📋 COPY THESE VALUES INTO CLAUDE DESKTOP SETTINGS:\n")
    
    print("1. Open Claude Desktop")
    print("2. Go to Settings (⚙️)")
    print("3. Find 'Developer' or 'MCP Servers' section")
    print("4. Click 'Add MCP Server' or 'Edit Configuration'")
    print("5. Enter these values:\n")
    
    print("-" * 70)
    print("SERVER NAME:")
    print("  hak-gal")
    print()
    
    print("COMMAND:")
    print(f"  {python_exe}")
    print()
    
    print("ARGUMENTS (as single line):")
    print(f"  {mcp_server_path}")
    print()
    
    print("ENVIRONMENT VARIABLES (optional):")
    print("  PYTHONPATH=D:\\MCP Mods\\HAK_GAL_HEXAGONAL")
    print("-" * 70)
    
    print("\n🔍 DETECTED SYSTEM INFO:\n")
    print(f"Python executable: {python_exe}")
    print(f"Python version: {sys.version.split()[0]}")
    print(f"MCP server exists: {Path(mcp_server_path).exists()}")
    
    # Check if httpx is installed
    try:
        import httpx
        print(f"httpx installed: ✅ (version {httpx.__version__})")
    except ImportError:
        print("httpx installed: ❌ (run: pip install httpx)")
    
    # Generate clipboard-ready version
    print("\n" + "=" * 70)
    print(" ALTERNATIVE: FULL COMMAND FOR TESTING")
    print("=" * 70)
    
    print("\nYou can test the MCP server with this command:")
    print(f'"{python_exe}" "{mcp_server_path}"')
    
    print("\n" + "=" * 70)
    print(" TROUBLESHOOTING")
    print("=" * 70)
    
    print("\nIf Claude can't find the server:")
    print("1. Make sure HAK_GAL API is running on port 5001")
    print("2. Check that Python path is correct")
    print("3. Restart Claude Desktop completely")
    print("4. Check Claude logs at: %APPDATA%\\Claude\\logs\\")
    
    print("\n✅ Configuration ready to copy!")
    print("After adding the server, restart Claude Desktop.\n")

if __name__ == "__main__":
    main()
