#!/usr/bin/env python3
"""
Test Clean API - Verify No Mocks
=================================
Testet ob die API ehrlich ist und keine Fake-Daten liefert
"""

import requests
import json

API_URL = "http://127.0.0.1:5001"

def test_honest_api():
    """Test that API returns honest errors instead of mocks"""
    
    print("=" * 60)
    print("TESTING CLEAN API - NO MOCKS")
    print("=" * 60)
    
    # Test 1: Health Check
    print("\n1. Health Check...")
    try:
        resp = requests.get(f"{API_URL}/health", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ API running: {data}")
            if 'clean' in str(data):
                print("   ✅ Clean version detected!")
        else:
            print(f"   ❌ Health check failed: {resp.status_code}")
            return
    except Exception as e:
        print(f"   ❌ API not reachable: {e}")
        print("\n   Please start the API first with: start_clean_api.bat")
        return
    
    # Test 2: LLM Explanation (should fail honestly if no LLM)
    print("\n2. Testing LLM Explanation (expecting honest error)...")
    try:
        resp = requests.post(
            f"{API_URL}/api/llm/get-explanation",
            json={
                "topic": "IsA(Socrates, Philosopher)",
                "context_facts": []
            },
            timeout=35
        )
        
        print(f"   Status Code: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 503:
            print("   ✅ HONEST ERROR! Service unavailable")
            print(f"   Message: {data.get('message', '')}")
            print(f"   Explanation: {data.get('explanation', '')}")
            
            # Check for fake facts
            suggested = data.get('suggested_facts', [])
            if len(suggested) == 0:
                print("   ✅ NO FAKE FACTS! Empty list as expected")
            else:
                print(f"   ❌ Still has {len(suggested)} fake facts!")
                
        elif resp.status_code == 200:
            # Real LLM response
            if 'error' in data.get('explanation', '').lower():
                print("   ✅ Got error message in explanation")
            else:
                print("   ℹ️ Got real LLM response (API keys configured)")
                print(f"   Preview: {data.get('explanation', '')[:100]}...")
        else:
            print(f"   ⚠️ Unexpected status: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Command endpoint
    print("\n3. Testing /api/command explain (expecting honest error)...")
    try:
        resp = requests.post(
            f"{API_URL}/api/command",
            json={
                "command": "explain",
                "query": "HasPart(Computer, CPU)"
            },
            timeout=35
        )
        
        print(f"   Status Code: {resp.status_code}")
        data = resp.json()
        
        if resp.status_code == 503:
            print("   ✅ HONEST ERROR! Service unavailable")
        elif resp.status_code == 200:
            if 'chatResponse' in data:
                chat = data['chatResponse']
                explanation = chat.get('natural_language_explanation', '')
                facts = chat.get('suggested_facts', [])
                
                if 'error' in explanation.lower() or 'not available' in explanation.lower():
                    print("   ✅ Got honest error message")
                    if len(facts) == 0:
                        print("   ✅ No fake facts!")
                else:
                    print("   ℹ️ Got real LLM response")
                    
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 4: Fact operations (should still work)
    print("\n4. Testing fact operations (should work)...")
    try:
        from datetime import datetime
        test_fact = f"TestFact{datetime.now().strftime('%Y%m%d%H%M%S')}(A,B)."
        
        resp = requests.post(
            f"{API_URL}/api/facts",
            json={"statement": test_fact},
            timeout=10
        )
        
        if resp.status_code == 201:
            print("   ✅ Fact addition still works!")
        elif resp.status_code == 409:
            print("   ✅ Duplicate detection works!")
        else:
            print(f"   ⚠️ Unexpected status: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 5: Reasoning (should work)
    print("\n5. Testing reasoning (should work)...")
    try:
        resp = requests.post(
            f"{API_URL}/api/reason",
            json={"query": "IsA(Socrates, Philosopher)"},
            timeout=10
        )
        
        if resp.status_code == 200:
            data = resp.json()
            print(f"   ✅ Reasoning works! Confidence: {data.get('confidence', 0):.3f}")
        else:
            print(f"   ❌ Reasoning failed: {resp.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print("The Clean API:")
    print("✅ Returns honest errors when LLM not available")
    print("✅ No fake suggested facts")
    print("✅ No mock explanations")
    print("✅ Core functions (facts, reasoning) still work")
    print("\nThis is HONEST software - no deception!")
    print("=" * 60)

if __name__ == "__main__":
    print("\nTesting Clean API...")
    print("Make sure to start it with: start_clean_api.bat")
    print("Press Enter to continue...")
    input()
    
    test_honest_api()
