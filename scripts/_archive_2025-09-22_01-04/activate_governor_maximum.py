#!/usr/bin/env python
"""
Aktiviere Governor für maximales autonomes Lernen
==================================================
Ziel: 45+ facts/min statt 0.01 facts/min
"""

import requests
import json
import time

def activate_governor_maximum():
    """Aktiviere Governor mit maximaler Performance"""
    
    print("="*70)
    print("GOVERNOR ACTIVATION - MAXIMUM LEARNING RATE")
    print("="*70)
    
    base_url = "http://localhost:5002"
    
    # 1. Check current status
    print("\n[1] Checking current Governor status...")
    try:
        r = requests.get(f"{base_url}/api/governor/status")
        if r.status_code == 200:
            status = r.json()
            print(f"✅ Current status: {status.get('status', 'unknown')}")
            print(f"   Learning rate: {status.get('learning_rate', 0)} facts/min")
            
            if status.get('status') == 'running':
                print("⚠️ Governor already running, stopping first...")
                requests.post(f"{base_url}/api/governor/stop")
                time.sleep(2)
        else:
            print(f"⚠️ Status endpoint returned: {r.status_code}")
    except Exception as e:
        print(f"⚠️ Could not get status: {e}")
    
    # 2. Start Governor with maximum configuration
    print("\n[2] Starting Governor with MAXIMUM settings...")
    
    config = {
        "mode": "ultra_performance",
        "target_facts_per_minute": 45,
        "enable_aethelred": True,
        "enable_thesis": True,
        "aethelred_interval": 10,  # Every 10 seconds
        "thesis_interval": 15,      # Every 15 seconds
        "batch_size": 5,
        "exploration_weight": 0.7,
        "exploitation_weight": 0.3,
        "enable_neural_feedback": True,
        "max_parallel_engines": 2
    }
    
    try:
        r = requests.post(f"{base_url}/api/governor/start", json=config)
        
        if r.status_code == 200:
            print("✅ Governor started successfully!")
            result = r.json()
            print(f"   Response: {json.dumps(result, indent=2)}")
        else:
            print(f"⚠️ Start returned status: {r.status_code}")
            print(f"   Response: {r.text}")
    except Exception as e:
        print(f"❌ Error starting governor: {e}")
    
    # 3. Wait and verify
    print("\n[3] Waiting for Governor to initialize...")
    time.sleep(3)
    
    # 4. Check final status
    print("\n[4] Verifying Governor activation...")
    try:
        r = requests.get(f"{base_url}/api/governor/status")
        if r.status_code == 200:
            status = r.json()
            
            if status.get('status') == 'running':
                print("✅ GOVERNOR ACTIVE AND RUNNING!")
                print(f"   Status: {status.get('status')}")
                print(f"   Learning Rate: {status.get('learning_rate', 0)} facts/min")
                print(f"   Active Engines: {status.get('active_engines', [])}")
                print(f"   Mode: {status.get('mode', 'unknown')}")
                
                print("\n" + "="*70)
                print("SUCCESS! Governor is now learning autonomously!")
                print("Target: 45 facts/minute")
                print("Monitor progress at: http://127.0.0.1:8088/dashboard")
                print("="*70)
            else:
                print(f"⚠️ Governor status: {status.get('status')}")
                print("   May need manual intervention")
        else:
            print(f"❌ Could not verify status: {r.status_code}")
    except Exception as e:
        print(f"❌ Error checking status: {e}")
    
    # 5. Test engines
    print("\n[5] Testing Engine endpoints...")
    
    engines = [
        ("/api/engines/aethelred/status", "Aethelred Engine"),
        ("/api/engines/thesis/status", "Thesis Engine")
    ]
    
    for endpoint, name in engines:
        try:
            r = requests.get(f"{base_url}{endpoint}")
            if r.status_code == 200:
                print(f"✅ {name}: Active")
            else:
                print(f"⚠️ {name}: Status {r.status_code}")
        except:
            print(f"❌ {name}: Not responding")

if __name__ == "__main__":
    activate_governor_maximum()
    
    print("\n📌 WICHTIG:")
    print("1. Dashboard sollte jetzt aktualisierte Metriken zeigen")
    print("2. Learning Rate sollte auf 45 facts/min steigen")
    print("3. Facts sollten automatisch wachsen (Ziel: 5000)")
    print("\nÖffnen Sie: http://127.0.0.1:8088/dashboard")
