#!/usr/bin/env python
"""
Import JSONL Facts into SQLite Database
========================================
Fixes the empty database problem!
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime

def import_jsonl_to_sqlite():
    """Import all JSONL facts into SQLite DB"""
    
    # Paths
    jsonl_path = Path(__file__).parent / 'data' / 'k_assistant.kb.jsonl'
    sqlite_path = Path(__file__).parent / 'k_assistant.db'
    
    print("="*60)
    print("🔄 IMPORTING JSONL FACTS INTO SQLITE")
    print("="*60)
    
    # Check JSONL exists
    if not jsonl_path.exists():
        print(f"❌ JSONL not found: {jsonl_path}")
        return False
    
    # Load JSONL facts
    facts = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                fact = json.loads(line.strip())
                facts.append(fact)
            except:
                # Try as plain text
                if line.strip():
                    facts.append({'statement': line.strip()})
    
    print(f"✅ Loaded {len(facts)} facts from JSONL")
    
    # Connect to SQLite
    conn = sqlite3.connect(str(sqlite_path))
    cursor = conn.cursor()
    
    # Create facts table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT NOT NULL,
            confidence REAL DEFAULT 1.0,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Clear existing facts (optional)
    cursor.execute('DELETE FROM facts')
    print("🗑️  Cleared existing facts")
    
    # Import facts
    imported = 0
    for fact in facts:
        try:
            statement = fact.get('statement', '')
            if not statement:
                continue
                
            # Clean statement
            if not statement.endswith('.'):
                statement += '.'
                
            confidence = fact.get('confidence', 1.0)
            source = fact.get('source', 'jsonl_import')
            metadata = json.dumps({
                'tags': fact.get('tags', []),
                'imported_at': datetime.now().isoformat()
            })
            
            cursor.execute('''
                INSERT INTO facts (statement, confidence, source, metadata)
                VALUES (?, ?, ?, ?)
            ''', (statement, confidence, source, metadata))
            
            imported += 1
            
            if imported % 100 == 0:
                print(f"   Imported {imported} facts...")
                
        except Exception as e:
            print(f"   ⚠️ Failed to import: {fact} - {e}")
    
    # Commit changes
    conn.commit()
    
    # Verify import
    cursor.execute('SELECT COUNT(*) FROM facts')
    final_count = cursor.fetchone()[0]
    
    print(f"\n✅ IMPORT COMPLETE!")
    print(f"   Total facts in DB: {final_count}")
    
    # Show samples
    cursor.execute('SELECT statement FROM facts LIMIT 5')
    samples = cursor.fetchall()
    print(f"\n📋 Sample facts:")
    for s in samples:
        print(f"   - {s[0][:80]}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("🚀 NEXT STEPS:")
    print("1. Restart the backend")
    print("2. Facts should now load from SQLite")
    print("="*60)
    
    return True

if __name__ == '__main__':
    import_jsonl_to_sqlite()
