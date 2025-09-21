#!/usr/bin/env python3
"""Bidirectional sync between SQLite and JSONL for HAK_GAL"""

import sqlite3
import json
from pathlib import Path
import time
import sys

# Configuration
SQLITE_DB = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
JSONL_FILE = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/data/k_assistant.kb.jsonl")

def sqlite_to_jsonl():
    """Export SQLite to JSONL"""
    if not SQLITE_DB.exists():
        print(f"❌ SQLite DB not found: {SQLITE_DB}")
        return False
    
    JSONL_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(str(SQLITE_DB))
    cursor = conn.cursor()
    
    with open(JSONL_FILE, 'w', encoding='utf-8') as f:
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
                try:
                    fact["tags"] = json.loads(tags) if isinstance(tags, str) else tags
                except:
                    fact["tags"] = []
            f.write(json.dumps(fact, ensure_ascii=False) + "\n")
            count += 1
    
    conn.close()
    print(f"✅ Exported {count} facts: SQLite → JSONL")
    return True

def jsonl_to_sqlite():
    """Import JSONL to SQLite"""
    if not JSONL_FILE.exists():
        print(f"❌ JSONL file not found: {JSONL_FILE}")
        return False
    
    conn = sqlite3.connect(str(SQLITE_DB))
    cursor = conn.cursor()
    
    # Create table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS facts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            statement TEXT UNIQUE NOT NULL,
            source TEXT,
            confidence REAL DEFAULT 1.0,
            timestamp REAL,
            tags TEXT
        )
    """)
    
    count = 0
    with open(JSONL_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            if not line.strip():
                continue
            try:
                fact = json.loads(line)
                statement = fact.get("statement", "")
                if not statement:
                    continue
                
                cursor.execute("""
                    INSERT OR IGNORE INTO facts (statement, source, confidence, timestamp, tags)
                    VALUES (?, ?, ?, ?, ?)
                """, (
                    statement,
                    fact.get("source", "unknown"),
                    fact.get("confidence", 1.0),
                    fact.get("timestamp", time.time()),
                    json.dumps(fact.get("tags", [])) if fact.get("tags") else None
                ))
                count += cursor.rowcount
            except Exception as e:
                print(f"Warning: Skip line: {e}")
    
    conn.commit()
    conn.close()
    print(f"✅ Imported {count} new facts: JSONL → SQLite")
    return True

def main():
    """Main sync logic"""
    print("🔄 HAK_GAL Format Sync Tool")
    print("=" * 50)
    
    sqlite_exists = SQLITE_DB.exists()
    jsonl_exists = JSONL_FILE.exists()
    
    print(f"SQLite DB:  {'✅ Found' if sqlite_exists else '❌ Missing'} - {SQLITE_DB}")
    print(f"JSONL File: {'✅ Found' if jsonl_exists else '❌ Missing'} - {JSONL_FILE}")
    print()
    
    if len(sys.argv) > 1:
        direction = sys.argv[1].lower()
        if direction == "to-jsonl":
            sqlite_to_jsonl()
        elif direction == "to-sqlite":
            jsonl_to_sqlite()
        else:
            print("Usage: python sync_formats.py [to-jsonl|to-sqlite|auto]")
    else:
        # Auto mode: sync based on what exists
        if sqlite_exists and not jsonl_exists:
            print("🔄 Auto-mode: Creating missing JSONL from SQLite...")
            sqlite_to_jsonl()
        elif jsonl_exists and not sqlite_exists:
            print("🔄 Auto-mode: Creating missing SQLite from JSONL...")
            jsonl_to_sqlite()
        elif sqlite_exists and jsonl_exists:
            # Compare timestamps
            sqlite_mtime = SQLITE_DB.stat().st_mtime
            jsonl_mtime = JSONL_FILE.stat().st_mtime
            
            if sqlite_mtime > jsonl_mtime:
                print("🔄 Auto-mode: SQLite is newer → updating JSONL...")
                sqlite_to_jsonl()
            else:
                print("🔄 Auto-mode: JSONL is newer → updating SQLite...")
                jsonl_to_sqlite()
        else:
            print("❌ Neither SQLite nor JSONL found! Nothing to sync.")
            sys.exit(1)

if __name__ == "__main__":
    main()
