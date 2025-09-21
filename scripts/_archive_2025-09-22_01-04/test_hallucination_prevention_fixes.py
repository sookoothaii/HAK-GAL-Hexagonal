"""
Test der behobenen Hallucination Prevention Issues
==================================================
Testet die drei Fixes:
1. Batch Validation mit numerischen IDs
2. Quality Analysis ohne Mock-Daten
3. Predicate Classifier erkennt HasProperty
"""

import requests
import json
import sqlite3
from datetime import datetime

# API Configuration
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"
BASE_URL = "http://127.0.0.1:5002/api/hallucination-prevention"
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_batch_validation_fix():
    """Test 1: Batch Validation mit numerischen IDs"""
    print("\n" + "="*60)
    print("TEST 1: Batch Validation mit numerischen IDs")
    print("="*60)
    
    # Hole echte ROWIDs aus der Datenbank
    conn = sqlite3.connect('D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db')
    cursor = conn.cursor()
    
    # Suche HasProperty-Fakten mit ROWIDs
    cursor.execute("""
        SELECT rowid, statement 
        FROM facts 
        WHERE statement LIKE 'HasProperty(%'
        ORDER BY rowid
        LIMIT 5
    """)
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        print("FEHLER: Keine HasProperty-Fakten in der Datenbank gefunden!")
        return False
    
    # Extrahiere ROWIDs
    rowids = [r[0] for r in results]
    print(f"Gefundene ROWIDs: {rowids}")
    
    # Test 1a: Numerische IDs (sollte funktionieren)
    print("\nTest 1a: Batch Validation mit numerischen IDs...")
    response = requests.post(
        f"{BASE_URL}/validate-batch",
        headers=HEADERS,
        json={
            "fact_ids": rowids,
            "validation_level": "comprehensive"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        if 'batch_result' in data:
            br = data['batch_result']
            results_count = len(br.get('results', []))
            print(f"✅ ERFOLG: {results_count} Ergebnisse erhalten")
            if results_count > 0:
                # Zeige erstes Ergebnis
                first_result = br['results'][0]
                print(f"   Erstes Ergebnis:")
                print(f"   - Fact: {first_result['fact'][:80]}...")
                print(f"   - Valid: {first_result['valid']}")
                print(f"   - Category: {first_result.get('category', 'N/A')}")
                print(f"   - Confidence: {first_result['confidence']}")
                return True
            else:
                print("❌ FEHLER: Leeres results Array!")
                return False
        else:
            print("❌ FEHLER: Keine batch_result in Response")
            return False
    else:
        print(f"❌ FEHLER: HTTP {response.status_code}")
        return False

def test_quality_analysis_fix():
    """Test 2: Quality Analysis ohne Mock-Daten"""
    print("\n" + "="*60)
    print("TEST 2: Quality Analysis mit echten Daten")
    print("="*60)
    
    response = requests.post(
        f"{BASE_URL}/quality-analysis",
        headers=HEADERS,
        json={}
    )
    
    if response.status_code == 200:
        data = response.json()
        
        # Handle nested response structure
        analysis = None
        if 'quality_analysis' in data and 'analysis' in data['quality_analysis']:
            analysis = data['quality_analysis']['analysis']
        elif 'analysis' in data:
            analysis = data['analysis']
        
        if analysis and isinstance(analysis, dict):
            # Prüfe auf Mock-Daten Indikator
            has_mock_flag = analysis.get('mock_data', True)
            total_facts = analysis.get('total_facts', 0)
            hasprop_count = analysis.get('hasproperty_count', 0)
            
            print(f"Total Facts: {total_facts}")
            print(f"HasProperty Count: {hasprop_count}")
            print(f"Mock Data Flag: {has_mock_flag}")
            print(f"Data Source: {analysis.get('data_source', 'unknown')}")
            
            # Check: Keine Mock-Daten (29.499 HasProperty)
            if hasprop_count == 29499:
                print("❌ FEHLER: Mock-Daten erkannt (29.499 HasProperty)!")
                return False
            elif has_mock_flag == False and analysis.get('data_source') == 'real_database_analysis':
                print("✅ ERFOLG: Echte Datenbankanalyse ohne Mock-Daten")
                
                # Zeige Prädikat-Verteilung
                if 'predicates' in analysis:
                    print("\nPrädikat-Verteilung:")
                    for pred, count in analysis['predicates'].items():
                        print(f"   {pred}: {count}")
                
                # Zeige Domain-Verteilung
                if 'domain_distribution' in analysis:
                    print("\nDomain-Verteilung:")
                    for domain, count in analysis['domain_distribution'].items():
                        if count > 0:
                            print(f"   {domain}: {count}")
                
                return True
            else:
                print("⚠️  WARNUNG: Unklarer Status der Daten")
                return False
        else:
            print("❌ FEHLER: Analyse fehlgeschlagen oder unerwartete Struktur")
            print(f"Response: {json.dumps(data, indent=2)}")
            return False
    else:
        print(f"❌ FEHLER: HTTP {response.status_code}")
        return False

def test_predicate_classifier_fix():
    """Test 3: Predicate Classifier erkennt HasProperty"""
    print("\n" + "="*60)
    print("TEST 3: Predicate Classifier Funktionalität")
    print("="*60)
    
    # Test-Fakten mit verschiedenen Prädikaten
    test_facts = [
        "HasProperty(water, liquid).",
        "ConsistsOf(water, H2O).",
        "Uses(computer, electricity).",
        "IsTypeOf(python, programming_language).",
        "HasPart(car, engine)."
    ]
    
    correctly_classified = 0
    
    for fact in test_facts:
        # Erwartetes Prädikat extrahieren
        expected_predicate = fact.split('(')[0]
        
        # Single Validation
        response = requests.post(
            f"{BASE_URL}/validate",
            headers=HEADERS,
            json={"fact": fact, "validation_level": "comprehensive"}
        )
        
        if response.status_code == 200:
            result = response.json()
            if 'validation_result' in result:
                category = result['validation_result'].get('category', 'Unknown')
                
                print(f"\nFact: {fact}")
                print(f"   Erwartetes Prädikat: {expected_predicate}")
                print(f"   Erkannte Kategorie: {category}")
                
                if category == expected_predicate:
                    print(f"   ✅ Korrekt klassifiziert!")
                    correctly_classified += 1
                else:
                    print(f"   ❌ Falsch klassifiziert!")
    
    success_rate = correctly_classified / len(test_facts)
    print(f"\n{'-'*40}")
    print(f"Erfolgsrate: {correctly_classified}/{len(test_facts)} ({success_rate*100:.1f}%)")
    
    if success_rate >= 0.8:  # 80% oder besser
        print("✅ ERFOLG: Predicate Classifier funktioniert!")
        return True
    else:
        print("❌ FEHLER: Predicate Classifier hat Probleme")
        return False

def test_statistics_endpoint():
    """Zusätzlicher Test: Statistics Endpoint"""
    print("\n" + "="*60)
    print("BONUS TEST: Statistics Endpoint")
    print("="*60)
    
    response = requests.get(
        f"{BASE_URL}/statistics",
        headers=HEADERS
    )
    
    if response.status_code == 200:
        stats = response.json()
        
        # Zeige Statistiken
        if 'stats' in stats:
            print("Validierungs-Statistiken:")
            for key, value in stats['stats'].items():
                print(f"   {key}: {value}")
        
        # Zeige Prädikat-Verteilung wenn vorhanden
        if 'predicate_distribution' in stats:
            print("\nPrädikat-Verteilung im Cache:")
            for pred, count in stats['predicate_distribution'].items():
                print(f"   {pred}: {count}")
        
        return True
    else:
        print(f"❌ FEHLER: HTTP {response.status_code}")
        return False

def main():
    """Führe alle Tests durch"""
    print("\n" + "="*80)
    print("HALLUCINATION PREVENTION FIX VERIFICATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print("="*80)
    
    # Prüfe ob API läuft
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS)
        if response.status_code != 200:
            print("❌ API nicht erreichbar! Bitte starten Sie den Server.")
            return
    except Exception as e:
        print(f"❌ Verbindungsfehler: {e}")
        return
    
    print("✅ API ist erreichbar\n")
    
    # Führe Tests durch
    results = {
        "Batch Validation": test_batch_validation_fix(),
        "Quality Analysis": test_quality_analysis_fix(),
        "Predicate Classifier": test_predicate_classifier_fix(),
        "Statistics": test_statistics_endpoint()
    }
    
    # Zusammenfassung
    print("\n" + "="*80)
    print("ZUSAMMENFASSUNG")
    print("="*80)
    
    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:.<40} {status}")
    
    print(f"\nGesamtergebnis: {passed_tests}/{total_tests} Tests bestanden ({passed_tests/total_tests*100:.0f}%)")
    
    if passed_tests == total_tests:
        print("\n🎉 ALLE FIXES ERFOLGREICH VERIFIZIERT! 🎉")
    else:
        print("\n⚠️  Einige Fixes benötigen weitere Arbeit.")

if __name__ == "__main__":
    main()
