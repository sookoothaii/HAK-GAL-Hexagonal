#!/usr/bin/env python3
"""
Find the correct API format for adding facts
=============================================
"""

import requests
import json

API_URL = "http://127.0.0.1:5001"

print("\n" + "🔬"*40)
print("TESTING DIFFERENT API FORMATS")
print("🔬"*40)

test_fact = "TestFact(API, Format)."

# Different formats to try
formats = [
    # Format 1: Just statement
    {
        "name": "Simple statement",
        "data": {"statement": test_fact}
    },
    # Format 2: With context
    {
        "name": "Statement with context",
        "data": {"statement": test_fact, "context": {"source": "test"}}
    },
    # Format 3: Just fact
    {
        "name": "Just fact",
        "data": {"fact": test_fact}
    },
    # Format 4: Facts array
    {
        "name": "Facts array",
        "data": {"facts": [test_fact]}
    },
    # Format 5: Command style
    {
        "name": "Command style",
        "data": {"command": "add_fact", "query": test_fact}
    },
    # Format 6: Add style
    {
        "name": "Add style",
        "data": {"add": test_fact}
    },
    # Format 7: Statement with confidence
    {
        "name": "Statement with confidence",
        "data": {"statement": test_fact, "confidence": 1.0}
    },
    # Format 8: Predicate/args style
    {
        "name": "Predicate/args",
        "data": {"predicate": "TestFact", "args": ["API", "Format"]}
    }
]

print("\nTrying POST /api/facts with different formats:\n")

for fmt in formats:
    print(f"Testing: {fmt['name']}")
    print(f"  Data: {json.dumps(fmt['data'])}")
    
    try:
        response = requests.post(
            f"{API_URL}/api/facts",
            json=fmt['data'],
            timeout=5
        )
        
        print(f"  Status: {response.status_code}")
        
        if response.status_code == 200 or response.status_code == 201:
            print(f"  ✅ SUCCESS! This format works!")
            print(f"  Response: {response.text[:200]}")
            print("\n" + "="*60)
            print("WORKING FORMAT FOUND:")
            print(f"  Endpoint: POST /api/facts")
            print(f"  Data: {json.dumps(fmt['data'], indent=2)}")
            print("="*60)
            break
        elif response.status_code == 405:
            print(f"  ❌ Method not allowed")
        elif response.status_code == 400:
            print(f"  ⚠️ Bad request - wrong format")
            if response.text and len(response.text) < 200:
                print(f"  Error: {response.text}")
        else:
            print(f"  ❌ Error {response.status_code}")
            if response.text and len(response.text) < 200:
                print(f"  Message: {response.text}")
    
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    
    print()

# Also test GET /api/facts to see the format
print("\n" + "-"*60)
print("Checking GET /api/facts to see data format:")
try:
    response = requests.get(f"{API_URL}/api/facts", params={'limit': 2})
    if response.status_code == 200:
        data = response.json()
        print(f"✅ GET works! Response structure:")
        print(json.dumps(data, indent=2)[:500])
    else:
        print(f"❌ GET failed: {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")
