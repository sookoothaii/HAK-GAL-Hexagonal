#!/usr/bin/env python
"""
FIX: Import JSONL into HAK_GAL_SUITE SQLite Database  
=====================================================
The backend loads from HAK_GAL_SUITE/k_assistant.db, not the local one!
This script fixes the ACTUAL database that's being used.
"""

import sqlite3
import json
from pathlib import Path
from datetime import datetime
import shutil

def fix_hakgal_suite_db():
    """Import JSONL facts into the ACTUAL database being used"""
    
    # Critical paths
    jsonl_path = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\data\k_assistant.kb.jsonl")
    target_db = Path(r"D:\MCP Mods\HAK_GAL_SUITE\k_assistant.db")
    
    print("="*60)
    print("🚨 FIXING THE ACTUAL DATABASE")
    print("="*60)
    print(f"Source: {jsonl_path}")
    print(f"Target: {target_db}")
    print("="*60)
    
    # Backup original DB
    backup_path = target_db.with_suffix('.db.backup')
    shutil.copy2(target_db, backup_path)
    print(f"✅ Backup created: {backup_path}")
    
    # Load JSONL facts
    if not jsonl_path.exists():
        print(f"❌ JSONL not found: {jsonl_path}")
        return False
        
    facts = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                fact = json.loads(line.strip())
                facts.append(fact)
            except:
                if line.strip():
                    facts.append({'statement': line.strip()})
    
    print(f"✅ Loaded {len(facts)} facts from JSONL")
    
    # Connect to target SQLite
    conn = sqlite3.connect(str(target_db))
    cursor = conn.cursor()
    
    # Create facts table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT NOT NULL UNIQUE,
            confidence REAL DEFAULT 1.0,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            metadata TEXT
        )
    ''')
    
    # Clear existing facts
    cursor.execute('DELETE FROM facts')
    conn.commit()
    print("🗑️  Cleared existing facts")
    
    # Import facts with deduplication
    imported = 0
    skipped = 0
    
    for fact in facts:
        try:
            statement = fact.get('statement', '')
            if not statement:
                continue
                
            # Clean statement
            statement = statement.strip()
            if not statement.endswith('.'):
                statement += '.'
                
            confidence = fact.get('confidence', 1.0)
            source = fact.get('source', 'hexagonal_import')
            metadata = json.dumps({
                'tags': fact.get('tags', []),
                'imported_at': datetime.now().isoformat()
            })
            
            try:
                cursor.execute('''
                    INSERT INTO facts (statement, confidence, source, metadata)
                    VALUES (?, ?, ?, ?)
                ''', (statement, confidence, source, metadata))
                imported += 1
            except sqlite3.IntegrityError:
                # Duplicate statement
                skipped += 1
                
            if imported % 100 == 0:
                print(f"   Imported {imported} facts...")
                conn.commit()
                
        except Exception as e:
            print(f"   ⚠️ Failed: {e}")
    
    # Final commit
    conn.commit()
    
    # Verify import
    cursor.execute('SELECT COUNT(*) FROM facts')
    final_count = cursor.fetchone()[0]
    
    print(f"\n✅ IMPORT COMPLETE!")
    print(f"   Total imported: {imported}")
    print(f"   Skipped duplicates: {skipped}")
    print(f"   Final count in DB: {final_count}")
    
    # Show samples
    cursor.execute('SELECT statement FROM facts ORDER BY id DESC LIMIT 5')
    samples = cursor.fetchall()
    print(f"\n📋 Latest facts:")
    for s in samples:
        print(f"   - {s[0][:80]}")
    
    conn.close()
    
    print("\n" + "="*60)
    print("🚀 SOLUTION COMPLETE!")
    print("1. The HAK_GAL_SUITE/k_assistant.db now has all facts")
    print("2. Restart the backend - it should load 3776 facts")
    print("3. If problems, restore from: " + str(backup_path))
    print("="*60)
    
    return True

if __name__ == '__main__':
    fix_hakgal_suite_db()
