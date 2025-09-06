#!/usr/bin/env python3
"""
Check MCP Server status and recent logs
"""
import os
import json
import subprocess
from pathlib import Path
from datetime import datetime

# Check if server process is running
def check_process():
    try:
        result = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq python.exe'], 
                              capture_output=True, text=True)
        return "python.exe" in result.stdout
    except:
        return False

# Read last N lines of log
def tail_log(log_path, lines=50):
    if not os.path.exists(log_path):
        return "Log file not found"
    
    try:
        with open(log_path, 'r', encoding='utf-8', errors='replace') as f:
            all_lines = f.readlines()
            return ''.join(all_lines[-lines:])
    except Exception as e:
        return f"Error reading log: {e}"

# Main check
print("=== MCP Server Status Check ===")
print(f"Timestamp: {datetime.now()}")
print()

# Check process
print("1. Process Status:")
if check_process():
    print("   Python processes found (server may be running)")
else:
    print("   No Python processes found")
print()

# Check recent logs
print("2. Recent Log Entries:")
log_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server.log"
recent_logs = tail_log(log_path, 30)
print(recent_logs)
print()

# Check JSONL logs  
print("3. Recent JSONL Entries:")
jsonl_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\mcp_server.jsonl"
recent_jsonl = tail_log(jsonl_path, 10)
print(recent_jsonl)
print()

# Check port 8088
print("4. Port 8088 Status:")
try:
    result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
    if ':8088' in result.stdout:
        print("   Port 8088 is in use")
        for line in result.stdout.split('\n'):
            if ':8088' in line:
                print(f"   {line.strip()}")
    else:
        print("   Port 8088 is NOT in use")
except Exception as e:
    print(f"   Error checking port: {e}")
