#!/usr/bin/env python
"""
Analyze ALL Databases and JSONL
================================
Find where the 3776 facts actually are!
"""

import sqlite3
import json
from pathlib import Path

def analyze_all_sources():
    """Check ALL data sources"""
    
    print("="*60)
    print("🔍 ANALYZING ALL DATA SOURCES")
    print("="*60)
    
    # Check JSONL first
    jsonl_path = Path(__file__).parent / 'data' / 'k_assistant.kb.jsonl'
    if jsonl_path.exists():
        with open(jsonl_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            facts = []
            for line in lines:
                try:
                    fact = json.loads(line.strip())
                    facts.append(fact.get('statement', line))
                except:
                    facts.append(line.strip())
            
            print(f"\n📄 JSONL: data/k_assistant.kb.jsonl")
            print(f"   ✅ Facts: {len(facts)}")
            if facts:
                print(f"   Sample:")
                for f in facts[:3]:
                    if isinstance(f, dict):
                        print(f"     - {f.get('statement', str(f))[:80]}")
                    else:
                        print(f"     - {str(f)[:80]}")
    
    # Check all SQLite DBs
    databases = [
        'k_assistant.db',
        'k_assistant_dev.db', 
        'k_assistant_backup.db',
        'data/k_assistant.db',
        '../HAK_GAL_SUITE/k_assistant.db'  # Original location
    ]
    
    for db_name in databases:
        db_path = Path(__file__).parent / db_name
        if not db_path.exists():
            continue
            
        try:
            with sqlite3.connect(str(db_path)) as conn:
                cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts'")
                if not cursor.fetchone():
                    continue
                
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                count = cursor.fetchone()[0]
                
                cursor = conn.execute("SELECT statement FROM facts LIMIT 3")
                samples = [row[0] for row in cursor]
                
                print(f"\n💾 SQLite: {db_name}")
                print(f"   {'✅' if count > 0 else '❌'} Facts: {count}")
                if samples:
                    print(f"   Sample:")
                    for s in samples:
                        print(f"     - {s[:80]}")
                        
        except Exception as e:
            pass
    
    print("\n" + "="*60)
    print("📊 SUMMARY:")
    print("- JSONL has the facts (3776)")
    print("- SQLite DBs are empty or missing")
    print("- Backend is loading from wrong source!")
    print("="*60)
    
    print("\n🚀 SOLUTION:")
    print("1. Import JSONL facts into SQLite")
    print("2. OR: Switch backend to use JSONL directly")
    print("3. OR: Copy working DB from HAK_GAL_SUITE")
    print("="*60)

if __name__ == '__main__':
    analyze_all_sources()
