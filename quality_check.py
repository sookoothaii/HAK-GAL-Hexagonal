#!/usr/bin/env python3
"""
SYSTEMATISCHE QUALITÄTSPRÜFUNG DER KNOWLEDGE BASE
Zieht stratifizierte Stichproben und validiert sie
"""

import sqlite3
import json
import random
from collections import defaultdict
from pathlib import Path

def analyze_database_quality():
    conn = sqlite3.connect('hexagonal_kb.db')
    cursor = conn.cursor()
    
    print("SYSTEMATISCHE QUALITÄTSPRÜFUNG DER KNOWLEDGE BASE")
    print("="*60)
    
    # 1. GESAMTSTATISTIK
    cursor.execute("SELECT COUNT(*) FROM facts")
    total = cursor.fetchone()[0]
    print(f"Gesamtanzahl Fakten: {total:,}")
    
    # 2. PRÄDIKAT-ANALYSE
    cursor.execute("""
        SELECT 
            CASE 
                WHEN statement LIKE 'HasProperty(%' THEN 'HasProperty'
                WHEN statement LIKE 'ConsistsOf(%' THEN 'ConsistsOf'
                WHEN statement LIKE 'Uses(%' THEN 'Uses'
                WHEN statement LIKE 'IsTypeOf(%' THEN 'IsTypeOf'
                WHEN statement LIKE 'HasPart(%' THEN 'HasPart'
                WHEN statement LIKE 'HasPurpose(%' THEN 'HasPurpose'
                ELSE 'Other'
            END as predicate,
            COUNT(*) as count
        FROM facts
        GROUP BY predicate
        ORDER BY count DESC
    """)
    
    print("\nPRÄDIKAT-VERTEILUNG:")
    print("-"*40)
    predicates = cursor.fetchall()
    for pred, count in predicates:
        percent = count/total*100
        bar = "█" * int(percent/2)
        print(f"{pred:15} {count:6,} ({percent:5.1f}%) {bar}")
    
    # 3. KRITISCHE ANALYSE: HasProperty
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE 'HasProperty(%'
        ORDER BY RANDOM() LIMIT 20
    """)
    hasprop_samples = [r[0] for r in cursor.fetchall()]
    
    print("\n⚠️ HASPR0PERTY STICHPROBE (20 von 29.499):")
    print("-"*40)
    suspicious = 0
    for i, fact in enumerate(hasprop_samples[:10], 1):
        # Prüfe auf vage/generische Properties
        vague_terms = ['dynamic', 'static', 'complex', 'simple', 'variable', 
                       'optimal', 'critical', 'essential', 'fundamental', 'reactive']
        is_vague = any(term in fact.lower() for term in vague_terms)
        
        if is_vague:
            print(f"❌ {fact}")
            suspicious += 1
        else:
            print(f"✓  {fact}")
    
    # 4. WISSENSCHAFTLICHE FAKTEN PRÜFEN
    samples = {}
    
    # Chemie
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%ConsistsOf%'
        AND (statement LIKE '%H2O%' OR statement LIKE '%CO2%' 
             OR statement LIKE '%NH3%' OR statement LIKE '%CH4%')
        ORDER BY RANDOM() LIMIT 10
    """)
    samples['Chemie'] = [r[0] for r in cursor.fetchall()]
    
    # Informatik
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%TCP%' OR statement LIKE '%HTTP%'
        OR statement LIKE '%algorithm%' OR statement LIKE '%hash%'
        ORDER BY RANDOM() LIMIT 10
    """)
    samples['Informatik'] = [r[0] for r in cursor.fetchall()]
    
    # Biologie
    cursor.execute("""
        SELECT statement FROM facts 
        WHERE statement LIKE '%cell%' OR statement LIKE '%DNA%'
        OR statement LIKE '%protein%' OR statement LIKE '%virus%'
        ORDER BY RANDOM() LIMIT 10
    """)
    samples['Biologie'] = [r[0] for r in cursor.fetchall()]
    
    print("\nWISSENSCHAFTLICHE STICHPROBEN:")
    print("-"*40)
    
    validation_needed = []
    for category, facts in samples.items():
        print(f"\n{category} ({len(facts)} Fakten):")
        for fact in facts[:3]:
            print(f"  • {fact}")
            validation_needed.append(fact)
    
    # 5. SPEICHERE für DeepSeek-Validierung
    validation_batch = {
        'hasProperty_samples': hasprop_samples,
        'scientific_samples': validation_needed,
        'total_for_validation': len(hasprop_samples) + len(validation_needed)
    }
    
    with open('quality_check_batch.json', 'w') as f:
        json.dump(validation_batch, f, indent=2)
    
    # 6. EMPFEHLUNGEN
    print("\n" + "="*60)
    print("QUALITÄTSBEWERTUNG:")
    print("-"*40)
    
    hasprop_percent = next(c for p, c in predicates if p == 'HasProperty') / total * 100
    
    if hasprop_percent > 80:
        print(f"❗ KRITISCH: {hasprop_percent:.1f}% sind HasProperty-Fakten!")
        print("   → Viele generische/vage Eigenschaften")
        print("   → SimpleFactGenerator-Artefakte")
    
    if suspicious > 5:
        print(f"\n⚠️ {suspicious}/10 HasProperty-Stichproben sind vage/generisch")
        print("   → Weitere Bereinigung notwendig")
    
    print("\nEMPFOHLENE AKTIONEN:")
    print("1. Alle HasProperty mit vagen Begriffen löschen")
    print("2. quality_check_batch.json mit DeepSeek validieren")
    print("3. Fokus auf wissenschaftlich präzise Fakten")
    
    conn.close()
    return validation_batch

if __name__ == "__main__":
    batch = analyze_database_quality()
    
    print("\n" + "="*60)
    print("NÄCHSTER SCHRITT:")
    print(f"python deepseek_reasoning_validator.py --input quality_check_batch.json")
    print(f"\nOder direkte Bereinigung:")
    print(f"python remove_vague_hasproperty.py")
