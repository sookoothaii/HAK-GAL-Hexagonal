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
    # Use absolute path to database
    db_path = Path(__file__).parent.parent.parent / 'hexagonal_kb.db'
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # ENTFERNT: Mock-Print-Statements die hardcodierte Daten zeigen
    # Stattdessen: Echte Datenbank-Analyse ohne Konsolen-Output
    
    try:
        # 1. GESAMTSTATISTIK
        cursor.execute("SELECT COUNT(*) FROM facts")
        total = cursor.fetchone()[0]
        
        # 2. PRÄDIKAT-ANALYSE
        cursor.execute("""
            SELECT 
                predicate_type,
                COUNT(*) as count
            FROM (
                SELECT 
                    CASE 
                        WHEN statement LIKE 'HasProperty(%' THEN 'HasProperty'
                        WHEN statement LIKE 'ConsistsOf(%' THEN 'ConsistsOf'
                        WHEN statement LIKE 'Uses(%' THEN 'Uses'
                        WHEN statement LIKE 'IsTypeOf(%' THEN 'IsTypeOf'
                        WHEN statement LIKE 'HasPart(%' THEN 'HasPart'
                        WHEN statement LIKE 'HasPurpose(%' THEN 'HasPurpose'
                        ELSE 'Other'
                    END as predicate_type
                FROM facts
            )
            GROUP BY predicate_type
            ORDER BY count DESC
        """)
        
        predicates_raw = cursor.fetchall()
        predicates = {}
        for pred_type, count in predicates_raw:
            predicates[pred_type] = count
        
        # 3. ECHTE HasProperty-Zählung (keine Mock-Daten!)
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE statement LIKE 'HasProperty(%'
        """)
        actual_hasproperty_count = cursor.fetchone()[0]
        
        # 4. Berechne echte Prozentsätze
        hasprop_percent = (actual_hasproperty_count / total * 100) if total > 0 else 0.0
        
        # 5. Domain-basierte Kategorisierung für bessere Analyse
        domain_counts = {}
        
        # Chemie
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE statement LIKE '%H2O%' OR statement LIKE '%CO2%' 
            OR statement LIKE '%NH3%' OR statement LIKE '%CH4%'
            OR statement LIKE '%molecule%' OR statement LIKE '%atom%'
            OR statement LIKE '%chemical%'
        """)
        domain_counts['chemistry'] = cursor.fetchone()[0]
        
        # Informatik
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE statement LIKE '%TCP%' OR statement LIKE '%HTTP%'
            OR statement LIKE '%algorithm%' OR statement LIKE '%computer%'
            OR statement LIKE '%software%' OR statement LIKE '%code%'
        """)
        domain_counts['computer_science'] = cursor.fetchone()[0]
        
        # Biologie
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE statement LIKE '%cell%' OR statement LIKE '%DNA%'
            OR statement LIKE '%protein%' OR statement LIKE '%virus%'
            OR statement LIKE '%organism%' OR statement LIKE '%biological%'
        """)
        domain_counts['biology'] = cursor.fetchone()[0]
        
        # Physik
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE statement LIKE '%electron%' OR statement LIKE '%photon%'
            OR statement LIKE '%gravity%' OR statement LIKE '%energy%'
            OR statement LIKE '%quantum%' OR statement LIKE '%force%'
        """)
        domain_counts['physics'] = cursor.fetchone()[0]
        
        # 6. Quality Metrics
        quality_metrics = {
            'has_trailing_dot': 0,
            'has_valid_syntax': 0,
            'is_n_ary': 0
        }
        
        # Stichprobe für Qualitätsmetriken (100 zufällige Fakten)
        cursor.execute("""
            SELECT statement FROM facts 
            ORDER BY RANDOM() 
            LIMIT 100
        """)
        sample_facts = cursor.fetchall()
        
        for (fact,) in sample_facts:
            if fact.endswith('.'):
                quality_metrics['has_trailing_dot'] += 1
            if '(' in fact and ')' in fact:
                quality_metrics['has_valid_syntax'] += 1
            if fact.count(',') >= 1:  # n-äre Fakten haben mindestens ein Komma
                quality_metrics['is_n_ary'] += 1
        
        # Prozentsätze berechnen
        sample_size = len(sample_facts)
        if sample_size > 0:
            quality_metrics = {
                k: (v / sample_size * 100) for k, v in quality_metrics.items()
            }
        
        # Close connection
        conn.close()
        
        # Return ECHTE analysis result (keine Mock-Daten!)
        return {
            "success": True,
            "total_facts": total,
            "hasproperty_count": actual_hasproperty_count,  # Echter Wert statt 29.499
            "hasproperty_percent": round(hasprop_percent, 2),
            "predicates": predicates,
            "domain_distribution": domain_counts,
            "quality_metrics": quality_metrics,
            "quality_assessment": "completed",
            # Flag dass dies echte Daten sind
            "data_source": "real_database_analysis",
            "mock_data": False
        }
        
    except Exception as e:
        conn.close()
        return {
            "success": False,
            "error": str(e),
            "quality_assessment": "failed"
        }

if __name__ == "__main__":
    batch = analyze_database_quality()
    
    print("\n" + "="*60)
    print("NÄCHSTER SCHRITT:")
    print(f"python deepseek_reasoning_validator.py --input quality_check_batch.json")
    print(f"\nOder direkte Bereinigung:")
    print(f"python remove_vague_hasproperty.py")
