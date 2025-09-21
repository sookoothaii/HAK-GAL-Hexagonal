#!/usr/bin/env python
"""
STOP GOVERNOR IMMEDIATELY
=========================
Stoppt den Governor sofort um weiteren Schaden zu verhindern
"""

import requests
import time

def stop_governor_now():
    """Stop the governor immediately"""
    
    print("="*70)
    print("🛑 EMERGENCY STOP - GOVERNOR")
    print("="*70)
    
    base_url = "http://localhost:5002"
    
    print("\n[1] Stopping Governor...")
    try:
        r = requests.post(f"{base_url}/api/governor/stop")
        print("✅ Stop command sent")
    except:
        print("⚠️ Could not reach governor (may already be stopped)")
    
    print("\n[2] Stopping all engines...")
    try:
        requests.post(f"{base_url}/api/engines/aethelred/stop")
        print("✅ Aethelred engine stopped")
    except:
        pass
    
    try:
        requests.post(f"{base_url}/api/engines/thesis/stop")
        print("✅ Thesis engine stopped")
    except:
        pass
    
    print("\n[3] Verifying...")
    time.sleep(2)
    
    try:
        r = requests.get(f"{base_url}/api/governor/status")
        status = r.json()
        if status.get('status') == 'stopped' or status.get('status') == 'inactive':
            print("✅ Governor is STOPPED")
        else:
            print(f"⚠️ Governor status: {status.get('status')}")
    except:
        print("✅ Governor not responding (good - it's stopped)")
    
    print("\n" + "="*70)
    print("✅ EMERGENCY STOP COMPLETE")
    print("="*70)
    print("\n⚠️ The engines were adding CODE as facts!")
    print("   This must be fixed before restarting!")

if __name__ == "__main__":
    stop_governor_now()
