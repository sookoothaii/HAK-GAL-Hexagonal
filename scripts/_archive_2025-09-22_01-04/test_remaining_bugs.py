#!/usr/bin/env python3
"""
Test der verbleibenden 2 kritischen Bugs nach empirischer Validierung
"""

import requests
import json
import time

API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002"

def test_batch_validation():
    """Test Batch Validation HTTP 500 Problem"""
    print("🔍 TEST 1: Batch Validation HTTP 500 Problem")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/validate-batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test verschiedene Payload-Formate
    test_cases = [
        {
            "name": "Standard Format",
            "data": {"fact_ids": [314, 288], "validation_level": "comprehensive"}
        },
        {
            "name": "Minimal Format", 
            "data": {"fact_ids": [314]}
        },
        {
            "name": "Single Element",
            "data": {"fact_ids": [314], "validation_level": "comprehensive"}
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📝 Test Case {i}: {test_case['name']}")
        print(f"Payload: {json.dumps(test_case['data'])}")
        
        try:
            response = requests.post(url, headers=headers, json=test_case['data'], timeout=10)
            print(f"Status: {response.status_code}")
            print(f"Response: {response.text[:200]}...")
            
            if response.status_code == 200:
                print("✅ SUCCESS!")
                return True
            elif response.status_code == 500:
                print("🔴 HTTP 500 - Backend Error")
            elif response.status_code == 400:
                print("🟡 HTTP 400 - Bad Request Format")
            else:
                print(f"⚠️ Unexpected Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Exception: {e}")
    
    return False

def test_suggest_correction():
    """Test Suggest Correction HTTP 405 Problem"""
    print("\n🔍 TEST 2: Suggest Correction HTTP 405 Problem")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/suggest-correction/314"
    headers = {"X-API-Key": API_KEY}
    
    print(f"URL: {url}")
    print(f"Method: GET")
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS!")
            return True
        elif response.status_code == 405:
            print("🔴 HTTP 405 - Method Not Allowed (Endpoint nicht implementiert)")
        elif response.status_code == 404:
            print("🟡 HTTP 404 - Not Found (Route nicht registriert)")
        else:
            print(f"⚠️ Unexpected Status: {response.status_code}")
            
    except Exception as e:
        print(f"❌ Exception: {e}")
    
    return False

def test_working_endpoints():
    """Test funktionierende Endpoints als Baseline"""
    print("\n✅ BASELINE: Funktionierende Endpoints")
    print("=" * 60)
    
    # Test Quality Analysis (sollte jetzt funktionieren)
    print("\n📊 Quality Analysis Test:")
    url = f"{BASE_URL}/api/hallucination-prevention/quality-analysis"
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Success: {data.get('success', 'N/A')}")
            print("✅ Quality Analysis funktional")
        else:
            print(f"❌ Quality Analysis failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Quality Analysis exception: {e}")
    
    # Test Health Endpoint (sollte jetzt funktionieren)
    print("\n🏥 Health Endpoint Test:")
    url = f"{BASE_URL}/api/hallucination-prevention/health"
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            print("✅ Health Endpoint funktional")
        else:
            print(f"❌ Health Endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health Endpoint exception: {e}")

def main():
    print("🚀 SYSTEMATIC REMAINING BUGS TEST")
    print("=" * 80)
    print("Test der verbleibenden 2 kritischen Bugs nach empirischer Validierung")
    print("=" * 80)
    
    # Test funktionierende Endpoints als Baseline
    test_working_endpoints()
    
    # Test verbleibende Bugs
    batch_success = test_batch_validation()
    suggest_success = test_suggest_correction()
    
    print("\n" + "=" * 80)
    print("📊 FINAL TEST RESULTS")
    print("=" * 80)
    print(f"✅ Batch Validation: {'FIXED' if batch_success else 'STILL BROKEN'}")
    print(f"✅ Suggest Correction: {'FIXED' if suggest_success else 'STILL BROKEN'}")
    
    if batch_success and suggest_success:
        print("\n🎉 ALL BUGS FIXED! API 100% FUNCTIONAL!")
    else:
        print(f"\n⚠️ {2 - (batch_success + suggest_success)} bugs still need fixing")

if __name__ == "__main__":
    main()

