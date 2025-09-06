#!/usr/bin/env python3
"""
Import System Monitoring Facts to HAK-GAL Knowledge Base
========================================================
Run this after Kill-Switch is disabled
"""

import json
import requests
from pathlib import Path

# Configuration
API_URL = "http://localhost:5001/api/facts"
AUTH_TOKEN = "515f57956e7bd15ddc3817573598f190"
FACTS_FILE = Path("monitoring_facts.json")

def import_facts():
    """Import monitoring facts to KB"""
    
    print("=" * 60)
    print("HAK-GAL MONITORING FACTS IMPORT")
    print("=" * 60)
    
    # Load facts
    with open(FACTS_FILE, 'r') as f:
        data = json.load(f)
    
    facts = data['monitoring_facts']
    total = len(facts)
    success = 0
    failed = 0
    
    print(f"\n📦 Loading {total} facts from {FACTS_FILE}")
    print("-" * 60)
    
    # Import each fact
    for i, fact_data in enumerate(facts, 1):
        statement = fact_data['statement']
        metadata = fact_data.get('metadata', {})
        
        print(f"\n[{i}/{total}] Importing: {statement}")
        
        # Prepare payload
        payload = {
            'statement': statement,
            'context': metadata
        }
        
        # Add auth token if provided
        if AUTH_TOKEN:
            payload['auth_token'] = AUTH_TOKEN
        
        try:
            # Send to API
            response = requests.post(API_URL, json=payload)
            
            if response.status_code in [200, 201]:
                print(f"  ✅ Success")
                success += 1
            elif response.status_code == 409:
                print(f"  ⚠️ Already exists")
                success += 1
            elif response.status_code == 503:
                print(f"  ❌ Kill-Switch active!")
                print("  Please disable Kill-Switch first:")
                print("  POST /api/safety/kill-switch/deactivate")
                return False
            else:
                print(f"  ❌ Failed: {response.status_code}")
                print(f"     {response.text}")
                failed += 1
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
            failed += 1
    
    print("\n" + "=" * 60)
    print("IMPORT COMPLETE")
    print(f"✅ Success: {success}/{total}")
    print(f"❌ Failed: {failed}/{total}")
    print("=" * 60)
    
    return failed == 0

def check_kill_switch():
    """Check if Kill-Switch is active"""
    try:
        response = requests.get("http://localhost:5001/api/safety/kill-switch")
        data = response.json()
        
        if data.get('mode') == 'safe':
            print("⚠️ Kill-Switch is in SAFE mode!")
            print("\nTo deactivate, run:")
            print("curl -X POST http://localhost:5001/api/safety/kill-switch/deactivate")
            return False
        
        print("✅ Kill-Switch is not active")
        return True
        
    except Exception as e:
        print(f"❌ Could not check Kill-Switch: {e}")
        return False

if __name__ == "__main__":
    import sys
    
    print("\n🔍 Checking Kill-Switch status...")
    if not check_kill_switch():
        print("\n❌ Cannot proceed with Kill-Switch active")
        sys.exit(1)
    
    print("\n📝 Starting import...")
    if import_facts():
        print("\n✅ All facts imported successfully!")
        sys.exit(0)
    else:
        print("\n❌ Import failed or incomplete")
        sys.exit(1)
