#!/usr/bin/env python3
"""Quick export from SQLite to JSONL to make HAK_GAL work"""

import sqlite3
import json
from pathlib import Path
import time

# Paths
sqlite_db = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
jsonl_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")

# Create data directory if not exists
jsonl_file.parent.mkdir(parents=True, exist_ok=True)

# Connect to SQLite
conn = sqlite3.connect(str(sqlite_db))
cursor = conn.cursor()

# Export all facts to JSONL
with open(jsonl_file, 'w', encoding='utf-8') as f:
    cursor.execute("SELECT statement, source, confidence, timestamp, tags FROM facts ORDER BY id")
    count = 0
    for row in cursor.fetchall():
        statement, source, confidence, timestamp, tags = row
        fact = {
            "statement": statement,
            "source": source or "unknown",
            "confidence": confidence or 1.0,
            "timestamp": timestamp or time.time()
        }
        if tags:
            fact["tags"] = json.loads(tags) if isinstance(tags, str) else tags
        f.write(json.dumps(fact, ensure_ascii=False) + "\n")
        count += 1

conn.close()
print(f"✅ Exported {count} facts from SQLite to JSONL")
print(f"   SQLite: {sqlite_db}")
print(f"   JSONL:  {jsonl_file}")
