#!/usr/bin/env python3
"""
Test Script für Halluzinations-Präventions-API-Endpoints
Testet die API-Endpoints mit echten Daten und HTTP-Requests
"""

import requests
import json
import time
import os
from pathlib import Path

# API Configuration
API_BASE_URL = "http://127.0.0.1:5002"
API_KEY = os.environ.get("HAKGAL_API_KEY", "your-api-key-here")

def get_api_key():
    """Hole API-Key aus verschiedenen Quellen"""
    # Versuche .env Dateien
    env_paths = [
        Path("D:/MCP Mods/hak_gal_user/.env"),
        Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/.env"),
        Path(".env")
    ]
    
    for env_path in env_paths:
        if env_path.exists():
            try:
                with open(env_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.startswith('HAKGAL_API_KEY='):
                            return line.split('=', 1)[1].strip().strip('"').strip("'")
            except Exception:
                continue
    
    return API_KEY

def make_api_request(endpoint, method="GET", data=None):
    """Mache API-Request mit Authentication"""
    url = f"{API_BASE_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": get_api_key()
    }
    
    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=30)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=30)
        else:
            raise ValueError(f"Unsupported method: {method}")
        
        return response
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None

def test_api_health():
    """Teste API-Health"""
    print("🏥 Testing API Health")
    print("-" * 40)
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            print("✅ API is healthy")
            return True
        else:
            print(f"❌ API health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to API: {e}")
        print("💡 Make sure the backend is running on port 5002")
        return False

def test_validate_fact_endpoint():
    """Teste /api/hallucination-prevention/validate"""
    print("\n🧪 Testing validate fact endpoint")
    print("-" * 40)
    
    # Test-Fakten
    test_facts = [
        "HasProperty(water, liquid).",
        "NH3 reacts with oxygen to form H2O and CO2.",
        "Water contains carbon and hydrogen.",
        "TCP is faster than HTTP.",
        "Water is a complex variable system."
    ]
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Testing: {fact}")
        
        data = {
            "fact": fact,
            "level": "comprehensive"
        }
        
        response = make_api_request("/api/hallucination-prevention/validate", "POST", data)
        
        if response and response.status_code == 200:
            result = response.json()
            validation = result.get('validation_result', {})
            
            print(f"   ✅ Valid: {validation.get('valid')}")
            print(f"   📊 Confidence: {validation.get('confidence', 0):.2f}")
            print(f"   📂 Category: {validation.get('category')}")
            
            if validation.get('issues'):
                print(f"   ⚠️ Issues: {validation['issues']}")
            
            if validation.get('correction'):
                print(f"   💡 Correction: {validation['correction']}")
        else:
            print(f"   ❌ Request failed: {response.status_code if response else 'No response'}")
            if response:
                print(f"   Error: {response.text}")

def test_governance_compliance_endpoint():
    """Teste /api/hallucination-prevention/governance-compliance"""
    print("\n⚖️ Testing governance compliance endpoint")
    print("-" * 40)
    
    test_facts = [
        "HasProperty(water, liquid).",
        "Water is harmful to humans.",
        "TCP is faster than HTTP."
    ]
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Testing: {fact}")
        
        data = {"fact": fact}
        response = make_api_request("/api/hallucination-prevention/governance-compliance", "POST", data)
        
        if response and response.status_code == 200:
            result = response.json()
            compliance = result.get('governance_compliance', {})
            
            print(f"   ✅ Compliant: {compliance.get('compliant')}")
            print(f"   📊 Confidence: {compliance.get('confidence', 0):.2f}")
            
            if compliance.get('issues'):
                print(f"   ⚠️ Issues: {compliance['issues']}")
        else:
            print(f"   ❌ Request failed: {response.status_code if response else 'No response'}")

def test_statistics_endpoint():
    """Teste /api/hallucination-prevention/statistics"""
    print("\n📊 Testing statistics endpoint")
    print("-" * 40)
    
    response = make_api_request("/api/hallucination-prevention/statistics", "GET")
    
    if response and response.status_code == 200:
        result = response.json()
        stats = result.get('statistics', {})
        
        print("✅ Statistics retrieved:")
        print(f"   📈 Total validated: {stats.get('stats', {}).get('total_validated', 0)}")
        print(f"   ❌ Invalid found: {stats.get('stats', {}).get('invalid_found', 0)}")
        print(f"   💡 Corrections suggested: {stats.get('stats', {}).get('corrections_suggested', 0)}")
        print(f"   ⚡ Cache hits: {stats.get('stats', {}).get('cache_hits', 0)}")
        
        validators = stats.get('validators_available', {})
        print(f"   🔧 Validators:")
        for validator, available in validators.items():
            status = "✅" if available else "❌"
            print(f"      {status} {validator}")
    else:
        print(f"❌ Request failed: {response.status_code if response else 'No response'}")

def test_quality_analysis_endpoint():
    """Teste /api/hallucination-prevention/quality-analysis"""
    print("\n📈 Testing quality analysis endpoint")
    print("-" * 40)
    
    response = make_api_request("/api/hallucination-prevention/quality-analysis", "POST", {})
    
    if response and response.status_code == 200:
        result = response.json()
        analysis = result.get('quality_analysis', {})
        
        if analysis.get('success'):
            data = analysis.get('analysis', {})
            print("✅ Quality analysis completed:")
            print(f"   📊 Total facts: {data.get('total_facts', 'N/A')}")
            print(f"   ⚠️ Vague facts: {data.get('vague_facts', 'N/A')}")
            print(f"   🚨 Problematic facts: {data.get('problematic_facts', 'N/A')}")
        else:
            print(f"❌ Quality analysis failed: {analysis.get('error')}")
    else:
        print(f"❌ Request failed: {response.status_code if response else 'No response'}")

def test_config_endpoint():
    """Teste /api/hallucination-prevention/config"""
    print("\n🔧 Testing config endpoint")
    print("-" * 40)
    
    # Test configuration update
    config_data = {
        "enabled": True,
        "auto_validation": True,
        "threshold": 0.8,
        "clear_cache": True
    }
    
    response = make_api_request("/api/hallucination-prevention/config", "POST", config_data)
    
    if response and response.status_code == 200:
        result = response.json()
        print("✅ Configuration updated successfully")
        print(f"   Message: {result.get('message')}")
    else:
        print(f"❌ Config update failed: {response.status_code if response else 'No response'}")

def main():
    """Haupttest-Funktion"""
    print("🚀 API Endpoints Test")
    print("Testing Hallucination Prevention API with real requests")
    print("=" * 60)
    
    # Prüfe API-Key
    api_key = get_api_key()
    if not api_key or api_key == "your-api-key-here":
        print("⚠️ Warning: No valid API key found")
        print("💡 Make sure HAKGAL_API_KEY is set in .env file")
    
    tests = [
        ("API Health", test_api_health),
        ("Validate Fact", test_validate_fact_endpoint),
        ("Governance Compliance", test_governance_compliance_endpoint),
        ("Statistics", test_statistics_endpoint),
        ("Quality Analysis", test_quality_analysis_endpoint),
        ("Configuration", test_config_endpoint)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*20} {test_name} {'='*20}")
            result = test_func()
            results.append((test_name, result is not False))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "="*60)
    print("📊 API ENDPOINTS TEST SUMMARY")
    print("="*60)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All API endpoint tests passed!")
        print("🚀 Hallucination Prevention API is working!")
    else:
        print("⚠️ Some API tests failed. Check the output above.")
        print("💡 Make sure:")
        print("   - Backend is running on port 5002")
        print("   - API key is correctly configured")
        print("   - All dependencies are installed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)

