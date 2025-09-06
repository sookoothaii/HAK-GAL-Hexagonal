#!/usr/bin/env python
"""
ULTIMATIVE LÖSUNG - VOLLSTÄNDIGES DEBUGGING UND FIX
====================================================
"""
import os
import socket
import subprocess
import time
import sys

def ultimate_fix():
    print("="*70)
    print("ULTIMATIVE LÖSUNG - VOLLSTÄNDIGES SYSTEM AUF 8088")
    print("="*70)
    
    # 1. Kill everything
    print("\n[1] Terminating all conflicting processes...")
    os.system("taskkill /F /IM caddy.exe 2>nul")
    os.system("netstat -ano | findstr :8088")
    time.sleep(2)
    
    # 2. Create the ULTIMATE Caddyfile
    print("\n[2] Creating ULTIMATE Caddyfile...")
    
    caddyfile = """
:8088 {
    reverse_proxy /* localhost:5173
}
"""
    
    with open("Caddyfile", "w") as f:
        f.write(caddyfile)
    
    print("✅ Caddyfile created - SIMPLEST POSSIBLE CONFIG")
    
    # 3. Start with full debug
    print("\n[3] Starting Caddy with FULL DEBUG...")
    print("-"*70)
    
    cmd = ["caddy", "run", "--config", "Caddyfile", "--adapter", "caddyfile"]
    
    print(f"Executing: {' '.join(cmd)}")
    print("-"*70)
    
    # This will run Caddy in the current console
    subprocess.run(cmd)

if __name__ == "__main__":
    print("This will create the SIMPLEST POSSIBLE proxy:")
    print("  8088 -> 5173 (Vite)")
    print("\nThe frontend at :5173 already talks to backend at :5002")
    print("\nPress Enter to continue...")
    input()
    
    ultimate_fix()
