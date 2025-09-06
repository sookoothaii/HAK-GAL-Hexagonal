#!/usr/bin/env python
"""
Simple Database Check - Direct SQL
===================================
Direkter Check ohne komplexe Queries
"""

import sqlite3
from pathlib import Path

def simple_db_check():
    """Einfacher direkter Datenbank-Check"""
    
    print("="*70)
    print("SIMPLE DATABASE CHECK")
    print("="*70)
    
    db_path = Path("hexagonal_kb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    with sqlite3.connect(str(db_path)) as conn:
        # Just get first 30 facts directly
        print("\n📊 First 30 Facts (DIRECT from database):")
        print("-"*70)
        
        cursor = conn.execute("SELECT statement FROM facts LIMIT 30")
        facts = cursor.fetchall()
        
        for i, (statement,) in enumerate(facts, 1):
            # Show the RAW fact
            if len(statement) > 120:
                print(f"{i:3}. {statement[:120]}...")
            else:
                print(f"{i:3}. {statement}")
        
        # Count total
        cursor = conn.execute("SELECT COUNT(*) FROM facts")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total Facts: {total:,}")
        
        # Get last 10 facts
        print("\n📊 Last 10 Facts (most recent):")
        print("-"*70)
        
        cursor = conn.execute("SELECT statement FROM facts ORDER BY rowid DESC LIMIT 10")
        facts = cursor.fetchall()
        
        for i, (statement,) in enumerate(facts, 1):
            if len(statement) > 120:
                print(f"{i:3}. {statement[:120]}...")
            else:
                print(f"{i:3}. {statement}")
        
        # Manual predicate count
        print("\n📊 Manually counting predicates...")
        cursor = conn.execute("SELECT statement FROM facts")
        all_facts = cursor.fetchall()
        
        predicate_count = {}
        no_predicate = 0
        
        for (statement,) in all_facts:
            if '(' in statement:
                pred = statement.split('(')[0]
                predicate_count[pred] = predicate_count.get(pred, 0) + 1
            else:
                no_predicate += 1
        
        print(f"\nFound {len(predicate_count)} different predicates:")
        print("-"*40)
        
        # Sort by count
        sorted_preds = sorted(predicate_count.items(), key=lambda x: x[1], reverse=True)
        
        for pred, count in sorted_preds[:20]:
            print(f"  {pred:30} : {count:5}")
        
        if no_predicate > 0:
            print(f"\n  Facts without predicates: {no_predicate}")
        
        # Summary
        print("\n" + "="*70)
        print("SUMMARY:")
        print("="*70)
        print(f"Total Facts: {total:,}")
        print(f"Unique Predicates: {len(predicate_count)}")
        print(f"Most Common: {sorted_preds[0][0] if sorted_preds else 'None'} ({sorted_preds[0][1] if sorted_preds else 0} facts)")
        
        if len(predicate_count) < 5:
            print("\n⚠️ WARNING: Very few unique predicates!")
            print("   The learning engines might be stuck in a loop!")
        elif len(predicate_count) > 50:
            print("\n✅ Good variety of predicates")
        else:
            print("\n📊 Moderate predicate diversity")

if __name__ == "__main__":
    simple_db_check()
