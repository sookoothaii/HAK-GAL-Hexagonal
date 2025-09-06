#!/usr/bin/env python3
"""
Database Repair Script for HAK-GAL
Repairs corrupted SQLite database
"""

import sqlite3
import shutil
from pathlib import Path
import sys

def repair_database():
    """Repair corrupted SQLite database"""
    
    db_path = Path("hexagonal_kb.db")
    backup_path = Path("hexagonal_kb_corrupted.db")
    recovered_path = Path("hexagonal_kb_recovered.db")
    
    print("=" * 60)
    print("HAK-GAL DATABASE REPAIR TOOL")
    print("=" * 60)
    
    # 1. Create backup
    print("\n1. Creating backup...")
    try:
        shutil.copy2(db_path, backup_path)
        print(f"   ✅ Backup created: {backup_path}")
    except Exception as e:
        print(f"   ❌ Backup failed: {e}")
        return False
    
    # 2. Try to repair using Python
    print("\n2. Attempting repair...")
    try:
        # Connect to corrupted database
        conn_old = sqlite3.connect(str(db_path))
        conn_old.execute("PRAGMA integrity_check")
        
        # Create new database
        conn_new = sqlite3.connect(str(recovered_path))
        
        # Get schema from old database
        print("   - Extracting schema...")
        cursor = conn_old.execute("SELECT sql FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        # Create tables in new database
        for table in tables:
            if table[0]:  # Skip NULL entries
                try:
                    conn_new.execute(table[0])
                except Exception as e:
                    print(f"   ⚠️ Table creation issue: {e}")
        
        # Copy data
        print("   - Copying data...")
        cursor = conn_old.execute("SELECT name FROM sqlite_master WHERE type='table'")
        table_names = [row[0] for row in cursor.fetchall()]
        
        total_facts = 0
        for table_name in table_names:
            if table_name.startswith('sqlite_'):
                continue
            try:
                # Get data from old database
                cursor = conn_old.execute(f"SELECT * FROM {table_name}")
                rows = cursor.fetchall()
                
                if rows:
                    # Get column names
                    columns = [desc[0] for desc in cursor.description]
                    placeholders = ','.join(['?' for _ in columns])
                    
                    # Insert into new database
                    conn_new.executemany(
                        f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})",
                        rows
                    )
                    
                    if table_name == 'facts':
                        total_facts = len(rows)
                    
                    print(f"   ✅ Table '{table_name}': {len(rows)} rows copied")
            except Exception as e:
                print(f"   ⚠️ Error copying table '{table_name}': {e}")
        
        # Commit and close
        conn_new.commit()
        conn_old.close()
        conn_new.close()
        
        print(f"\n   ✅ Recovery complete: {total_facts} facts recovered")
        
        # 3. Replace old database
        print("\n3. Replacing corrupted database...")
        db_path.unlink()  # Delete corrupted
        recovered_path.rename(db_path)  # Rename recovered to original
        print(f"   ✅ Database replaced successfully")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Repair failed: {e}")
        
        # Try alternative method - dump and recreate
        print("\n4. Trying alternative repair method...")
        try:
            import subprocess
            
            # Use sqlite3 command line if available
            result = subprocess.run(
                ["sqlite3", str(db_path), ".dump"],
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                # Create new database from dump
                with open("dump.sql", "w") as f:
                    f.write(result.stdout)
                
                subprocess.run(
                    ["sqlite3", str(recovered_path)],
                    input=result.stdout,
                    text=True
                )
                
                # Replace database
                db_path.unlink()
                recovered_path.rename(db_path)
                print("   ✅ Alternative repair successful")
                return True
        except:
            pass
        
        print("\n   ❌ All repair attempts failed")
        print("   💡 Restore from backup: copy backups\\db_20250830120609.db hexagonal_kb.db")
        return False

def check_database():
    """Check database integrity"""
    print("\n5. Checking database integrity...")
    try:
        conn = sqlite3.connect("hexagonal_kb.db")
        cursor = conn.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        if result == "ok":
            print("   ✅ Database integrity: OK")
            
            # Get stats
            cursor = conn.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            print(f"   ✅ Facts count: {count}")
        else:
            print(f"   ⚠️ Integrity check: {result}")
        
        conn.close()
        return result == "ok"
    except Exception as e:
        print(f"   ❌ Check failed: {e}")
        return False

if __name__ == "__main__":
    success = repair_database()
    
    if success:
        check_database()
        print("\n" + "=" * 60)
        print("✅ DATABASE REPAIR COMPLETE")
        print("You can now restart the server:")
        print("python src_hexagonal/hexagonal_api_enhanced_clean.py")
        print("=" * 60)
    else:
        print("\n" + "=" * 60)
        print("❌ DATABASE REPAIR FAILED")
        print("Manual recovery needed:")
        print("1. Stop all processes using the database")
        print("2. Copy backups\\db_20250830120609.db hexagonal_kb.db")
        print("=" * 60)
        sys.exit(1)
