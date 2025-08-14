#!/usr/bin/env python3
"""
Extract last lines from large MCP log files
"""

import sys
from pathlib import Path

def get_last_lines(filepath, num_lines=20):
    """Read last N lines from a large file efficiently"""
    try:
        with open(filepath, 'rb') as f:
            # Seek to end
            f.seek(0, 2)
            file_size = f.tell()
            
            # Read last 5KB
            chunk_size = min(5120, file_size)
            f.seek(-chunk_size, 2)
            
            # Decode and get lines
            chunk = f.read().decode('utf-8', errors='ignore')
            lines = chunk.split('\n')
            
            # Return last N lines
            return lines[-num_lines:] if len(lines) > num_lines else lines
    except Exception as e:
        return [f"Error reading file: {e}"]

# Process each log
logs = {
    "mcp-server-Filesystem.log": "Filesystem MCP Server",
    "mcp-server-Socket.log": "Socket MCP Server",
    "mcp.log": "Main MCP Log"
}

base_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL")

for filename, description in logs.items():
    filepath = base_path / filename
    print(f"\n{'='*60}")
    print(f"📄 {description}: {filename}")
    print(f"{'='*60}")
    
    if filepath.exists():
        # Get file size
        size_mb = filepath.stat().st_size / (1024 * 1024)
        print(f"Size: {size_mb:.2f} MB")
        print("\nLast 15 lines:")
        print("-" * 40)
        
        lines = get_last_lines(filepath, 15)
        for line in lines:
            line = line.strip()
            if line:
                # Truncate very long lines
                if len(line) > 150:
                    line = line[:147] + "..."
                print(line)
    else:
        print(f"❌ File not found")

print("\n" + "="*60)
print("ANALYSIS COMPLETE")
print("="*60)
