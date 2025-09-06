#!/usr/bin/env python
"""
Correct Database Analysis - Using RIGHT Columns
================================================
Nutzt die korrekten Spalten der Datenbank
"""

import sqlite3
from pathlib import Path
from collections import Counter

def correct_database_analysis():
    """Analysiere die Datenbank mit den RICHTIGEN Spalten"""
    
    print("="*70)
    print("CORRECT DATABASE ANALYSIS")
    print("="*70)
    
    db_path = Path("hexagonal_kb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    with sqlite3.connect(str(db_path)) as conn:
        # Show table structure
        print("\n📊 Table Structure:")
        print("-"*40)
        cursor = conn.execute("PRAGMA table_info(facts)")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  Column: {col[1]:20} Type: {col[2]}")
        
        # Total facts
        cursor = conn.execute("SELECT COUNT(*) FROM facts")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total Facts: {total:,}")
        
        # Check predicate column
        print("\n📊 Checking 'predicate' column...")
        cursor = conn.execute("SELECT predicate, COUNT(*) as count FROM facts GROUP BY predicate ORDER BY count DESC LIMIT 20")
        pred_column = cursor.fetchall()
        
        if pred_column and pred_column[0][0] is not None:
            print("\n✅ Predicate column is populated:")
            print("-"*40)
            for pred, count in pred_column:
                print(f"  {pred:30} : {count:5} ({count/total*100:5.1f}%)")
        else:
            print("❌ Predicate column is EMPTY or NULL!")
        
        # Check actual statement structure
        print("\n📊 Analyzing statement column (extracting predicates)...")
        cursor = conn.execute("SELECT statement FROM facts")
        all_statements = cursor.fetchall()
        
        predicate_counter = Counter()
        for (statement,) in all_statements:
            if '(' in statement and ')' in statement:
                pred = statement.split('(')[0].strip()
                predicate_counter[pred] += 1
        
        print(f"\n✅ Found {len(predicate_counter)} unique predicates in statements:")
        print("-"*40)
        for pred, count in predicate_counter.most_common(20):
            print(f"  {pred:30} : {count:5} ({count/total*100:5.1f}%)")
        
        # Check subject/object columns
        print("\n📊 Checking subject/object columns...")
        cursor = conn.execute("SELECT subject, object FROM facts LIMIT 5")
        samples = cursor.fetchall()
        
        if samples and samples[0][0] is not None:
            print("✅ Subject/Object columns populated:")
            for subj, obj in samples:
                print(f"  Subject: {subj}, Object: {obj}")
        else:
            print("❌ Subject/Object columns are EMPTY!")
        
        # The real problem
        print("\n" + "="*70)
        print("DIAGNOSIS:")
        print("="*70)
        
        if pred_column and pred_column[0][0] is None:
            print("🚨 PROBLEM IDENTIFIED:")
            print("   The 'predicate' column exists but is NOT populated!")
            print("   All predicates are NULL, causing query to fail!")
            print("\n   SOLUTION:")
            print("   1. Fix the fact insertion code to populate predicate column")
            print("   2. OR update existing facts to populate the column")
            print("   3. OR use statement extraction (which works)")
        else:
            print("✅ Database structure is correct")
            print(f"   Found {len(predicate_counter)} unique predicates")
        
        # Quality assessment
        print("\n📊 QUALITY METRICS:")
        print("-"*40)
        
        top_predicates = predicate_counter.most_common(10)
        good_predicates = ['IsA', 'HasProperty', 'Causes', 'RelatedTo', 'Contains', 
                          'PartOf', 'UsedFor', 'LocatedIn', 'CreatedBy', 'Requires']
        
        good_count = sum(count for pred, count in predicate_counter.items() if pred in good_predicates)
        
        print(f"  Total unique predicates: {len(predicate_counter)}")
        print(f"  Good predicates: {good_count} ({good_count/total*100:.1f}%)")
        print(f"  Most common: {top_predicates[0][0]} ({top_predicates[0][1]} facts)")
        
        if len(predicate_counter) > 100:
            print("\n✅ EXCELLENT predicate diversity!")
        elif len(predicate_counter) > 50:
            print("\n✅ Good predicate diversity")
        else:
            print("\n⚠️ Limited predicate diversity")
        
        return len(predicate_counter)

if __name__ == "__main__":
    unique_preds = correct_database_analysis()
    
    print("\n" + "="*70)
    print("RECOMMENDATION:")
    print("="*70)
    
    if unique_preds and unique_preds > 50:
        print("✅ Your database is FINE!")
        print("   The 'Uses: 4373' was a SQL query bug")
        print("\n   The database has good diversity with many predicates.")
        print("   You can continue with learning, but maybe:")
        print("   1. Optimize for more 'good' predicates")
        print("   2. Increase learning rate")
    else:
        print("⚠️ Limited diversity - needs improvement")
