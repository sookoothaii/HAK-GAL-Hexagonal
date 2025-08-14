#!/usr/bin/env python3
"""
Quick Verification Test nach Governor Fix
==========================================
Testet ob alle Fixes erfolgreich waren
"""

import requests
import time
from datetime import datetime

def test_fix():
    """Verifiziert die Fixes"""
    
    print("="*60)
    print("🔍 VERIFYING HEXAGONAL FIXES")
    print("="*60)
    
    base_url = "http://127.0.0.1:5001"
    results = {}
    
    # Test 1: API erreichbar
    print("\n[1/4] Testing API availability...")
    try:
        r = requests.get(f"{base_url}/health", timeout=5)
        health = r.json()
        results['api'] = r.status_code == 200
        print(f"  ✅ API running on port 5001")
        print(f"  - WebSocket: {health.get('websocket')}")
        print(f"  - Governor: {health.get('governor')}")
        print(f"  - Repository: {health.get('repository')}")
    except Exception as e:
        results['api'] = False
        print(f"  ❌ API not reachable: {e}")
        return results
    
    # Test 2: Governor Status (zeigt ob Import Fix funktioniert)
    print("\n[2/4] Testing Governor (Import Fix)...")
    try:
        r = requests.get(f"{base_url}/api/governor/status", timeout=5)
        if r.status_code == 200:
            gov_status = r.json()
            results['governor'] = True
            print(f"  ✅ Governor working!")
            print(f"  - Mode: {gov_status.get('mode')}")
            print(f"  - Running: {gov_status.get('running')}")
            print(f"  - Initialized: {gov_status.get('initialized')}")
        else:
            results['governor'] = False
            print(f"  ⚠️ Governor endpoint exists but returned {r.status_code}")
    except Exception as e:
        results['governor'] = False
        print(f"  ❌ Governor not available: {e}")
    
    # Test 3: Facts Count (sollte 3316 zeigen)
    print("\n[3/4] Testing Facts Repository...")
    try:
        r = requests.get(f"{base_url}/api/status", timeout=5)
        status = r.json()
        fact_count = status.get('fact_count', 0)
        results['facts'] = fact_count > 0
        print(f"  ✅ Facts loaded: {fact_count}")
        
        if fact_count != 3316:
            print(f"  ⚠️ Expected 3316 facts, got {fact_count}")
    except Exception as e:
        results['facts'] = False
        print(f"  ❌ Could not get facts: {e}")
    
    # Test 4: HRM Reasoning (CUDA Performance)
    print("\n[4/4] Testing HRM Reasoning (CUDA)...")
    try:
        start = time.time()
        r = requests.post(f"{base_url}/api/reason", 
                         json={"query": "IsTypeOf(Water, Substance)"},
                         timeout=5)
        duration_ms = (time.time() - start) * 1000
        
        if r.status_code == 200:
            result = r.json()
            results['reasoning'] = True
            print(f"  ✅ Reasoning working!")
            print(f"  - Confidence: {result.get('confidence', 0):.4f}")
            print(f"  - Response Time: {duration_ms:.2f}ms")
            print(f"  - Device: {result.get('device', 'unknown')}")
        else:
            results['reasoning'] = False
            print(f"  ❌ Reasoning returned {r.status_code}")
    except Exception as e:
        results['reasoning'] = False
        print(f"  ❌ Reasoning failed: {e}")
    
    # Summary
    print("\n" + "="*60)
    print("📊 FIX VERIFICATION SUMMARY")
    print("="*60)
    
    all_ok = all(results.values())
    
    for test, passed in results.items():
        status = "✅" if passed else "❌"
        print(f"{status} {test.upper()}: {'PASSED' if passed else 'FAILED'}")
    
    if all_ok:
        print("\n🎉 ALL FIXES VERIFIED SUCCESSFULLY!")
        print("The Hexagonal API is ready for production use.")
    else:
        failed = [k for k, v in results.items() if not v]
        print(f"\n⚠️ Some tests failed: {', '.join(failed)}")
        print("Please check the logs and restart the API.")
    
    return results

if __name__ == "__main__":
    test_fix()
