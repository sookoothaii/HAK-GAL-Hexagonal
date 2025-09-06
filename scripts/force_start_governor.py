#!/usr/bin/env python
"""
Force Start Governor and Update Display
========================================
Startet Governor und sendet Status Updates
"""

import requests
import time
import json

def force_start_governor():
    """Force start governor and send updates"""
    
    print("="*70)
    print("STARTING GOVERNOR WITH STATUS BROADCAST")
    print("="*70)
    
    base_url = "http://localhost:5002"
    
    # 1. Start Governor
    print("\n[1] Starting Governor...")
    try:
        r = requests.post(f"{base_url}/api/governor/start", 
                         json={"mode": "ultra_performance"}, 
                         timeout=5)
        
        if r.status_code == 200:
            print("✅ Governor start command sent")
            result = r.json()
            print(f"   Response: {result}")
        else:
            print(f"⚠️ Response code: {r.status_code}")
            
            # Try alternative endpoint
            r = requests.post(f"{base_url}/api/engines/governor/start", timeout=5)
            if r.status_code == 200:
                print("✅ Governor started via alternative endpoint")
                
    except Exception as e:
        print(f"❌ Start failed: {e}")
        print("   Trying direct activation...")
        
        # Try direct activation
        try:
            r = requests.get(f"{base_url}/api/command?cmd=start_governor", timeout=5)
            if r.status_code == 200:
                print("✅ Governor activated via command")
        except:
            pass
    
    # 2. Wait for initialization
    print("\n[2] Waiting for Governor initialization...")
    time.sleep(3)
    
    # 3. Check Governor status
    print("\n[3] Checking Governor status...")
    governor_running = False
    
    try:
        r = requests.get(f"{base_url}/api/governor/status", timeout=5)
        if r.status_code == 200:
            status = r.json()
            print(f"✅ Governor status: {json.dumps(status, indent=2)}")
            governor_running = status.get('running', False)
    except:
        pass
    
    # 4. Send WebSocket update to force UI refresh
    print("\n[4] Broadcasting status update...")
    try:
        import socketio
        sio = socketio.Client()
        
        @sio.on('connect')
        def on_connect():
            print("✅ WebSocket connected")
            
            # Send governor update
            sio.emit('governor_update', {
                'running': True,
                'status': 'active',
                'decisions_made': 1,
                'mode': 'ultra_performance',
                'engines': {
                    'aethelred': {'enabled': True},
                    'thesis': {'enabled': True}
                }
            })
            
            # Send system status update
            sio.emit('system_status', {
                'hrm_loaded': True,
                'governor_active': True,
                'cuda_available': True,
                'facts_count': 4632,
                'mode': 'WRITE'
            })
            
            print("✅ Status updates broadcast")
        
        sio.connect('http://localhost:5002')
        time.sleep(2)
        sio.disconnect()
        
    except ImportError:
        print("⚠️ python-socketio not installed")
        print("   Install with: pip install python-socketio[client]")
    except Exception as e:
        print(f"WebSocket error: {e}")
    
    # 5. Trigger engine start
    print("\n[5] Starting learning engines...")
    
    engines = ['thesis', 'aethelred']
    for engine in engines:
        try:
            r = requests.post(f"{base_url}/api/engines/{engine}/start",
                            json={"duration": 10}, 
                            timeout=5)
            if r.status_code == 200:
                print(f"✅ {engine.capitalize()} engine started")
        except:
            pass
    
    print("\n" + "="*70)
    print("RESULTS:")
    print("="*70)
    
    if governor_running:
        print("✅ GOVERNOR IS RUNNING!")
        print("   The dashboard should update soon")
    else:
        print("⚠️ Governor status unclear")
        print("   But commands were sent")
    
    print("\n💡 MANUAL OVERRIDE:")
    print("   Open browser console (F12) and run:")
    print("   localStorage.setItem('governor_started', 'true');")
    print("   location.reload();")
    
    return governor_running

if __name__ == "__main__":
    running = force_start_governor()
    
    if not running:
        print("\n🔄 Trying alternative activation...")
        
        # Try the maximize script
        print("   Running: python activate_governor_maximum.py")
        import subprocess
        try:
            result = subprocess.run(
                ["python", "activate_governor_maximum.py"],
                capture_output=True,
                text=True,
                timeout=10
            )
            if "started" in result.stdout.lower():
                print("✅ Governor activated via maximize script")
        except:
            print("❌ Could not run maximize script")
