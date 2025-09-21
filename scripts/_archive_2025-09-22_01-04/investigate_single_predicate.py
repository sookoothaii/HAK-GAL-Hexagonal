#!/usr/bin/env python
"""
Investigate Single Predicate Problem
=====================================
Warum haben ALLE Facts das gleiche Prädikat "Uses"?
"""

import sqlite3
from pathlib import Path
from collections import Counter

def investigate_single_predicate():
    """Untersuche warum alle Facts 'Uses' als Prädikat haben"""
    
    print("="*70)
    print("🔍 INVESTIGATING SINGLE PREDICATE ANOMALY")
    print("="*70)
    
    db_path = Path("hexagonal_kb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    with sqlite3.connect(str(db_path)) as conn:
        # Get total count
        cursor = conn.execute("SELECT COUNT(*) FROM facts")
        total = cursor.fetchone()[0]
        print(f"\n📊 Total Facts: {total:,}")
        
        # Get predicate distribution
        print("\n📊 Checking predicate distribution...")
        cursor = conn.execute("""
            SELECT 
                CASE 
                    WHEN instr(statement, '(') > 0 
                    THEN substr(statement, 1, instr(statement, '(') - 1)
                    ELSE statement
                END as predicate,
                COUNT(*) as count
            FROM facts 
            GROUP BY predicate
            ORDER BY count DESC
            LIMIT 20
        """)
        
        predicates = cursor.fetchall()
        
        print("\nPredicate Distribution:")
        print("-"*40)
        for pred, count in predicates:
            percentage = (count / total * 100)
            print(f"  {pred:30} : {count:5} ({percentage:5.1f}%)")
        
        # Check if it's really "Uses" or display error
        if len(predicates) == 1 and predicates[0][0] == 'Uses':
            print("\n❌ CRITICAL PROBLEM: All facts have 'Uses' predicate!")
            print("   This is NOT normal!")
        
        # Get sample facts
        print("\n📊 Sample Facts (first 20):")
        print("-"*40)
        cursor = conn.execute("SELECT rowid, statement FROM facts ORDER BY rowid DESC LIMIT 20")
        samples = cursor.fetchall()
        
        for rowid, statement in samples:
            # Show full statement to understand structure
            if len(statement) > 100:
                print(f"  [{rowid}] {statement[:100]}...")
            else:
                print(f"  [{rowid}] {statement}")
        
        # Check actual structure
        print("\n📊 Checking actual fact structure...")
        cursor = conn.execute("SELECT statement FROM facts LIMIT 100")
        facts = cursor.fetchall()
        
        # Analyze structure
        has_parentheses = 0
        has_period = 0
        predicates_found = Counter()
        
        for (statement,) in facts:
            if '(' in statement and ')' in statement:
                has_parentheses += 1
                # Extract actual predicate
                pred = statement[:statement.index('(')]
                predicates_found[pred] += 1
            if statement.endswith('.'):
                has_period += 1
        
        print(f"\nStructure Analysis (of 100 facts):")
        print(f"  Has parentheses: {has_parentheses}")
        print(f"  Ends with period: {has_period}")
        print(f"  Unique predicates found: {len(predicates_found)}")
        
        if predicates_found:
            print("\nActual Predicates Found:")
            for pred, count in predicates_found.most_common(10):
                print(f"    {pred}: {count}")
        
        # Check if database might be corrupted
        print("\n📊 Database Integrity Check...")
        cursor = conn.execute("PRAGMA integrity_check")
        integrity = cursor.fetchone()[0]
        print(f"  Integrity: {integrity}")
        
        # Check table structure
        cursor = conn.execute("PRAGMA table_info(facts)")
        columns = cursor.fetchall()
        print("\n  Table columns:")
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
        
        # Get distinct predicates properly
        print("\n📊 Getting DISTINCT predicates...")
        cursor = conn.execute("""
            SELECT DISTINCT
                CASE 
                    WHEN instr(statement, '(') > 0 
                    THEN substr(statement, 1, instr(statement, '(') - 1)
                    ELSE 'NO_PREDICATE'
                END as predicate
            FROM facts 
            LIMIT 50
        """)
        
        distinct_preds = cursor.fetchall()
        print(f"\nFound {len(distinct_preds)} distinct predicates:")
        for (pred,) in distinct_preds[:20]:
            print(f"  - {pred}")
        
        # Diagnosis
        print("\n" + "="*70)
        print("DIAGNOSIS:")
        print("="*70)
        
        if len(distinct_preds) == 1:
            print("🚨 CRITICAL BUG: Database query is returning wrong results!")
            print("   The SQL query might be broken or the data is corrupted.")
            print("\n   RECOMMENDED ACTIONS:")
            print("   1. Restart the backend")
            print("   2. Check the actual database file with SQLite browser")
            print("   3. The display bug might be in the query interface")
        else:
            print("✅ Database has diverse predicates")
            print("   The 'Uses: 4373' display was likely a query error")

if __name__ == "__main__":
    investigate_single_predicate()
