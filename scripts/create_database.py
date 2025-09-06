#!/usr/bin/env python3
"""
CREATE THE MISSING DATABASE!
============================
"""

import sqlite3
from pathlib import Path

print("\n" + "🔨"*40)
print("CREATING HEXAGONAL DATABASE")
print("🔨"*40)

db_path = Path("hexagonal_kb.db")

if db_path.exists():
    print(f"\n⚠️ Database already exists: {db_path}")
    print(f"   Size: {db_path.stat().st_size:,} bytes")
else:
    print(f"\n📦 Creating new database: {db_path}")
    
    # Create database and tables
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Create facts table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT UNIQUE NOT NULL,
            confidence REAL DEFAULT 1.0,
            source TEXT DEFAULT 'system',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    # Create index for faster searches
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_statement ON facts(statement)
    """)
    
    # Add some initial facts to test
    initial_facts = [
        "IsA(HAK_GAL, KnowledgeSystem).",
        "IsA(Hexagonal, Architecture).",
        "Uses(HAK_GAL, DeepSeek).",
        "HasProperty(System, Operational).",
        "GeneratedBy(Knowledge, Engines)."
    ]
    
    for fact in initial_facts:
        try:
            cursor.execute(
                "INSERT INTO facts (statement, source) VALUES (?, ?)",
                (fact, "initialization")
            )
            print(f"   ✅ Added: {fact}")
        except sqlite3.IntegrityError:
            print(f"   ⚠️ Already exists: {fact}")
    
    conn.commit()
    
    # Check what we have
    cursor.execute("SELECT COUNT(*) FROM facts")
    count = cursor.fetchone()[0]
    
    print(f"\n✅ Database created successfully!")
    print(f"   Total facts: {count}")
    
    conn.close()

# Verify
if db_path.exists():
    print(f"\n✅ DATABASE NOW EXISTS!")
    print(f"   Path: {db_path.absolute()}")
    print(f"   Size: {db_path.stat().st_size:,} bytes")
    
    # Test connection
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM facts")
    count = cursor.fetchone()[0]
    conn.close()
    
    print(f"   Facts in database: {count}")
else:
    print("\n❌ Failed to create database!")

print("\n" + "="*60)
print("NOW START THE BACKEND:")
print("  python src_hexagonal/hexagonal_api_enhanced_clean.py")
print("="*60)
