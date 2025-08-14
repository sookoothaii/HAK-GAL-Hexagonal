#!/usr/bin/env python3
"""
Analyze MCP Server Logs to understand current state
"""

import os
from pathlib import Path
from datetime import datetime

def analyze_log(filepath, lines_to_read=50):
    """Analyze last N lines of a log file"""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            all_lines = f.readlines()
            total_lines = len(all_lines)
            last_lines = all_lines[-lines_to_read:] if len(all_lines) > lines_to_read else all_lines
            
            # Get file size
            file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
            
            return {
                'exists': True,
                'size_mb': round(file_size, 2),
                'total_lines': total_lines,
                'last_lines': last_lines,
                'last_modified': datetime.fromtimestamp(os.path.getmtime(filepath))
            }
    except Exception as e:
        return {
            'exists': False,
            'error': str(e)
        }

def main():
    """Analyze all MCP logs"""
    
    print("=" * 70)
    print("MCP SERVER LOGS ANALYSIS")
    print("=" * 70)
    
    log_files = [
        "mcp-server-Filesystem.log",
        "mcp-server-Socket.log", 
        "mcp.log",
        "mcp_server.log",
        "mcp_server_v2.log"
    ]
    
    base_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL")
    
    for log_file in log_files:
        log_path = base_path / log_file
        print(f"\n{'='*60}")
        print(f"📄 {log_file}")
        print(f"{'='*60}")
        
        result = analyze_log(log_path)
        
        if result['exists']:
            print(f"✅ File exists")
            print(f"📊 Size: {result['size_mb']} MB")
            print(f"📝 Total lines: {result['total_lines']:,}")
            print(f"🕐 Last modified: {result['last_modified']}")
            
            print(f"\n🔍 Last 10 lines:")
            print("-" * 40)
            for line in result['last_lines'][-10:]:
                line = line.strip()
                if line:
                    # Truncate long lines
                    if len(line) > 120:
                        line = line[:117] + "..."
                    print(f"  {line}")
            
            # Analyze content patterns
            print(f"\n📊 Pattern Analysis (last 50 lines):")
            patterns = {
                'errors': 0,
                'warnings': 0,
                'success': 0,
                'initialize': 0,
                'tool_calls': 0,
                'connected': 0
            }
            
            for line in result['last_lines']:
                line_lower = line.lower()
                if 'error' in line_lower:
                    patterns['errors'] += 1
                if 'warning' in line_lower or 'warn' in line_lower:
                    patterns['warnings'] += 1
                if 'success' in line_lower or 'initialized' in line_lower:
                    patterns['success'] += 1
                if 'initialize' in line_lower:
                    patterns['initialize'] += 1
                if 'tool' in line_lower or 'call' in line_lower:
                    patterns['tool_calls'] += 1
                if 'connected' in line_lower or 'connection' in line_lower:
                    patterns['connected'] += 1
                    
            for pattern, count in patterns.items():
                if count > 0:
                    print(f"  {pattern}: {count} occurrences")
                    
        else:
            print(f"❌ File not found or error: {result.get('error', 'Unknown')}")
    
    # Check for running Python processes
    print(f"\n{'='*60}")
    print("🔍 CHECKING FOR MCP PROCESSES")
    print(f"{'='*60}")
    
    import subprocess
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        lines = result.stdout.split('\n')
        python_procs = [line for line in lines if 'python.exe' in line.lower()]
        
        if python_procs:
            print(f"✅ Found {len(python_procs)} Python processes:")
            for proc in python_procs[:5]:  # Show max 5
                print(f"  {proc.strip()}")
        else:
            print("❌ No Python processes found")
    except:
        print("⚠️ Could not check processes")
    
    # Summary and recommendations
    print(f"\n{'='*70}")
    print("📋 SUMMARY & RECOMMENDATIONS")
    print(f"{'='*70}")
    
    if (base_path / "mcp-server-Filesystem.log").exists():
        print("\n✅ Filesystem MCP Server is/was active")
        print("   This server provides file system access to Claude")
        
    if (base_path / "mcp-server-Socket.log").exists():
        print("\n✅ Socket MCP Server is/was active")
        print("   This server provides Socket/Network capabilities")
        
    if (base_path / "mcp.log").exists():
        print("\n✅ General MCP log found")
        print("   Check for initialization and tool registration")
    
    print("\n🎯 NEXT STEPS:")
    print("1. If servers are running, Claude should have MCP tools")
    print("2. Check in Claude: 'What MCP tools do you have?'")
    print("3. If no tools, restart Claude completely")
    print("4. Check Claude DevTools Console for MCP messages")
    
if __name__ == "__main__":
    main()
