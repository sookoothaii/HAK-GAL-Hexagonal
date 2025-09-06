#!/usr/bin/env python3
"""
Complete SQLite migration for HAK_GAL MCP Server
This script patches all file-based operations to use SQLite
"""

import re
import shutil
from pathlib import Path
from datetime import datetime

def migrate_to_sqlite():
    """Migrate the MCP server from JSONL to SQLite"""
    
    server_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/scripts/hak_gal_mcp_fixed.py")
    
    # Create timestamped backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = server_file.parent / f"hak_gal_mcp_fixed_pre_sqlite_{timestamp}.py"
    shutil.copy2(server_file, backup_file)
    print(f"✅ Backup created: {backup_file}")
    
    # Read the file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add SQLite helper methods right after the __init__ method
    sqlite_methods = '''
    def _init_sqlite_db(self):
        """Initialize SQLite database with proper schema"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS facts (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        statement TEXT UNIQUE NOT NULL,
                        source TEXT,
                        confidence REAL DEFAULT 1.0,
                        timestamp REAL,
                        tags TEXT
                    )
                """)
                conn.commit()
                logger.info(f"SQLite DB initialized: {self.sqlite_db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize SQLite: {e}")

    def _yield_statements(self, limit=None):
        """Generator that yields statements from SQLite DB"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    yield row[0]
        except Exception as e:
            logger.error(f"Error in _yield_statements: {e}")
            return

    def _get_all_statements(self):
        """Get all statements from SQLite as a list"""
        statements = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                statements = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error in _get_all_statements: {e}")
        return statements

    def _get_fact_objects(self, limit=None, offset=None, reverse=False):
        """Get full fact objects from SQLite"""
        facts = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement, source, confidence, timestamp, tags FROM facts"
                if reverse:
                    query += " ORDER BY id DESC"
                else:
                    query += " ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                if offset:
                    query += f" OFFSET {offset}"
                    
                cursor = conn.execute(query)
                for row in cursor:
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
                    facts.append(fact)
        except Exception as e:
            logger.error(f"Error in _get_fact_objects: {e}")
        return facts

    def _count_facts(self):
        """Count total facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                return cursor.fetchone()[0]
        except:
            return 0
'''

    # Add helper methods after __init__
    init_end = content.find("self.use_sqlite")
    if init_end != -1:
        # Find the end of __init__ method
        init_end = content.find("\n\n    def ", init_end)
        if init_end != -1:
            # Check if methods don't already exist
            if "_init_sqlite_db" not in content:
                content = content[:init_end] + "\n        # Initialize SQLite\n        self._init_sqlite_db()\n" + sqlite_methods + content[init_end:]
                print("✅ Added SQLite helper methods")
    
    # Replace file-based operations with SQLite calls
    replacements = [
        # search_knowledge
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+for line in f:',
         'for statement in self._yield_statements():\n                line = json.dumps({"statement": statement})'),
        
        # list_recent_facts
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+lines = f\.readlines\(\)',
         'facts = self._get_fact_objects(limit=count)\n                    lines = [json.dumps(f) for f in facts]'),
        
        # kb_stats - replace file stat with SQLite stats
        (r'st = self\.kb_path\.stat\(\)',
         'cnt = self._count_facts()'),
        
        # export_facts
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+lines = f\.readlines\(\)',
         'facts = self._get_fact_objects()\n                    lines = [json.dumps(f) + "\\n" for f in facts]'),
    ]
    
    # Apply regex replacements
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # Simple string replacements for common patterns
    simple_replacements = [
        # Replace file iteration patterns
        ('with open(self.kb_path, \'r\', encoding=\'utf-8\') as f:\n                        for line in f:',
         'for statement in self._yield_statements():\n                            line = json.dumps({"statement": statement})'),
        
        # Replace another common pattern
        ('with open(self.kb_path, "r", encoding="utf-8") as f:\n                        for line in f:',
         'for statement in self._yield_statements():\n                            line = json.dumps({"statement": statement})'),
         
        # Fix health_check
        ('kb_exists = self.kb_path.exists()',
         'kb_exists = self.sqlite_db_path.exists()'),
    ]
    
    for old, new in simple_replacements:
        content = content.replace(old, new)
    
    # Write the patched content
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"✅ Server migrated to SQLite successfully!")
    print(f"   Original backed up to: {backup_file}")
    print(f"   Updated file: {server_file}")
    print("\n⚠️  Please restart the MCP server for changes to take effect")
    
    return True

if __name__ == "__main__":
    migrate_to_sqlite()
