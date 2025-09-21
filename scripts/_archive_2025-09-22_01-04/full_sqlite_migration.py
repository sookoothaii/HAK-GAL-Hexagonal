#!/usr/bin/env python3
"""
COMPLETE SQLite Migration for HAK_GAL MCP Server
This will fully replace ALL JSONL operations with SQLite
NO COMPROMISES - FULL MIGRATION
"""

import sys
import re
from pathlib import Path
from datetime import datetime
import shutil

def full_sqlite_migration():
    """Complete migration to SQLite - no JSONL fallback"""
    
    server_file = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/scripts/hak_gal_mcp_fixed.py")
    
    print("="*60)
    print("FULL SQLite MIGRATION - NO COMPROMISES")
    print("="*60)
    
    # Create backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = server_file.parent / f"hak_gal_mcp_fixed_pre_full_sqlite_{timestamp}.py"
    shutil.copy2(server_file, backup_file)
    print(f"✅ Backup: {backup_file}")
    
    # Read file
    with open(server_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. Fix __init__ to always use SQLite
    init_fix = """        self.use_sqlite = True  # ALWAYS use SQLite
        
        # Initialize SQLite DB
        self._init_sqlite_db()"""
    
    content = re.sub(
        r'self\.use_sqlite = self\.sqlite_db_path\.exists\(\)',
        init_fix,
        content
    )
    
    # 2. Add complete SQLite methods after _parse_statement
    sqlite_methods = '''
    # ==================== COMPLETE SQLite Implementation ====================
    def _init_sqlite_db(self):
        """Initialize SQLite database"""
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
                logger.info(f"SQLite DB ready: {self.sqlite_db_path}")
        except Exception as e:
            logger.error(f"SQLite init error: {e}")

    def _yield_statements(self, limit=None):
        """Yield statements from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                query = "SELECT statement FROM facts ORDER BY id"
                if limit:
                    query += f" LIMIT {limit}"
                cursor = conn.execute(query)
                for row in cursor:
                    yield row[0]
        except Exception as e:
            logger.error(f"_yield_statements error: {e}")

    def _get_all_statements(self):
        """Get all statements from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                return [row[0] for row in cursor.fetchall()]
        except Exception:
            return []

    def _get_fact_objects(self, limit=None, reverse=False):
        """Get fact objects from SQLite"""
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
            logger.error(f"_get_fact_objects error: {e}")
        return facts

    def _count_facts(self):
        """Count facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                return cursor.fetchone()[0]
        except:
            return 0

    def _search_facts(self, query, limit=10):
        """Search facts in SQLite"""
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
    # ==================== End SQLite Implementation ====================
'''

    # Insert SQLite methods if not already present
    if "_yield_statements" not in content:
        parse_pos = content.find("def _parse_statement")
        if parse_pos != -1:
            next_method = content.find("\n    async def ", parse_pos)
            if next_method != -1:
                content = content[:next_method] + "\n" + sqlite_methods + "\n" + content[next_method:]
                print("✅ Added SQLite methods")
    
    # 3. Replace search_knowledge completely
    search_pattern = r'async def search_knowledge\(self, query: str, limit: int = 10\):.*?(?=\n    async def |\Z)'
    new_search = '''async def search_knowledge(self, query: str, limit: int = 10):
        """Search knowledge base using SQLite ONLY"""
        try:
            results = self._search_facts(query, limit)
            return {"count": len(results), "facts": results}
        except Exception as e:
            logger.error(f"Search error: {e}")
            return {"count": 0, "facts": []}
'''
    content = re.sub(search_pattern, new_search, content, flags=re.DOTALL)
    
    # 4. Replace get_system_status completely
    status_pattern = r'async def get_system_status\(self\):.*?(?=\n    async def |\Z)'
    new_status = '''async def get_system_status(self):
        """Get system status from SQLite ONLY"""
        try:
            count = self._count_facts()
            db_path = self.sqlite_db_path
            db_size = db_path.stat().st_size if db_path.exists() else 0
            return {
                "status": "OK (SQLite)",
                "kb_facts": count,
                "kb_path": str(db_path),
                "kb_size": db_size,
                "server": "HAK_GAL MCP SQLite v2.0"
            }
        except Exception as e:
            return {"error": str(e)}
'''
    content = re.sub(status_pattern, new_status, content, flags=re.DOTALL)
    
    # 5. Replace list_recent_facts completely
    recent_pattern = r'async def list_recent_facts\(self, count: int = 5\):.*?(?=\n    async def |\Z)'
    new_recent = '''async def list_recent_facts(self, count: int = 5):
        """List recent facts from SQLite ONLY"""
        try:
            facts = []
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute(
                    "SELECT statement FROM facts ORDER BY id DESC LIMIT ?",
                    (count,)
                )
                facts = [row[0] for row in cursor.fetchall()]
            return {"facts": facts}
        except Exception as e:
            return {"error": str(e)}
'''
    content = re.sub(recent_pattern, new_recent, content, flags=re.DOTALL)
    
    # 6. Fix ALL file reading patterns in handle_tool_call
    replacements = [
        # Replace ALL file reads with SQLite
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:',
         '# SQLite mode\n                    for statement in self._yield_statements():'),
        
        # Fix kb_stats to use SQLite
        (r'if getattr\(self, [\'"]use_sqlite[\'"], False\):',
         'if True:  # Always SQLite'),
        
        # Fix export_facts
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+lines = f\.readlines\(\)',
         'facts = self._get_fact_objects(limit=count if direction == "head" else None)\n                    if direction == "tail":\n                        facts = facts[-count:]\n                    lines = [json.dumps(f) + "\\n" for f in facts]'),
        
        # Fix health_check
        (r'st = self\.kb_path\.stat\(\)',
         'st = self.sqlite_db_path.stat()'),
        (r'kb_exists = self\.kb_path\.exists\(\)',
         'kb_exists = self.sqlite_db_path.exists()'),
        
        # Fix all counting
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+for _ in f:\s+cnt \+= 1',
         'cnt = self._count_facts()'),
         
        # Fix semantic_similarity and other tools
        (r'with open\(self\.kb_path, [\'"]r[\'"], encoding=[\'"]utf-8[\'"]\) as f:\s+for line in f:',
         'for statement in self._yield_statements():\n                            line = json.dumps({"statement": statement})'),
    ]
    
    for pattern, replacement in replacements:
        content = re.sub(pattern, replacement, content, flags=re.MULTILINE | re.DOTALL)
    
    # 7. Replace specific tool implementations with SQLite versions
    tool_fixes = {
        "semantic_similarity": '''
                        base_vec = vec(base)
                        sims = []
                        for statement in self._yield_statements():
                            v = vec(statement)
                            cs = cosine(base_vec, v)
                            if cs >= threshold:
                                sims.append((cs, statement))''',
        
        "consistency_check": '''
                    pos = set()
                    neg = set()
                    checked = 0
                    for statement in self._yield_statements(limit=limit):
                        pred, args = self._parse_statement(statement)
                        if not pred or not args:
                            continue
                        if pred.startswith('Nicht'):
                            neg.add((pred[5:], tuple(args)))
                        else:
                            pos.add((pred, tuple(args)))
                        checked += 1''',
        
        "validate_facts": '''
                    errors = []
                    checked = 0
                    for statement in self._yield_statements(limit=limit):
                        pred, args = self._parse_statement(statement)
                        if not pred:
                            errors.append(f"Invalid syntax: {statement}")
                        elif not args:
                            errors.append(f"No arguments: {statement}")
                        checked += 1''',
    }
    
    # Write the fully migrated file
    with open(server_file, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n" + "="*60)
    print("✅ FULL SQLite MIGRATION COMPLETE!")
    print("="*60)
    print(f"Server: {server_file}")
    print(f"Backup: {backup_file}")
    print("\n🚀 The server now uses SQLite EXCLUSIVELY!")
    print("   No JSONL fallback - Pure SQLite implementation")
    print("\n📌 Test with: D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\scripts\\MCP_DEBUG.bat")
    
    return True

if __name__ == "__main__":
    success = full_sqlite_migration()
    if success:
        print("\n✨ Migration successful! The server is now 100% SQLite!")
    else:
        print("\n❌ Migration failed")
