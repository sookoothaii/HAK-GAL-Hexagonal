#!/usr/bin/env python3
"""
Test Script für Halluzinations-Präventions-Integration
Testet die Integration der 4 Validatoren in das Backend
"""

import sys
import os
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))

def test_imports():
    """Teste alle Imports"""
    print("🔍 Testing imports...")
    
    try:
        from application.hallucination_prevention_service import (
            HallucinationPreventionService, 
            ValidationLevel,
            create_hallucination_prevention_service
        )
        print("✅ Hallucination Prevention Service import successful")
    except Exception as e:
        print(f"❌ Hallucination Prevention Service import failed: {e}")
        return False
    
    try:
        from adapters.hallucination_prevention_adapter import (
            HallucinationPreventionAdapter,
            create_hallucination_prevention_adapter
        )
        print("✅ Hallucination Prevention Adapter import successful")
    except Exception as e:
        print(f"❌ Hallucination Prevention Adapter import failed: {e}")
        return False
    
    return True

def test_service_creation():
    """Teste Service-Erstellung"""
    print("\n🔧 Testing service creation...")
    
    try:
        from application.hallucination_prevention_service import create_hallucination_prevention_service
        
        service = create_hallucination_prevention_service()
        print("✅ Hallucination Prevention Service created successfully")
        
        # Test statistics
        stats = service.get_validation_statistics()
        print(f"📊 Service statistics: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Service creation failed: {e}")
        return False

def test_adapter_creation():
    """Teste Adapter-Erstellung"""
    print("\n🔌 Testing adapter creation...")
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        print("✅ Hallucination Prevention Adapter created successfully")
        
        # Test statistics
        stats = adapter.get_validation_statistics()
        print(f"📊 Adapter statistics: {stats}")
        
        return True
    except Exception as e:
        print(f"❌ Adapter creation failed: {e}")
        return False

def test_fact_validation():
    """Teste Fakt-Validierung"""
    print("\n🧪 Testing fact validation...")
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        
        # Test fakt
        test_fact = "HasProperty(water, liquid)."
        
        # Validiere Fakt
        result = adapter.validate_fact_before_insert(test_fact)
        print(f"✅ Fact validation successful")
        print(f"📝 Validation result: {result}")
        
        # Test Governance-Compliance
        compliance = adapter.validate_governance_compliance(test_fact)
        print(f"✅ Governance compliance check successful")
        print(f"⚖️ Compliance result: {compliance}")
        
        return True
    except Exception as e:
        print(f"❌ Fact validation failed: {e}")
        return False

def test_api_endpoints():
    """Teste API-Endpoint-Integration"""
    print("\n🌐 Testing API endpoint integration...")
    
    try:
        # Test Backend-Import (ohne vollständige Initialisierung)
        from hexagonal_api_enhanced_clean import HexagonalAPI
        print("✅ Backend API import successful")
        
        # Prüfe ob Hallucination-Prevention-Endpoints definiert sind
        api_file = Path("src_hexagonal/hexagonal_api_enhanced_clean.py")
        content = api_file.read_text(encoding='utf-8')
        
        required_endpoints = [
            "/api/hallucination-prevention/validate",
            "/api/hallucination-prevention/validate-batch",
            "/api/hallucination-prevention/statistics",
            "/api/hallucination-prevention/quality-analysis",
            "/api/hallucination-prevention/governance-compliance"
        ]
        
        for endpoint in required_endpoints:
            if endpoint in content:
                print(f"✅ Endpoint {endpoint} found")
            else:
                print(f"❌ Endpoint {endpoint} missing")
                return False
        
        return True
    except Exception as e:
        print(f"❌ API endpoint integration test failed: {e}")
        return False

def test_validator_files():
    """Teste Validator-Dateien"""
    print("\n📁 Testing validator files...")
    
    validator_files = [
        "src_hexagonal/application/strict_scientific_validator.py",
        "src_hexagonal/application/validate_facts_with_llm.py", 
        "src_hexagonal/application/quality_check.py",
        "src_hexagonal/application/deepseek_reasoning_validator.py"
    ]
    
    all_found = True
    for file_path in validator_files:
        if Path(file_path).exists():
            print(f"✅ {file_path} found")
        else:
            print(f"❌ {file_path} missing")
            all_found = False
    
    return all_found

def main():
    """Haupttest-Funktion"""
    print("🚀 Hallucination Prevention Integration Test")
    print("=" * 50)
    
    tests = [
        ("Validator Files", test_validator_files),
        ("Imports", test_imports),
        ("Service Creation", test_service_creation),
        ("Adapter Creation", test_adapter_creation),
        ("Fact Validation", test_fact_validation),
        ("API Endpoints", test_api_endpoints)
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results.append((test_name, False))
    
    # Zusammenfassung
    print("\n" + "="*50)
    print("📊 TEST SUMMARY")
    print("="*50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Integration successful!")
        return True
    else:
        print("⚠️ Some tests failed. Check the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

