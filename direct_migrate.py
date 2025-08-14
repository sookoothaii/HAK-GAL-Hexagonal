#!/usr/bin/env python3
"""
Direct SQLite Migration - Simple and Clean
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("HAK-GAL DIRECT SQLITE MIGRATION")
print("=" * 60)

# Paths
jsonl_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")
sqlite_path = Path("D:/MCP Mods/HAK_GAL_SUITE/k_assistant.db")

# Backup existing
if sqlite_path.exists():
    backup = Path(f"D:/MCP Mods/HAK_GAL_SUITE/k_assistant_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
    import shutil
    shutil.copy2(sqlite_path, backup)
    print(f"✅ Backup created: {backup.name}")

# Connect to SQLite
conn = sqlite3.connect(sqlite_path)
cursor = conn.cursor()

# Check existing table structure
cursor.execute("PRAGMA table_info(facts)")
existing_columns = cursor.fetchall()
if existing_columns:
    print("\n📊 Existing table structure found:")
    for col in existing_columns:
        print(f"   - {col[1]} ({col[2]})")
    
    # Clear existing data instead of dropping table
    print("\n🔧 Clearing existing facts...")
    cursor.execute("DELETE FROM facts")
    print("   ✅ Table cleared")
else:
    # Create new table if it doesn't exist
    print("\n🔧 Creating facts table...")
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            statement TEXT NOT NULL PRIMARY KEY,
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'migration',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_statement ON facts(statement)")
    print("   ✅ Table created")

# Read and validate facts
print("\n📖 Reading JSONL facts...")
valid_facts = []
seen = set()
invalid = 0

with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line in f:
        if not line.strip():
            continue
        try:
            obj = json.loads(line)
            stmt = obj.get('statement', '').strip()
            
            # Basic validation
            if not stmt:
                invalid += 1
                continue
                
            # Ensure period
            if not stmt.endswith('.'):
                stmt += '.'
                
            # Check syntax: Predicate(Args).
            if not re.match(r'^[A-Za-z][A-Za-z0-9_]*\([^)]+\)\.$', stmt):
                invalid += 1
                continue
                
            # Deduplicate
            if stmt in seen:
                continue
            seen.add(stmt)
            
            valid_facts.append({
                'statement': stmt,
                'confidence': obj.get('confidence', 1.0),
                'source': 'jsonl_migration'
            })
            
        except Exception:
            invalid += 1

print(f"   ✅ Found {len(valid_facts)} valid unique facts")
print(f"   ⚠️ Rejected {invalid} invalid entries")

# Insert into SQLite
print(f"\n💾 Inserting into SQLite...")
inserted = 0
failed = 0

for fact in valid_facts:
    try:
        cursor.execute("""
            INSERT INTO facts (statement, confidence, source)
            VALUES (?, ?, ?)
        """, (fact['statement'], fact['confidence'], fact['source']))
        inserted += 1
        
        if inserted % 500 == 0:
            print(f"   Progress: {inserted}/{len(valid_facts)}")
            
    except sqlite3.IntegrityError:
        failed += 1  # Duplicate
    except Exception as e:
        failed += 1
        print(f"   Error: {e}")

# Commit
conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM facts")
final_count = cursor.fetchone()[0]

# Get distribution
cursor.execute("""
    SELECT 
        CASE 
            WHEN statement LIKE 'Has%' THEN 'Has*'
            WHEN statement LIKE 'Is%' THEN 'Is*'
            WHEN statement LIKE 'Causes%' THEN 'Causes'
            WHEN statement LIKE 'Contains%' THEN 'Contains'
            ELSE SUBSTR(statement, 1, INSTR(statement, '(') - 1)
        END as pred_group,
        COUNT(*) as cnt
    FROM facts
    GROUP BY pred_group
    ORDER BY cnt DESC
    LIMIT 15
""")

print("\n" + "=" * 60)
print("✅ MIGRATION COMPLETE")
print("=" * 60)
print(f"Source facts: {len(valid_facts)}")
print(f"Inserted: {inserted}")
print(f"Failed: {failed}")
print(f"Final DB count: {final_count}")
print("\nTop predicate groups:")
for pred, cnt in cursor.fetchall():
    print(f"  {pred}: {cnt}")

conn.close()
print("\n✅ Database ready at:", sqlite_path)
print("\n⚠️ IMPORTANT: Restart the backend to use the new database!")
