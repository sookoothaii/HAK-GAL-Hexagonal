#!/usr/bin/env python3
"""
Verify current state before and after migration
"""

import sqlite3
import json
from pathlib import Path

print("=" * 60)
print("DATABASE STATE VERIFICATION")
print("=" * 60)

# Check SQLite
sqlite_path = Path("D:/MCP Mods/HAK_GAL_SUITE/k_assistant.db")
if sqlite_path.exists():
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    
    # Get count
    cursor.execute("SELECT COUNT(*) FROM facts")
    sqlite_count = cursor.fetchone()[0]
    
    # Get table structure first
    cursor.execute("PRAGMA table_info(facts)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    # Get samples (without assuming id column exists)
    cursor.execute("SELECT statement FROM facts LIMIT 3")
    samples = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    print(f"SQLite Database:")
    print(f"  Path: {sqlite_path}")
    print(f"  Facts: {sqlite_count}")
    print(f"  Recent samples:")
    for s in samples:
        print(f"    - {s[:80]}...")
else:
    print(f"❌ SQLite not found: {sqlite_path}")

print()

# Check JSONL
jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
if jsonl_path.exists():
    count = 0
    samples = []
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
                if count <= 3:
                    try:
                        obj = json.loads(line)
                        samples.append(obj.get('statement', ''))
                    except:
                        pass
    
    print(f"JSONL File:")
    print(f"  Path: {jsonl_path}")
    print(f"  Facts: {count}")
    print(f"  First samples:")
    for s in samples:
        print(f"    - {s[:80]}...")
else:
    print(f"❌ JSONL not found: {jsonl_path}")

print("\n" + "=" * 60)
print("RECOMMENDATION:")
if sqlite_path.exists() and jsonl_path.exists():
    conn = sqlite3.connect(sqlite_path)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facts")
    sqlite_count = cursor.fetchone()[0]
    conn.close()
    
    jsonl_count = count
    
    if sqlite_count < jsonl_count * 0.5:
        print(f"⚠️ SQLite has only {sqlite_count}/{jsonl_count} facts ({(sqlite_count/jsonl_count)*100:.1f}%)")
        print("👉 Run migration: python direct_migrate.py")
    else:
        print(f"✅ SQLite has {sqlite_count} facts ({(sqlite_count/jsonl_count)*100:.1f}% of JSONL)")
        print("Database appears properly migrated")
