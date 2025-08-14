#!/usr/bin/env python3
"""
Quick test of current database state
"""

import sqlite3
from pathlib import Path

# Check current SQLite state
db_path = Path("D:/MCP Mods/HAK_GAL_SUITE/k_assistant.db")

if db_path.exists():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get current count
    cursor.execute("SELECT COUNT(*) FROM facts")
    count = cursor.fetchone()[0]
    print(f"Current facts in SQLite: {count}")
    
    # Get sample facts
    cursor.execute("SELECT statement FROM facts LIMIT 5")
    samples = cursor.fetchall()
    print("\nSample facts:")
    for s in samples:
        print(f"  - {s[0]}")
    
    # Get predicate distribution
    cursor.execute("""
        SELECT 
            SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
            COUNT(*) as cnt 
        FROM facts 
        WHERE statement LIKE '%(%' 
        GROUP BY predicate 
        ORDER BY cnt DESC 
        LIMIT 10
    """)
    
    print("\nTop predicates:")
    for pred, cnt in cursor.fetchall():
        print(f"  {pred}: {cnt}")
    
    conn.close()
else:
    print(f"Database not found: {db_path}")

# Check JSONL state
jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
if jsonl_path.exists():
    import json
    count = 0
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                count += 1
    print(f"\nFacts in JSONL: {count}")
