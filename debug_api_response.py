#!/usr/bin/env python3
"""
Debug API Response - Exact Key Analysis
Nach HAK/GAL Verfassung Artikel 3: Externe Verifikation
"""

import requests
import json

def debug_api_responses():
    """Debug exact API responses to find key mismatch"""
    
    print("=" * 60)
    print("🔍 DEBUG API RESPONSES - Key Analysis")
    print("=" * 60)
    
    # Test Hexagonal API Status
    print("\n1. HEXAGONAL API /api/status:")
    try:
        resp = requests.get("http://127.0.0.1:5001/api/status", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Raw Response: {json.dumps(data, indent=2)}")
            print(f"   Keys in response: {list(data.keys())}")
            
            # Check different possible keys
            possible_keys = ['fact_count', 'facts_count', 'factCount', 'total_facts', 'count']
            for key in possible_keys:
                if key in data:
                    print(f"   ✅ Found key '{key}': {data[key]}")
        else:
            print(f"   Status Code: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Facts Endpoint
    print("\n2. HEXAGONAL API /api/facts:")
    try:
        resp = requests.get("http://127.0.0.1:5001/api/facts?limit=1", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Keys in response: {list(data.keys())}")
            if 'total' in data:
                print(f"   ✅ Total from /api/facts: {data['total']}")
            if 'count' in data:
                print(f"   Count (retrieved): {data['count']}")
        else:
            print(f"   Status Code: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test Original API for comparison
    print("\n3. ORIGINAL API /api/knowledge-base/status:")
    try:
        resp = requests.get("http://127.0.0.1:5000/api/knowledge-base/status", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   Raw Response: {json.dumps(data, indent=2)}")
            print(f"   Keys in response: {list(data.keys())}")
        else:
            print(f"   Status Code: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Direct test the count method
    print("\n4. TESTING COUNT METHOD DIRECTLY:")
    print("   Check if API is actually calling repository.count()...")
    
    # Make multiple requests to see if consistent
    print("\n5. CONSISTENCY CHECK (3 requests):")
    for i in range(3):
        try:
            resp = requests.get("http://127.0.0.1:5001/api/facts", timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                print(f"   Request {i+1}: total={data.get('total', 'N/A')}")
        except:
            print(f"   Request {i+1}: Failed")

if __name__ == "__main__":
    debug_api_responses()
