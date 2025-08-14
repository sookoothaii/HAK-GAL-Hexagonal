#!/usr/bin/env python
"""
Check SQLite Database Facts Count
==================================
Verify actual facts in SQLite database
"""

import sqlite3
from pathlib import Path

def check_sqlite_facts():
    """Check facts in all SQLite databases"""
    
    databases = [
        'k_assistant.db',
        'k_assistant_dev.db',
        'k_assistant_backup.db'
    ]
    
    for db_name in databases:
        db_path = Path(__file__).parent / db_name
        if not db_path.exists():
            print(f"❌ {db_name}: Not found")
            continue
            
        try:
            with sqlite3.connect(str(db_path)) as conn:
                # Check if facts table exists
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts'")
                if not cursor.fetchone():
                    print(f"⚠️  {db_name}: No 'facts' table")
                    continue
                
                # Count facts
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                
                # Get sample facts
                cursor = conn.execute("SELECT statement FROM facts LIMIT 5")
                samples = [row[0] for row in cursor]
                
                # Get unique predicates
                cursor = conn.execute("""
                    SELECT DISTINCT substr(statement, 1, instr(statement, '(') - 1) as predicate
                    FROM facts 
                    WHERE instr(statement, '(') > 0
                    LIMIT 10
                """)
                predicates = [row[0] for row in cursor if row[0]]
                
                print(f"\n✅ {db_name}:")
                print(f"   Facts: {count}")
                print(f"   Sample facts:")
                for s in samples[:3]:
                    print(f"     - {s[:80]}...")
                print(f"   Sample predicates: {', '.join(predicates[:5])}")
                
        except Exception as e:
            print(f"❌ {db_name}: Error - {e}")
    
    print("\n" + "="*60)
    print("Recommendation: Use the database with the most facts")
    print("="*60)

if __name__ == '__main__':
    check_sqlite_facts()
