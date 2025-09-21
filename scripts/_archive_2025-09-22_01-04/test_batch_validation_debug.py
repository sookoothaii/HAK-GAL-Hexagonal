#!/usr/bin/env python3
"""
Debug Batch Validation HTTP 500 Problem
"""

import requests
import json

API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002"

def test_batch_validation_formats():
    """Test verschiedene Batch Validation Formate"""
    print("🔍 DEBUG: Batch Validation HTTP 500 Problem")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/validate-batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    test_cases = [
        {
            "name": "Original failing format (Array of objects)",
            "data": [{"fact": "HasProperty(water, liquid)"}, {"fact": "IsA(hydrogen, element)"}]
        },
        {
            "name": "fact_ids format",
            "data": {"fact_ids": [314, 288], "validation_level": "comprehensive"}
        },
        {
            "name": "facts object format",
            "data": {"facts": [{"fact": "HasProperty(water, liquid)"}], "validation_level": "comprehensive"}
        },
        {
            "name": "Simple array of strings",
            "data": ["HasProperty(water, liquid)", "IsA(hydrogen, element)"]
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['data'])}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'], timeout=10)
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                result = response.json()
                print(f"Response keys: {list(result.keys())}")
                return True
            elif response.status_code == 500:
                print("🔴 HTTP 500 - Backend Error")
                print(f"Error: {response.text[:200]}")
            elif response.status_code == 400:
                print("🟡 HTTP 400 - Bad Request")
                print(f"Error: {response.text[:200]}")
            else:
                print(f"⚠️ Unexpected Status: {response.status_code}")
                print(f"Response: {response.text[:200]}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

def check_backend_logs():
    """Prüfe ob Backend-Logs verfügbar sind"""
    print("\n🔍 Backend Status Check")
    print("=" * 40)
    
    # Test ob Backend überhaupt läuft
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"Backend Health: HTTP {response.status_code}")
        
        # Test Hallucination Prevention Health
        response = requests.get(
            f"{BASE_URL}/api/hallucination-prevention/health",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        print(f"HP Health: HTTP {response.status_code}")
        
    except Exception as e:
        print(f"❌ Backend not reachable: {e}")

def main():
    print("🚀 BATCH VALIDATION DEBUG SCRIPT")
    print("=" * 50)
    
    check_backend_logs()
    
    success = test_batch_validation_formats()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ BATCH VALIDATION WORKING!")
        print("🎉 ALL API ENDPOINTS NOW FUNCTIONAL!")
    else:
        print("❌ BATCH VALIDATION STILL BROKEN")
        print("🔧 Backend restart may be required")

if __name__ == "__main__":
    main()

