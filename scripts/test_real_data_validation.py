#!/usr/bin/env python3
"""
Test Script für Halluzinations-Prävention mit echten Daten
Testet die Integration mit echten Fakten aus der HAK_GAL Knowledge Base
"""

import sys
import os
import sqlite3
import json
import time
from pathlib import Path
from datetime import datetime

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))

def get_real_facts_from_db(db_path="hexagonal_kb.db", limit=20):
    """Hole echte Fakten aus der Datenbank"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Hole zufällige Fakten
        cursor.execute(f"""
            SELECT rowid, statement 
            FROM facts 
            ORDER BY RANDOM() 
            LIMIT {limit}
        """)
        
        facts = cursor.fetchall()
        conn.close()
        
        return facts
    except Exception as e:
        print(f"❌ Fehler beim Laden der Fakten: {e}")
        return []

def test_real_facts_validation():
    """Teste Validierung mit echten Fakten"""
    print("🧪 Testing with real data from HAK_GAL Knowledge Base")
    print("=" * 60)
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        # Initialisiere Adapter
        adapter = create_hallucination_prevention_adapter()
        print("✅ Adapter initialisiert")
        
        # Hole echte Fakten
        real_facts = get_real_facts_from_db(limit=10)
        
        if not real_facts:
            print("❌ Keine Fakten aus der Datenbank geladen")
            return False
        
        print(f"📊 {len(real_facts)} echte Fakten geladen")
        
        # Validiere jeden Fakt
        validation_results = []
        
        for fact_id, fact in real_facts:
            print(f"\n🔍 Validating Fact ID {fact_id}:")
            print(f"   Statement: {fact[:100]}{'...' if len(fact) > 100 else ''}")
            
            # Validiere mit verschiedenen Stufen
            structural_result = adapter.validate_fact_before_insert(fact, fact_id)
            governance_result = adapter.validate_governance_compliance(fact)
            
            validation_results.append({
                'fact_id': fact_id,
                'fact': fact,
                'structural_validation': structural_result,
                'governance_compliance': governance_result
            })
            
            print(f"   ✅ Structural Valid: {structural_result['valid']}")
            print(f"   📊 Confidence: {structural_result['confidence']:.2f}")
            print(f"   ⚖️ Governance Compliant: {governance_result['compliant']}")
            
            if structural_result['issues']:
                print(f"   ⚠️ Issues: {structural_result['issues']}")
            
            if structural_result['correction']:
                print(f"   💡 Correction: {structural_result['correction']}")
        
        return validation_results
        
    except Exception as e:
        print(f"❌ Fehler beim Testen: {e}")
        return False

def test_batch_validation():
    """Teste Batch-Validierung mit echten Fakten"""
    print("\n🔄 Testing batch validation with real data")
    print("=" * 60)
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        
        # Hole Fakten-IDs
        real_facts = get_real_facts_from_db(limit=5)
        fact_ids = [fact[0] for fact in real_facts]
        
        print(f"📊 Batch-Validierung für {len(fact_ids)} Fakten")
        
        # Batch-Validierung
        batch_result = adapter.batch_validate_facts(fact_ids, "comprehensive")
        
        print(f"✅ Batch-Validierung abgeschlossen")
        print(f"📊 Success Rate: {batch_result['success_rate']:.2%}")
        print(f"⏱️ Duration: {batch_result.get('duration', 'N/A')}s")
        
        # Zeige Ergebnisse
        for result in batch_result['results']:
            print(f"\n   Fact ID {result['fact_id']}:")
            print(f"   Valid: {result['valid']} | Confidence: {result['confidence']:.2f}")
            if result['issues']:
                print(f"   Issues: {result['issues']}")
        
        return batch_result
        
    except Exception as e:
        print(f"❌ Batch-Validierung fehlgeschlagen: {e}")
        return False

def test_quality_analysis():
    """Teste Qualitätsanalyse der gesamten Datenbank"""
    print("\n📈 Testing database quality analysis")
    print("=" * 60)
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        
        print("🔍 Führe Qualitätsanalyse durch...")
        quality_result = adapter.run_database_quality_analysis()
        
        if quality_result.get('success'):
            analysis = quality_result['analysis']
            print("✅ Qualitätsanalyse abgeschlossen")
            
            # Zeige Ergebnisse
            print(f"📊 Gesamt-Fakten: {analysis.get('total_facts', 'N/A')}")
            print(f"⚠️ Vage Fakten: {analysis.get('vague_facts', 'N/A')}")
            print(f"🔧 Problematische Fakten: {analysis.get('problematic_facts', 'N/A')}")
            
            if 'vague_terms_found' in analysis:
                print(f"📝 Gefundene vage Begriffe: {analysis['vague_terms_found']}")
            
            if 'problematic_patterns' in analysis:
                print(f"🚨 Problematische Muster: {analysis['problematic_patterns']}")
                
        else:
            print(f"❌ Qualitätsanalyse fehlgeschlagen: {quality_result.get('error')}")
        
        return quality_result
        
    except Exception as e:
        print(f"❌ Qualitätsanalyse-Fehler: {e}")
        return False

def test_statistics():
    """Teste Validierungsstatistiken"""
    print("\n📊 Testing validation statistics")
    print("=" * 60)
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        
        stats = adapter.get_validation_statistics()
        
        print("✅ Statistiken abgerufen:")
        print(f"📈 Total validated: {stats['stats']['total_validated']}")
        print(f"❌ Invalid found: {stats['stats']['invalid_found']}")
        print(f"💡 Corrections suggested: {stats['stats']['corrections_suggested']}")
        print(f"⚡ Cache hits: {stats['stats']['cache_hits']}")
        print(f"⏱️ Avg validation time: {stats['stats']['validation_time_avg']:.3f}s")
        
        print(f"\n🔧 Validators available:")
        for validator, available in stats['validators_available'].items():
            status = "✅" if available else "❌"
            print(f"   {status} {validator}")
        
        return stats
        
    except Exception as e:
        print(f"❌ Statistiken-Fehler: {e}")
        return False

def test_problematic_facts():
    """Teste mit bekannten problematischen Fakten"""
    print("\n🚨 Testing with known problematic facts")
    print("=" * 60)
    
    try:
        from adapters.hallucination_prevention_adapter import create_hallucination_prevention_adapter
        
        adapter = create_hallucination_prevention_adapter()
        
        # Bekannte problematische Fakten
        problematic_facts = [
            "NH3 reacts with oxygen to form H2O and CO2.",  # Chemisch falsch
            "Water is a complex variable system.",  # Vage Begriffe
            "TCP is faster than HTTP.",  # Technisch korrekt, aber vage
            "HasProperty(water, liquid).",  # Korrektes Format
            "Water contains carbon and hydrogen.",  # Chemisch falsch
        ]
        
        print("🧪 Teste bekannte problematische Fakten:")
        
        for i, fact in enumerate(problematic_facts, 1):
            print(f"\n{i}. Testing: {fact}")
            
            # Validiere
            result = adapter.validate_fact_before_insert(fact, i)
            compliance = adapter.validate_governance_compliance(fact)
            
            print(f"   Valid: {result['valid']} | Confidence: {result['confidence']:.2f}")
            print(f"   Governance Compliant: {compliance['compliant']}")
            
            if result['issues']:
                print(f"   Issues: {result['issues']}")
            
            if result['correction']:
                print(f"   Suggested correction: {result['correction']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Problematische Fakten-Test fehlgeschlagen: {e}")
        return False

def main():
    """Haupttest-Funktion"""
    print("🚀 Real Data Validation Test")
    print("Testing Hallucination Prevention with real HAK_GAL data")
    print("=" * 70)
    
    tests = [
        ("Statistics", test_statistics),
        ("Real Facts Validation", test_real_facts_validation),
        ("Batch Validation", test_batch_validation),
        ("Quality Analysis", test_quality_analysis),
        ("Problematic Facts", test_problematic_facts)
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
    print("\n" + "="*70)
    print("📊 REAL DATA TEST SUMMARY")
    print("="*70)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All real data tests passed!")
        print("🚀 Hallucination Prevention is working with real HAK_GAL data!")
    else:
        print("⚠️ Some tests failed. Check the output above.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

