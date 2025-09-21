#!/usr/bin/env python3
"""
Test der Halluzinations-Präventions-API-Endpoints mit korrektem API-Key
"""

import requests
import json
import sys

API_BASE = "http://127.0.0.1:5002"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

def test_endpoint(endpoint, method="GET", data=None):
    """Teste einen einzelnen Endpoint mit API-Key"""
    url = f"{API_BASE}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            print(f"   ✅ Success!")
            try:
                json_response = response.json()
                print(f"   Response: {json.dumps(json_response, indent=2)[:300]}{'...' if len(json.dumps(json_response)) > 300 else ''}")
            except:
                print(f"   Response: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
        else:
            print(f"   ❌ Error: {response.text}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")
        return None

def main():
    """Teste alle Halluzinations-Präventions-Endpoints mit API-Key"""
    print("🚀 Testing Hallucination Prevention API Endpoints with API Key")
    print("=" * 70)
    print(f"🔑 API Key: {API_KEY}")
    print("=" * 70)
    
    # Test 1: Health Check (sollte ohne API-Key funktionieren)
    print("\n1. Health Check")
    test_endpoint("/health")
    
    # Test 2: Statistics
    print("\n2. Statistics Endpoint")
    test_endpoint("/api/hallucination-prevention/statistics")
    
    # Test 3: Validate Single Fact
    print("\n3. Validate Single Fact")
    test_endpoint("/api/hallucination-prevention/validate", "POST", {
        "fact": "HasProperty(H2O, liquid).",
        "level": "comprehensive"
    })
    
    # Test 4: Governance Compliance
    print("\n4. Governance Compliance")
    test_endpoint("/api/hallucination-prevention/governance-compliance", "POST", {
        "fact": "HasProperty(H2O, liquid)."
    })
    
    # Test 5: Quality Analysis
    print("\n5. Quality Analysis")
    test_endpoint("/api/hallucination-prevention/quality-analysis", "POST", {})
    
    # Test 6: Batch Validation
    print("\n6. Batch Validation")
    test_endpoint("/api/hallucination-prevention/validate-batch", "POST", {
        "fact_ids": [1, 2, 3],
        "level": "comprehensive"
    })
    
    # Test 7: Invalid Facts
    print("\n7. Invalid Facts")
    test_endpoint("/api/hallucination-prevention/invalid-facts")
    
    # Test 8: Configuration
    print("\n8. Configuration")
    test_endpoint("/api/hallucination-prevention/config", "POST", {
        "enabled": True,
        "auto_validation": True,
        "threshold": 0.8
    })
    
    # Test 9: Suggest Correction
    print("\n9. Suggest Correction")
    test_endpoint("/api/hallucination-prevention/suggest-correction/1")
    
    print("\n" + "=" * 70)
    print("✅ API Endpoint Testing Complete")

if __name__ == "__main__":
    main()
