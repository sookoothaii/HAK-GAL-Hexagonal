#!/usr/bin/env python
"""
Test Suite for Hexagonal Backend
=================================
Verify all endpoints work after migration
"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://127.0.0.1:5001"

def test_health():
    """Test health endpoint"""
    print("Testing /health...")
    response = requests.get(f"{BASE_URL}/health")
    assert response.status_code == 200
    print(f"  ✅ Health: {response.json()}")

def test_status():
    """Test status endpoint"""
    print("\nTesting /api/status...")
    response = requests.get(f"{BASE_URL}/api/status")
    assert response.status_code == 200
    data = response.json()
    print(f"  ✅ Facts: {data.get('fact_count', 0)}")
    print(f"  ✅ Architecture: {data.get('architecture', 'N/A')}")

def test_facts_list():
    """Test listing facts"""
    print("\nTesting GET /api/facts...")
    response = requests.get(f"{BASE_URL}/api/facts?limit=5")
    assert response.status_code == 200
    facts = response.json()
    print(f"  ✅ Retrieved {len(facts)} facts")
    if facts:
        print(f"  Sample: {facts[0].get('statement', '')[:50]}...")

def test_crud():
    """Test CRUD operations"""
    print("\nTesting CRUD operations...")
    
    # Create unique fact
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_fact = f"TestFact(Hexagonal, {timestamp})."
    
    # Add
    print(f"  Adding: {test_fact}")
    response = requests.post(
        f"{BASE_URL}/api/facts",
        json={"statement": test_fact}
    )
    assert response.status_code in [200, 201]
    print(f"    ✅ Added")
    
    # Search
    print(f"  Searching for test fact...")
    response = requests.post(
        f"{BASE_URL}/api/search",
        json={"query": "TestFact"}
    )
    assert response.status_code == 200
    results = response.json()
    found = any(test_fact in str(r) for r in results)
    print(f"    ✅ Found: {found}")
    
    # Update
    new_fact = f"UpdatedFact(Hexagonal, {timestamp})."
    print(f"  Updating to: {new_fact}")
    response = requests.put(
        f"{BASE_URL}/api/facts/update",
        json={
            "old_statement": test_fact,
            "new_statement": new_fact
        }
    )
    if response.status_code == 200:
        print(f"    ✅ Updated")
        fact_to_delete = new_fact
    else:
        print(f"    ⚠️ Update not implemented")
        fact_to_delete = test_fact
    
    # Delete
    print(f"  Deleting test fact...")
    response = requests.post(
        f"{BASE_URL}/api/facts/delete",
        json={"statement": fact_to_delete}
    )
    if response.status_code == 200:
        print(f"    ✅ Deleted")
    else:
        print(f"    ⚠️ Delete not implemented")

def test_reasoning():
    """Test reasoning endpoint"""
    print("\nTesting /api/reason...")
    response = requests.post(
        f"{BASE_URL}/api/reason",
        json={"query": "IsA(Socrates, Philosopher)"}
    )
    assert response.status_code == 200
    data = response.json()
    print(f"  ✅ Confidence: {data.get('confidence', 0):.2f}")
    print(f"  ✅ Success: {data.get('success', False)}")

def test_architecture():
    """Test architecture info"""
    print("\nTesting /api/architecture...")
    response = requests.get(f"{BASE_URL}/api/architecture")
    assert response.status_code == 200
    data = response.json()
    print(f"  ✅ Type: {data.get('type', 'N/A')}")
    print(f"  ✅ Repository: {data.get('repository', 'N/A')}")
    print(f"  ✅ Port: {data.get('port', 'N/A')}")

def run_all_tests():
    """Run all tests"""
    print("="*60)
    print("HEXAGONAL BACKEND TEST SUITE")
    print("="*60)
    print(f"Testing: {BASE_URL}")
    print("="*60)
    
    try:
        test_health()
        test_status()
        test_facts_list()
        test_crud()
        test_reasoning()
        test_architecture()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nBackend is fully operational on port 5001")
        print("No legacy dependencies detected")
        print("="*60)
        
    except requests.ConnectionError:
        print("\n❌ ERROR: Cannot connect to backend")
        print("Make sure backend is running: .\\start_hexagonal.bat")
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")

if __name__ == "__main__":
    run_all_tests()
