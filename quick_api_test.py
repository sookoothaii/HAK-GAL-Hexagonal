#!/usr/bin/env python3
"""
Quick API Test für neue Claude Instanz
"""

import requests
import json

API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002"

def test_endpoint(name, method, endpoint, data=None):
    """Test einen einzelnen Endpoint"""
    print(f"\n🔍 Testing {name}")
    print("-" * 40)
    
    url = f"{BASE_URL}{endpoint}"
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    
    try:
        if method == "GET":
            response = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
        else:
            response = requests.post(url, headers=headers, json=data, timeout=10)
        
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS")
            return True
        else:
            print(f"❌ FAILED - HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")
        return False

def main():
    print("🚀 QUICK API TEST FÜR CLAUDE INSTANZ")
    print("=" * 50)
    
    tests = [
        ("Health Check", "GET", "/api/hallucination-prevention/health"),
        ("Statistics", "GET", "/api/hallucination-prevention/statistics"),
        ("Single Validation", "POST", "/api/hallucination-prevention/validate", {"fact": "HasProperty(water, liquid)"}),
        ("Quality Analysis", "POST", "/api/hallucination-prevention/quality-analysis", {}),
        ("Batch Validation", "POST", "/api/hallucination-prevention/validate-batch", [{"fact": "HasProperty(water, liquid)"}]),
        ("Suggest Correction", "POST", "/api/hallucination-prevention/suggest-correction", {"fact": "HasProperty(water,liquid)"}),
        ("Governance Compliance", "POST", "/api/hallucination-prevention/governance-compliance", {"fact": "HasProperty(water, liquid)"}),
        ("Invalid Facts", "GET", "/api/hallucination-prevention/invalid-facts"),
        ("Configuration", "POST", "/api/hallucination-prevention/config", {"validation_threshold": 0.8})
    ]
    
    results = []
    for test in tests:
        result = test_endpoint(*test)
        results.append(result)
    
    success_count = sum(results)
    total_count = len(results)
    
    print("\n" + "=" * 50)
    print(f"📊 RESULTS: {success_count}/{total_count} endpoints working")
    print(f"Success Rate: {(success_count/total_count)*100:.1f}%")
    
    if success_count == total_count:
        print("🎉 ALL ENDPOINTS WORKING!")
    else:
        print(f"⚠️ {total_count - success_count} endpoints need fixing")

if __name__ == "__main__":
    main()

