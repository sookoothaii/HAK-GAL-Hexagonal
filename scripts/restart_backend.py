#!/usr/bin/env python3
"""
Restart the backend server with optimized governor
"""
import subprocess
import time
import sys
import os
from pathlib import Path

print("="*60)
print("BACKEND RESTART WITH OPTIMIZED GOVERNOR")
print("="*60)

project_dir = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

# 1. Stop backend
print("\n1. Stopping backend server...")
try:
    import requests
    requests.post("http://127.0.0.1:5002/api/shutdown", timeout=2)
    print("   ✅ Shutdown request sent")
except:
    print("   ⚠️ Server may already be stopped")

# Kill any remaining Python processes on port 5002
try:
    subprocess.run(['netstat', '-ano', '|', 'findstr', ':5002'], 
                   capture_output=True, shell=True)
    subprocess.run(['taskkill', '/F', '/IM', 'python.exe'], 
                   capture_output=True)
    print("   ✅ Cleared port 5002")
except:
    pass

time.sleep(2)

# 2. Start backend with new code
print("\n2. Starting backend with optimized governor...")

backend_script = project_dir / "src_hexagonal" / "app.py"
if not backend_script.exists():
    # Try alternative location
    backend_script = project_dir / "app.py"

if backend_script.exists():
    print(f"   Starting: {backend_script}")
    
    # Set environment
    os.environ['HAKGAL_AUTH_TOKEN'] = '515f57956e7bd15ddc3817573598f190'
    os.environ['PYTHONPATH'] = str(project_dir)
    
    # Start in new window
    subprocess.Popen([
        sys.executable,
        str(backend_script)
    ], 
    cwd=str(project_dir),
    creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    
    print("   ✅ Backend starting in new window...")
    
    # Wait for startup
    print("\n3. Waiting for backend to be ready...")
    time.sleep(3)
    
    # Test if running
    try:
        import requests
        response = requests.get("http://127.0.0.1:5002/api/stats", timeout=5)
        if response.status_code == 200:
            print("   ✅ Backend is running!")
            
            # Check if optimized
            response = requests.get("http://127.0.0.1:5002/api/llm-governor/status", timeout=2)
            if response.status_code == 200:
                data = response.json()
                if data.get('optimized'):
                    print("   ✅ Optimized governor loaded!")
                    print("\n   Features active:")
                    for feature in data.get('features', []):
                        print(f"     • {feature}")
        else:
            print("   ⚠️ Backend not responding properly")
    except Exception as e:
        print(f"   ⚠️ Backend not ready yet: {e}")
        print("   Try refreshing in a few seconds")

else:
    print(f"   ❌ Backend script not found at {backend_script}")
    print("\n   Manual start required:")
    print(f"   cd {project_dir}")
    print("   python src_hexagonal\\app.py")

print("\n" + "="*60)
print("NEXT STEPS:")
print("="*60)
print("\n1. Wait for backend to fully start (check new window)")
print("2. Open http://localhost:8088/governor")
print("3. Click 'Start Governor' button")
print("4. Monitor with: python scripts\\monitor_generation.py")
print("\nThe optimized generator will now:")
print("  • Prevent duplicates")
print("  • Limit HasProperty to 20%")
print("  • Use balanced predicates")
print("="*60)
