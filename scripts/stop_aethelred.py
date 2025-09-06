#!/usr/bin/env python
"""
Stop Aethelred Engine - Quick Fix for Timeouts
===============================================
Stoppt nur Aethelred, lässt Thesis weiterlaufen
"""

import subprocess
import os
import signal
import psutil
import time

def stop_aethelred():
    """Stop only the Aethelred engine"""
    
    print("="*70)
    print("STOPPING AETHELRED ENGINE")
    print("="*70)
    
    stopped = False
    
    # Method 1: Try to find and kill the process
    print("\n[1] Looking for Aethelred process...")
    
    try:
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                cmdline = proc.info.get('cmdline')
                if cmdline and any('aethelred' in str(arg).lower() for arg in cmdline):
                    print(f"✅ Found Aethelred process (PID: {proc.info['pid']})")
                    proc.terminate()
                    time.sleep(1)
                    if proc.is_running():
                        proc.kill()
                    print("✅ Aethelred stopped")
                    stopped = True
                    break
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except Exception as e:
        print(f"⚠️ Process search error: {e}")
    
    # Method 2: Windows taskkill
    if not stopped and os.name == 'nt':
        print("\n[2] Using Windows taskkill...")
        try:
            # Kill any Python process running aethelred
            result = subprocess.run(
                'taskkill /F /FI "WINDOWTITLE eq *aethelred*"',
                shell=True, 
                capture_output=True, 
                text=True
            )
            if "SUCCESS" in result.stdout:
                print("✅ Aethelred stopped via taskkill")
                stopped = True
        except:
            pass
    
    # Method 3: Send stop command to API
    print("\n[3] Sending stop command via API...")
    try:
        import requests
        r = requests.post("http://localhost:5002/api/engines/aethelred/stop")
        if r.status_code == 200:
            print("✅ Aethelred stop command sent")
            stopped = True
    except:
        print("⚠️ Could not reach API")
    
    print("\n" + "="*70)
    print("RESULT:")
    print("="*70)
    
    if stopped:
        print("✅ Aethelred engine stopped")
        print("✅ Thesis engine continues running")
        print("✅ Timeouts should stop now")
        print("\n💡 Facts will continue growing with Thesis alone")
        print("   This is more stable and still effective!")
    else:
        print("⚠️ Aethelred might already be stopped")
        print("   Check the terminal windows")
    
    # Check current status
    print("\n[4] Checking current status...")
    try:
        import requests
        r = requests.get("http://localhost:5002/api/governor/status")
        status = r.json()
        print(f"   Governor: {status.get('status', 'unknown')}")
        print(f"   Learning Rate: {status.get('learning_rate', 0)} facts/min")
        
        r = requests.get("http://localhost:5002/api/facts/count")
        count = r.json()
        print(f"   Current Facts: {count.get('count', 0):,}")
        
    except:
        pass

if __name__ == "__main__":
    stop_aethelred()
    
    print("\n📊 To see facts still growing:")
    print("   http://127.0.0.1:8088/dashboard")
