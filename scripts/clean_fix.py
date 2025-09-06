#!/usr/bin/env python3
"""
Clean fix for HAK_GAL MCP Server - Restore from backup and add SQLite methods properly
"""

import shutil
from pathlib import Path
from datetime import datetime

def clean_fix():
    """Restore from a known good backup and add SQLite methods cleanly"""
    
    server_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/scripts/hak_gal_mcp_fixed.py")
    backup_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/scripts/hak_gal_mcp_fixed_backup_20250815_225436.py")
    
    if not backup_file.exists():
        print("❌ Backup not found!")
        return False
    
    # Restore from backup
    shutil.copy2(backup_file, server_file)
    print(f"✅ Restored from backup: {backup_file}")
    
    # Read the file
    with open(server_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Find line 80 and fix indentation
    for i in range(len(lines)):
        # Fix the use_sqlite line
        if "self.use_sqlite =" in lines[i]:
            # Make sure it has correct indentation (8 spaces)
            lines[i] = "        self.use_sqlite = True  # ALWAYS use SQLite\n"
            print(f"✅ Fixed line {i+1}: use_sqlite")
        
        # Add _init_sqlite_db() call if missing
        if "self.use_sqlite = True" in lines[i] and i+1 < len(lines):
            if "_init_sqlite_db" not in lines[i+1]:
                lines.insert(i+1, "        self._init_sqlite_db()  # Initialize SQLite\n")
                print(f"✅ Added _init_sqlite_db() call")
    
    # Add SQLite methods after _parse_statement if not present
    parse_line = -1
    for i, line in enumerate(lines):
        if "def _parse_statement" in line:
            parse_line = i
            break
    
    # Find next method after _parse_statement
    next_method_line = -1
    if parse_line > 0:
        for i in range(parse_line + 1, len(lines)):
            if "    async def " in lines[i] or "    def send_response" in lines[i]:
                next_method_line = i
                break
    
    # Check if SQLite methods already exist
    has_sqlite_methods = any("_init_sqlite_db" in line for line in lines)
    
    if not has_sqlite_methods and next_method_line > 0:
        sqlite_methods = """
    # ==================== SQLite Methods ====================
    def _init_sqlite_db(self):
        \"\"\"Initialize SQLite database\"\"\"
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute(\"\"\"
                    CREATE TABLE IF NOT EXISTS facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        statement TEXT UNIQUE NOT NULL,
                        source TEXT,
                        confidence REAL DEFAULT 1.0,
                        timestamp REAL,
                        tags TEXT
                    )
                \"\"\")
                conn.commit()
                logger.info(f"SQLite DB initialized: {self.sqlite_db_path}")
        except Exception as e:
            logger.error(f"SQLite init error: {e}")

    def _yield_statements(self, limit=None):
        \"\"\"Yield statements from SQLite\"\"\"
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    yield row[0]
        except Exception as e:
            logger.error(f"Error: {e}")

    def _get_all_statements(self):
        \"\"\"Get all statements from SQLite\"\"\"
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                return [row[0] for row in cursor.fetchall()]
        except:
            return []

    def _count_facts(self):
        \"\"\"Count facts in SQLite\"\"\"
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                return cursor.fetchone()[0]
        except:
            return 0

    def _search_facts(self, query, limit=10):
        \"\"\"Search facts in SQLite\"\"\"
        results = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute(
                    "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                    (f"%{query}%", limit)
                )
                results = [row[0] for row in cursor.fetchall()]
        except:
            pass
        return results

"""
        lines.insert(next_method_line, sqlite_methods)
        print(f"✅ Added SQLite methods at line {next_method_line}")
    
    # Write the fixed file
    with open(server_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ File fixed and saved: {server_file}")
    print("\n🚀 Test the server now with:")
    print("   .\\scripts\\MCP_DEBUG.bat")
    
    return True

if __name__ == "__main__":
    clean_fix()
