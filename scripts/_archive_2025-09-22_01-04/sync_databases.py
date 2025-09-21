#!/usr/bin/env python3
"""
Synchronisiert k_assistant.db -> hexagonal_kb.db für faire Benchmark-Tests
Port 5001 (Python) vs Port 5002 (Mojo) mit identischen Daten
"""

import sqlite3
import shutil
from pathlib import Path
from datetime import datetime

def sync_databases():
    """Kopiert alle Facts von k_assistant.db nach hexagonal_kb.db"""
    
    source_db = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/k_assistant.db")
    target_db = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
    
    if not source_db.exists():
        print(f"❌ Source database not found: {source_db}")
        return False
    
    # Backup der Target-DB
    if target_db.exists():
        backup_path = target_db.parent / f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        shutil.copy2(target_db, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    try:
        # Verbindungen öffnen
        source_conn = sqlite3.connect(source_db)
        target_conn = sqlite3.connect(target_db)
        
        source_cur = source_conn.cursor()
        target_cur = target_conn.cursor()
        
        # Target-DB Schema prüfen/erstellen
        target_cur.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement TEXT NOT NULL,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Vorher: Facts zählen
        target_cur.execute("SELECT COUNT(*) FROM facts")
        before_count = target_cur.fetchone()[0]
        print(f"📊 Target DB before: {before_count} facts")
        
        source_cur.execute("SELECT COUNT(*) FROM facts")
        source_count = source_cur.fetchone()[0]
        print(f"📊 Source DB has: {source_count} facts")
        
        # Target-DB leeren (für sauberen Import)
        target_cur.execute("DELETE FROM facts")
        print("🗑️ Cleared target database")
        
        # Alle Facts kopieren
        source_cur.execute("""
            SELECT statement, confidence, source, tags, created_at, updated_at 
            FROM facts
        """)
        
        facts = source_cur.fetchall()
        
        target_cur.executemany("""
            INSERT INTO facts (statement, confidence, source, tags, created_at, updated_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, facts)
        
        # Commit und verify
        target_conn.commit()
        
        target_cur.execute("SELECT COUNT(*) FROM facts")
        after_count = target_cur.fetchone()[0]
        
        print(f"✅ Synchronized: {after_count} facts copied")
        
        # Top-Prädikate vergleichen
        print("\n📊 Verification - Top predicates in target DB:")
        target_cur.execute("""
            SELECT 
                SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                COUNT(*) as count
            FROM facts
            WHERE statement LIKE '%(%'
            GROUP BY predicate
            ORDER BY count DESC
            LIMIT 10
        """)
        
        for pred, count in target_cur.fetchall():
            print(f"  {pred}: {count}")
        
        source_conn.close()
        target_conn.close()
        
        print(f"\n✅ SUCCESS: hexagonal_kb.db now has {after_count} facts")
        print("🎯 Ready for fair benchmark: Port 5001 (Python) vs Port 5002 (Mojo)")
        return True
        
    except Exception as e:
        print(f"❌ Error during sync: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("DATABASE SYNCHRONIZATION FOR BENCHMARK TESTING")
    print("k_assistant.db -> hexagonal_kb.db")
    print("=" * 60)
    sync_databases()
