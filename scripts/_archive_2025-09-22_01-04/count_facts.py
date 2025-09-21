#!/usr/bin/env python
"""Quick fact counter for HAK_GAL databases"""
import sqlite3
from pathlib import Path

# Check main SQLite database
db_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
if db_path.exists():
    conn = sqlite3.connect(str(db_path))
    cursor = conn.execute("SELECT COUNT(*) FROM facts")
    count = cursor.fetchone()[0]
    print(f"hexagonal_kb.db: {count} facts")
    
    # Get top predicates
    cursor = conn.execute("""
        SELECT 
            CASE 
                WHEN instr(statement, '(') > 0 
                THEN substr(statement, 1, instr(statement, '(') - 1)
                ELSE 'Invalid'
            END as predicate,
            COUNT(*) as cnt
        FROM facts 
        GROUP BY predicate
        ORDER BY cnt DESC
        LIMIT 10
    """)
    print("\nTop Predicates:")
    for pred, cnt in cursor:
        print(f"  {pred}: {cnt}")
    conn.close()
else:
    print("hexagonal_kb.db not found")

# Check JSONL file
jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
if jsonl_path.exists():
    with open(jsonl_path, 'r', encoding='utf-8') as f:
        lines = sum(1 for line in f if line.strip())
    print(f"\nk_assistant.kb.jsonl: {lines} facts")
else:
    print("\nk_assistant.kb.jsonl not found")
