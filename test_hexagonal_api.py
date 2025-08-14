#!/usr/bin/env python3
"""
Hexagonal API Test Client
==========================
Testet alle Endpoints der Hexagonal API
"""

import requests
import json
import time

BASE_URL = "http://localhost:5001"

def test_health():
    """Test Health Endpoint"""
    print("\n🔍 Testing /health...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data['status']}")
            print(f"  ✅ Architecture: {data['architecture']}")
            print(f"  ✅ Port: {data['port']}")
            print(f"  ✅ Repository: {data['repository']}")
            return True
    except requests.exceptions.ConnectionError:
        print("  ❌ API not running on port 5001")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_status():
    """Test Status Endpoint"""
    print("\n🔍 Testing /api/status...")
    try:
        response = requests.get(f"{BASE_URL}/api/status")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Status: {data['status']}")
            print(f"  ✅ Facts Count: {data['facts_count']}")
            print(f"  ✅ Repository: {data['repository_type']}")
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_get_facts():
    """Test GET Facts"""
    print("\n🔍 Testing GET /api/facts...")
    try:
        response = requests.get(f"{BASE_URL}/api/facts?limit=5")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Retrieved {data['count']} facts")
            print(f"  ✅ Total in DB: {data['total']}")
            
            # Show first fact
            if data['facts']:
                first = data['facts'][0]
                print(f"  📝 Example: {first['statement'][:50]}...")
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_add_fact():
    """Test POST Fact"""
    print("\n🔍 Testing POST /api/facts...")
    
    # Create unique fact
    timestamp = int(time.time())
    test_fact = {
        "statement": f"TestFact{timestamp}(Hexagonal,Working)",
        "context": {
            "source": "test_client",
            "timestamp": timestamp
        }
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/facts",
            json=test_fact
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print(f"  ✅ Success: {data['success']}")
            print(f"  ✅ Message: {data['message']}")
            return True
        else:
            data = response.json()
            print(f"  ⚠️ Response: {data}")
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_search():
    """Test Search Endpoint"""
    print("\n🔍 Testing POST /api/search...")
    
    search_query = {
        "query": "Socrates",
        "limit": 5
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=search_query
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Query: {data['query']}")
            print(f"  ✅ Results: {data['count']} facts found")
            
            if data['results']:
                print(f"  📝 First match: {data['results'][0]['statement'][:50]}...")
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_reasoning():
    """Test Reasoning Endpoint"""
    print("\n🔍 Testing POST /api/reason...")
    
    reason_query = {
        "query": "HasTrait(Mammalia,ProducesMilk)"
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/reason",
            json=reason_query
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Query: {data['query']}")
            print(f"  ✅ Confidence: {data['confidence']:.4f}")
            print(f"  ✅ High Confidence: {data['high_confidence']}")
            print(f"  ✅ Terms: {', '.join(data['reasoning_terms'])}")
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def test_architecture():
    """Test Architecture Info"""
    print("\n🔍 Testing /api/architecture...")
    try:
        response = requests.get(f"{BASE_URL}/api/architecture")
        if response.status_code == 200:
            data = response.json()
            print(f"  ✅ Pattern: {data['pattern']}")
            print(f"  ✅ Layers: {len(data['layers'])} layers defined")
            print(f"  ✅ Benefits: {len(data['benefits'])} benefits listed")
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
    return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("HAK-GAL HEXAGONAL API TEST SUITE")
    print("=" * 60)
    print(f"Target: {BASE_URL}")
    print("Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung")
    
    tests = [
        ("Health Check", test_health),
        ("System Status", test_status),
        ("Get Facts", test_get_facts),
        ("Add Fact", test_add_fact),
        ("Search Facts", test_search),
        ("Reasoning", test_reasoning),
        ("Architecture", test_architecture)
    ]
    
    results = {}
    for test_name, test_func in tests:
        results[test_name] = test_func()
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS:")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {test_name:20} : {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ ALL TESTS PASSED!")
        print("Hexagonal API is fully operational!")
    else:
        failed = [name for name, passed in results.items() if not passed]
        print(f"❌ {len(failed)} TESTS FAILED:")
        for name in failed:
            print(f"  - {name}")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == '__main__':
    exit(main())
