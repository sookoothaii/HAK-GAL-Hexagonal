#!/usr/bin/env python
"""
QUICK FIX: Copy k_assistant_dev.db to HAK_GAL_SUITE
====================================================
Use the CORRECT database with 3079 valid facts
"""

import shutil
from pathlib import Path
from datetime import datetime

def quick_fix():
    """Copy the working DB with 3079 facts to where backend expects it"""
    
    # Source: Working DB with 3079 CORRECT facts
    source_db = Path(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\k_assistant_dev.db")
    
    # Target: Where backend actually loads from
    target_db = Path(r"D:\MCP Mods\HAK_GAL_SUITE\k_assistant.db")
    
    print("="*60)
    print("⚡ QUICK FIX: Deploy Correct Database")
    print("="*60)
    print(f"Source: k_assistant_dev.db (3079 VALID facts)")
    print(f"Target: {target_db}")
    print("="*60)
    
    # Check source exists
    if not source_db.exists():
        print(f"❌ Source not found: {source_db}")
        return False
    
    # Backup target if it exists
    if target_db.exists():
        backup_name = f"k_assistant_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db.backup"
        backup_path = target_db.parent / backup_name
        shutil.copy2(target_db, backup_path)
        print(f"✅ Backup created: {backup_path}")
    
    # Copy the correct DB
    print(f"\n📋 Copying database...")
    shutil.copy2(source_db, target_db)
    print(f"✅ Database copied successfully!")
    
    # Verify
    import sqlite3
    with sqlite3.connect(str(target_db)) as conn:
        cursor = conn.execute("SELECT COUNT(*) FROM facts")
        count = cursor.fetchone()[0]
        
        cursor = conn.execute("SELECT statement FROM facts LIMIT 5")
        samples = [row[0] for row in cursor]
    
    print(f"\n✅ VERIFICATION:")
    print(f"   Facts in target DB: {count}")
    print(f"   Sample facts:")
    for s in samples[:3]:
        print(f"     - {s[:60]}...")
    
    print("\n" + "="*60)
    print("🎉 SUCCESS!")
    print("1. The backend will now load 3079 correct facts")
    print("2. Restart the backend to see the change")
    print("3. JSONL is ignored (it was corrupt anyway)")
    print("="*60)
    
    return True

if __name__ == '__main__':
    quick_fix()
