#!/usr/bin/env python3
"""
Quick Test for Hexagonal API Fixes
===================================
Tests both duplicate detection and LLM explanation
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5001"

def test_api():
    """Run comprehensive API tests"""
    
    print("=" * 60)
    print("HEXAGONAL API TEST SUITE")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Testing Health Check...")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            print("   ✅ API is running")
            print(f"   Response: {resp.json()}")
        else:
            print(f"   ❌ Health check failed: {resp.status_code}")
    except Exception as e:
        print(f"   ❌ API not reachable: {e}")
        print("\n   Please start the API first!")
        return
    
    # Test 2: Add New Fact
    print("\n2. Testing Add Fact (should work)...")
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    test_fact = f"TestFact{timestamp}(TestA,TestB)."
    
    try:
        resp = requests.post(
            f"{API_URL}/api/facts",
            json={"statement": test_fact},
            timeout=10
        )
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        if resp.status_code == 201:
            print("   ✅ Fact added successfully!")
        elif resp.status_code == 409:
            print("   ⚠️ Fact already exists (duplicate detection working)")
        else:
            print(f"   ❌ Unexpected status: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error adding fact: {e}")
    
    # Test 3: Try to add same fact again (should fail with 409)
    print("\n3. Testing Duplicate Detection...")
    time.sleep(1)
    
    try:
        resp = requests.post(
            f"{API_URL}/api/facts",
            json={"statement": test_fact},
            timeout=10
        )
        print(f"   Status: {resp.status_code}")
        print(f"   Response: {resp.json()}")
        
        if resp.status_code == 409:
            print("   ✅ Duplicate detection working correctly!")
        elif resp.status_code == 201:
            print("   ❌ Duplicate detection NOT working (fact added twice)")
        else:
            print(f"   ⚠️ Unexpected status: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Test /api/command endpoint
    print("\n4. Testing /api/command endpoint...")
    try:
        resp = requests.post(
            f"{API_URL}/api/command",
            json={
                "command": "add_fact",
                "statement": f"CommandTest{timestamp}(A,B)."
            },
            timeout=10
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code in [201, 409]:
            print("   ✅ /api/command endpoint working!")
        else:
            print(f"   ❌ Command endpoint error: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Test LLM Explanation
    print("\n5. Testing LLM Explanation...")
    try:
        resp = requests.post(
            f"{API_URL}/api/llm/get-explanation",
            json={
                "topic": "HasPart(Computer,CPU)",
                "context_facts": ["HasPart(Computer,RAM).", "HasPart(Computer,Motherboard)."]
            },
            timeout=30
        )
        print(f"   Status: {resp.status_code}")
        if resp.status_code == 200:
            result = resp.json()
            if 'explanation' in result:
                print("   ✅ LLM Explanation working!")
                print(f"   Preview: {result['explanation'][:200]}...")
            else:
                print("   ⚠️ Response missing explanation field")
        else:
            print(f"   ❌ LLM endpoint error: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 6: Count Facts
    print("\n6. Testing Fact Count...")
    try:
        resp = requests.get(f"{API_URL}/api/facts/count", timeout=10)
        if resp.status_code == 200:
            count = resp.json().get('count', 0)
            print(f"   ✅ Total facts: {count}")
        else:
            print(f"   ❌ Count endpoint error: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("TEST SUITE COMPLETE")
    print("=" * 60)

if __name__ == "__main__":
    test_api()
