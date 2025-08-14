#!/usr/bin/env python3
"""
Safe SQLite Migration - Handles existing table structure
"""

import json
import sqlite3
import re
from pathlib import Path
from datetime import datetime

print("=" * 60)
print("HAK-GAL SAFE SQLITE MIGRATION")
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
column_names = [col[1] for col in existing_columns] if existing_columns else []

print("\n📊 Database Analysis:")
if existing_columns:
    print(f"   Existing table found with columns: {', '.join(column_names)}")
    
    # Get current count before clearing
    cursor.execute("SELECT COUNT(*) FROM facts")
    old_count = cursor.fetchone()[0]
    print(f"   Current facts: {old_count}")
    
    # Clear existing data
    print("\n🔧 Clearing existing facts...")
    cursor.execute("DELETE FROM facts")
    conn.commit()
    print("   ✅ Table cleared")
else:
    print("   No existing table found. Creating new structure...")
    
    # Create new table
    cursor.execute("""
        CREATE TABLE facts (
            statement TEXT NOT NULL PRIMARY KEY,
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'migration',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    cursor.execute("CREATE INDEX idx_statement ON facts(statement)")
    print("   ✅ Table created")
    column_names = ['statement', 'confidence', 'source', 'created_at']

# Read and validate facts
print("\n📖 Reading JSONL facts...")
valid_facts = []
seen = set()
invalid = 0
duplicates = 0

with open(jsonl_path, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
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
                print(f"   ⚠️ Invalid syntax at line {line_num}: {stmt[:50]}...")
                continue
                
            # Deduplicate
            if stmt in seen:
                duplicates += 1
                continue
            seen.add(stmt)
            
            valid_facts.append({
                'statement': stmt,
                'confidence': obj.get('confidence', 1.0),
                'source': obj.get('source', 'jsonl_migration')
            })
            
        except json.JSONDecodeError as e:
            invalid += 1
            print(f"   ⚠️ JSON error at line {line_num}: {e}")
        except Exception as e:
            invalid += 1
            print(f"   ⚠️ Error at line {line_num}: {e}")

print(f"\n📊 JSONL Analysis Complete:")
print(f"   Valid unique facts: {len(valid_facts)}")
print(f"   Invalid entries: {invalid}")
print(f"   Duplicates removed: {duplicates}")

# Insert into SQLite
print(f"\n💾 Inserting into SQLite...")
inserted = 0
failed = 0

# Determine which columns we can use
has_confidence = 'confidence' in column_names
has_source = 'source' in column_names

for i, fact in enumerate(valid_facts, 1):
    try:
        if has_confidence and has_source:
            cursor.execute("""
                INSERT INTO facts (statement, confidence, source)
                VALUES (?, ?, ?)
            """, (fact['statement'], fact['confidence'], fact['source']))
        elif has_confidence:
            cursor.execute("""
                INSERT INTO facts (statement, confidence)
                VALUES (?, ?)
            """, (fact['statement'], fact['confidence']))
        elif has_source:
            cursor.execute("""
                INSERT INTO facts (statement, source)
                VALUES (?, ?)
            """, (fact['statement'], fact['source']))
        else:
            cursor.execute("""
                INSERT INTO facts (statement)
                VALUES (?)
            """, (fact['statement'],))
            
        inserted += 1
        
        if inserted % 500 == 0:
            print(f"   Progress: {inserted}/{len(valid_facts)} ({(inserted/len(valid_facts))*100:.1f}%)")
            conn.commit()  # Commit in batches
            
    except sqlite3.IntegrityError:
        failed += 1  # Duplicate (shouldn't happen after our dedup, but just in case)
    except Exception as e:
        failed += 1
        print(f"   Error inserting fact {i}: {e}")
        print(f"     Statement: {fact['statement'][:100]}...")

# Final commit
conn.commit()

# Verify
cursor.execute("SELECT COUNT(*) FROM facts")
final_count = cursor.fetchone()[0]

# Get distribution
print("\n📊 Analyzing migrated data...")
cursor.execute("""
    SELECT 
        SUBSTR(statement, 1, 
            CASE 
                WHEN INSTR(statement, '(') > 0 THEN INSTR(statement, '(') - 1
                ELSE 10
            END
        ) as predicate,
        COUNT(*) as cnt
    FROM facts
    WHERE statement LIKE '%(%'
    GROUP BY predicate
    ORDER BY cnt DESC
    LIMIT 20
""")

predicates = cursor.fetchall()

print("\n" + "=" * 60)
print("✅ MIGRATION COMPLETE")
print("=" * 60)
print(f"Source JSONL facts: {len(valid_facts) + duplicates + invalid}")
print(f"Valid unique facts: {len(valid_facts)}")
print(f"Successfully inserted: {inserted}")
print(f"Failed inserts: {failed}")
print(f"Final database count: {final_count}")
print(f"\nMigration efficiency: {(final_count/(len(valid_facts) + duplicates + invalid))*100:.1f}%")

print("\nTop 20 predicates:")
for pred, cnt in predicates:
    percentage = (cnt/final_count)*100 if final_count > 0 else 0
    print(f"  {pred}: {cnt} ({percentage:.1f}%)")

# Check language distribution
english_count = sum(cnt for pred, cnt in predicates if not any(
    pred.startswith(p) for p in ['Hat', 'Ist', 'Verursacht', 'Besteht', 'Wird']
))
total_top20 = sum(cnt for _, cnt in predicates)
print(f"\nLanguage estimate (from top 20):")
print(f"  English-style predicates: {(english_count/total_top20)*100:.1f}%")

conn.close()
print("\n✅ Database ready at:", sqlite_path)
print("\n⚠️ IMPORTANT: Restart the backend to use the new database!")
print("   Run: .\\start_enhanced_api.bat")
