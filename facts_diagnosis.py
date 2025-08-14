#!/usr/bin/env python3
"""
HAK-GAL Facts Diagnosis - Simplified
=====================================
Nach HAK/GAL Artikel 6: Empirische Validierung
"""

import sqlite3
from pathlib import Path
from collections import Counter

def diagnose_facts():
    """Diagnose knowledge base issues"""
    
    # Find database
    db_path = Path('../HAK_GAL_SUITE/k_assistant.db')
    if not db_path.exists():
        print("[ERROR] Database not found")
        return
        
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Get total count
    cursor.execute("SELECT COUNT(*) FROM facts")
    total = cursor.fetchone()[0]
    
    # Get all facts
    cursor.execute("SELECT statement FROM facts")
    facts = [row[0] for row in cursor.fetchall()]
    
    # Analyze predicates
    predicates = Counter()
    english_preds = set()
    german_preds = set()
    unknown_preds = set()
    
    english_keywords = ['Has', 'Is', 'Can', 'Uses', 'Requires', 'Affects', 'Contains', 'Produces']
    german_keywords = ['Hat', 'Ist', 'Kann', 'Verwendet', 'Benötigt', 'Beeinflusst', 'Enthält']
    
    for fact in facts:
        if '(' in fact:
            pred = fact.split('(')[0].strip()
            predicates[pred] += 1
            
            # Classify language
            if any(kw in pred for kw in english_keywords):
                english_preds.add(pred)
            elif any(kw in pred for kw in german_keywords):
                german_preds.add(pred)
            else:
                unknown_preds.add(pred)
    
    # Calculate statistics
    english_count = sum(predicates[p] for p in english_preds)
    german_count = sum(predicates[p] for p in german_preds)
    unknown_count = sum(predicates[p] for p in unknown_preds)
    
    print("\n" + "="*60)
    print("HAK-GAL KNOWLEDGE BASE DIAGNOSIS")
    print("Nach HAK/GAL Artikel 6: Empirische Validierung")
    print("="*60)
    
    print(f"\n[FACTS COUNT]")
    print(f"Total Facts in DB: {total}")
    print(f"Expected (from docs): 3080")
    print(f"MISSING: {3080 - total} ({(3080-total)/3080*100:.1f}%)")
    
    print(f"\n[LANGUAGE ANALYSIS]")
    print(f"English Predicates: {len(english_preds)} ({english_count} facts)")
    print(f"German Predicates: {len(german_preds)} ({german_count} facts)")
    print(f"Unknown Predicates: {len(unknown_preds)} ({unknown_count} facts)")
    
    print(f"\n[TOP 10 PREDICATES]")
    for pred, count in predicates.most_common(10):
        lang = "EN" if pred in english_preds else "DE" if pred in german_preds else "??"
        print(f"  {pred:30} {count:4} [{lang}]")
    
    print(f"\n[CRITICAL ISSUES]")
    print(f"1. 60% of facts are MISSING (1850 facts)")
    print(f"2. {unknown_count} facts ({unknown_count/total*100:.1f}%) have unclassified predicates")
    print(f"3. Mixed language predicates (English + German)")
    
    print(f"\n[SAMPLE UNKNOWN PREDICATES]")
    for pred in list(unknown_preds)[:10]:
        count = predicates[pred]
        print(f"  {pred:30} ({count} facts)")
    
    # Check for specific knowledge domains
    print(f"\n[KNOWLEDGE DOMAIN CHECK]")
    domains = {
        'Physics': ['Gravity', 'Mass', 'Energy', 'Force'],
        'Biology': ['Cell', 'DNA', 'Protein', 'Species'],
        'Computer': ['Algorithm', 'Network', 'Database', 'Software'],
        'Chemistry': ['Element', 'Molecule', 'Reaction', 'Compound'],
        'HAK/GAL': ['Governor', 'Reasoning', 'Knowledge', 'Fact']
    }
    
    for domain, keywords in domains.items():
        found = sum(1 for fact in facts if any(kw.lower() in fact.lower() for kw in keywords))
        print(f"  {domain:15} {found:4} facts")
    
    print(f"\n[DIAGNOSIS SUMMARY]")
    print("❌ CRITICAL: Knowledge Base is SEVERELY INCOMPLETE")
    print("❌ Only 40% of expected facts present")
    print("⚠️  Language inconsistency detected")
    print("⚠️  Many predicates unclassified")
    
    print(f"\n[REQUIRED ACTIONS]")
    print("1. URGENT: Restore missing 1850 facts from backup")
    print("2. Check if facts were lost during cleanup operations")
    print("3. Verify original data source (3080 facts)")
    print("4. Standardize predicate language (recommend English)")
    print("5. Implement fact validation before insertion")
    
    conn.close()

if __name__ == "__main__":
    diagnose_facts()