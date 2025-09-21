#!/usr/bin/env python3
"""
Direkter Test der Halluzinations-Präventions-API-Endpoints
"""

import requests
import json
import sys

API_BASE = "http://127.0.0.1:5002"

def test_endpoint(endpoint, method="GET", data=None, headers=None):
    """Teste einen einzelnen Endpoint"""
    url = f"{API_BASE}{endpoint}"
    
    default_headers = {"Content-Type": "application/json"}
    if headers:
        default_headers.update(headers)
    
    try:
        if method == "GET":
            response = requests.get(url, headers=default_headers, timeout=10)
        elif method == "POST":
            response = requests.post(url, headers=default_headers, json=data, timeout=10)
        else:
            print(f"❌ Unsupported method: {method}")
            return None
        
        print(f"🔍 {method} {endpoint}")
        print(f"   Status: {response.status_code}")
        print(f"   Response: {response.text[:200]}{'...' if len(response.text) > 200 else ''}")
        
        return response
        
    except Exception as e:
        print(f"❌ Error testing {endpoint}: {e}")
        return None

def main():
    """Teste alle Halluzinations-Präventions-Endpoints"""
    print("🚀 Testing Hallucination Prevention API Endpoints")
    print("=" * 60)
    
    # Test 1: Health Check
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
        "auto_validation": True
    })
    
    print("\n" + "=" * 60)
    print("✅ API Endpoint Testing Complete")

if __name__ == "__main__":
    main()

