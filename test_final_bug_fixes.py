#!/usr/bin/env python3
"""
Finale empirische Validierung aller Bug-Fixes nach HAK_GAL Verfassung P6 & L3
"""

import requests
import json
import time

API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002"

def test_batch_validation_fix():
    """Test Batch Validation Fix (HTTP 500 → HTTP 200)"""
    print("🔍 TEST 1: Batch Validation Fix (HTTP 500 → HTTP 200)")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/validate-batch"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test mit dem ursprünglich fehlgeschlagenen Format
    test_data = [
        {"fact": "HasProperty(water, liquid)"},
        {"fact": "IsA(hydrogen, element)"}
    ]
    
    print(f"Testing with original failing format: {json.dumps(test_data)}")
    
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Batch Validation HTTP 500 → HTTP 200 FIXED!")
            return True
        elif response.status_code == 500:
            print("🔴 STILL HTTP 500 - Fix failed")
            return False
        else:
            print(f"⚠️ Unexpected Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_suggest_correction_fix():
    """Test Suggest Correction Fix (HTTP 405 → HTTP 200)"""
    print("\n🔍 TEST 2: Suggest Correction Fix (HTTP 405 → HTTP 200)")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/suggest-correction"
    headers = {
        "X-API-Key": API_KEY,
        "Content-Type": "application/json"
    }
    
    # Test mit dem ursprünglich fehlgeschlagenen POST Format
    test_data = {"fact": "HasProperty(water,liquid)"}
    
    print(f"Testing POST format: {json.dumps(test_data)}")
    
    try:
        response = requests.post(url, headers=headers, json=test_data, timeout=10)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.text[:300]}...")
        
        if response.status_code == 200:
            print("✅ SUCCESS! Suggest Correction HTTP 405 → HTTP 200 FIXED!")
            return True
        elif response.status_code == 405:
            print("🔴 STILL HTTP 405 - Fix failed")
            return False
        else:
            print(f"⚠️ Unexpected Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_quality_analysis_still_working():
    """Test dass Quality Analysis Fix weiterhin funktioniert"""
    print("\n🔍 TEST 3: Quality Analysis Fix Still Working")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/quality-analysis"
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.post(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            success = data.get('success', False)
            print(f"Success: {success}")
            if success:
                print("✅ Quality Analysis Fix still working!")
                return True
            else:
                print("🔴 Quality Analysis Success=False again!")
                return False
        else:
            print(f"❌ Quality Analysis HTTP {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_health_endpoint_still_working():
    """Test dass Health Endpoint Fix weiterhin funktioniert"""
    print("\n🔍 TEST 4: Health Endpoint Fix Still Working")
    print("=" * 60)
    
    url = f"{BASE_URL}/api/hallucination-prevention/health"
    headers = {"X-API-Key": API_KEY}
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            print("✅ Health Endpoint Fix still working!")
            return True
        else:
            print(f"🔴 Health Endpoint HTTP {response.status_code} again!")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_all_endpoints_comprehensive():
    """Test alle 9 Endpoints für finale API-Erfolgsrate"""
    print("\n🔍 TEST 5: Comprehensive All Endpoints Test")
    print("=" * 60)
    
    endpoints = [
        ("Single Validation", "POST", "/api/hallucination-prevention/validate", {"fact": "HasProperty(water, liquid)"}),
        ("Batch Validation", "POST", "/api/hallucination-prevention/validate-batch", [{"fact": "HasProperty(water, liquid)"}]),
        ("Quality Analysis", "POST", "/api/hallucination-prevention/quality-analysis", {}),
        ("Health Endpoint", "GET", "/api/hallucination-prevention/health", None),
        ("Suggest Correction", "POST", "/api/hallucination-prevention/suggest-correction", {"fact": "HasProperty(water,liquid)"}),
        ("Statistics", "GET", "/api/hallucination-prevention/statistics", None),
        ("Governance Compliance", "POST", "/api/hallucination-prevention/governance-compliance", {"fact": "HasProperty(water, liquid)"}),
        ("Invalid Facts", "GET", "/api/hallucination-prevention/invalid-facts", None),
        ("Configuration", "POST", "/api/hallucination-prevention/config", {"validation_threshold": 0.8})
    ]
    
    headers = {"X-API-Key": API_KEY, "Content-Type": "application/json"}
    working_count = 0
    
    for name, method, endpoint, data in endpoints:
        try:
            url = f"{BASE_URL}{endpoint}"
            
            if method == "GET":
                response = requests.get(url, headers={"X-API-Key": API_KEY}, timeout=10)
            else:
                response = requests.post(url, headers=headers, json=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ {name}: HTTP 200")
                working_count += 1
            else:
                print(f"❌ {name}: HTTP {response.status_code}")
                
        except Exception as e:
            print(f"❌ {name}: Exception {e}")
    
    success_rate = (working_count / len(endpoints)) * 100
    print(f"\n📊 FINAL API SUCCESS RATE: {working_count}/{len(endpoints)} ({success_rate:.1f}%)")
    
    return success_rate >= 95.0  # 95%+ für "vollständig funktional"

def main():
    print("🚀 FINALE EMPIRISCHE VALIDIERUNG ALLER BUG-FIXES")
    print("=" * 80)
    print("Nach HAK_GAL Verfassung P6 & L3 - Alle Behauptungen systematisch testen")
    print("=" * 80)
    
    # Test alle Fixes
    batch_fix = test_batch_validation_fix()
    suggest_fix = test_suggest_correction_fix()
    quality_still_working = test_quality_analysis_still_working()
    health_still_working = test_health_endpoint_still_working()
    comprehensive_test = test_all_endpoints_comprehensive()
    
    print("\n" + "=" * 80)
    print("📊 FINALE EMPIRISCHE BEWERTUNG")
    print("=" * 80)
    
    print(f"✅ Batch Validation Fix: {'SUCCESS' if batch_fix else 'FAILED'}")
    print(f"✅ Suggest Correction Fix: {'SUCCESS' if suggest_fix else 'FAILED'}")
    print(f"✅ Quality Analysis Still Working: {'YES' if quality_still_working else 'NO'}")
    print(f"✅ Health Endpoint Still Working: {'YES' if health_still_working else 'NO'}")
    print(f"✅ Comprehensive API Test: {'PASS' if comprehensive_test else 'FAIL'}")
    
    all_fixes_working = batch_fix and suggest_fix and quality_still_working and health_still_working and comprehensive_test
    
    if all_fixes_working:
        print("\n🎉 ALLE BUG-FIXES EMPIRISCH VALIDIERT!")
        print("🎯 API 100% FUNKTIONAL - HAK_GAL VERFASSUNG COMPLIANCE ERREICHT!")
    else:
        print(f"\n⚠️ {5 - sum([batch_fix, suggest_fix, quality_still_working, health_still_working, comprehensive_test])} Tests failed - Fixes incomplete")

if __name__ == "__main__":
    main()

