#!/usr/bin/env python3
"""
SQLite adapter methods for HAK_GAL MCP Server
These methods replace the JSONL file reading with SQLite queries
"""

import sqlite3
import json
import time
from pathlib import Path

class SQLiteAdapter:
    """Methods to add to HAKGALMCPServer for SQLite support"""
    
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
        except Exception as e:
            pass

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
        except Exception:
            return

    def _get_all_statements(self):
        """Get all statements from SQLite as a list"""
        statements = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT statement FROM facts ORDER BY id")
                statements = [row[0] for row in cursor.fetchall()]
        except Exception:
            pass
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
        except Exception:
            pass
        return facts

    def _count_facts(self):
        """Count total facts in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                cursor = conn.execute("SELECT COUNT(*) FROM facts")
                return cursor.fetchone()[0]
        except:
            return 0

    def _search_facts_sqlite(self, query, limit=10):
        """Search facts in SQLite"""
        results = []
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                # Simple LIKE search
                cursor = conn.execute(
                    "SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?",
                    (f"%{query}%", limit)
                )
                results = [row[0] for row in cursor.fetchall()]
        except:
            pass
        return results

    def _add_fact_sqlite(self, statement, source=None, confidence=1.0, tags=None):
        """Add a fact to SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                tags_json = json.dumps(tags) if tags else None
                conn.execute("""
                    INSERT OR IGNORE INTO facts (statement, source, confidence, timestamp, tags)
                    VALUES (?, ?, ?, ?, ?)
                """, (statement, source or "mcp", confidence, time.time(), tags_json))
                conn.commit()
                return conn.total_changes > 0
        except:
            return False

    def _delete_fact_sqlite(self, statement):
        """Delete a fact from SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute("DELETE FROM facts WHERE statement = ?", (statement,))
                conn.commit()
                return conn.total_changes
        except:
            return 0

    def _update_fact_sqlite(self, old_statement, new_statement):
        """Update a fact in SQLite"""
        try:
            with sqlite3.connect(str(self.sqlite_db_path)) as conn:
                conn.execute(
                    "UPDATE facts SET statement = ? WHERE statement = ?",
                    (new_statement, old_statement)
                )
                conn.commit()
                return conn.total_changes
        except:
            return 0

# Export as functions to patch into the main server
def patch_methods():
    """Returns the methods to patch into HAKGALMCPServer"""
    return {
        '_init_sqlite_db': SQLiteAdapter._init_sqlite_db,
        '_yield_statements': SQLiteAdapter._yield_statements,
        '_get_all_statements': SQLiteAdapter._get_all_statements,
        '_get_fact_objects': SQLiteAdapter._get_fact_objects,
        '_count_facts': SQLiteAdapter._count_facts,
        '_search_facts_sqlite': SQLiteAdapter._search_facts_sqlite,
        '_add_fact_sqlite': SQLiteAdapter._add_fact_sqlite,
        '_delete_fact_sqlite': SQLiteAdapter._delete_fact_sqlite,
        '_update_fact_sqlite': SQLiteAdapter._update_fact_sqlite,
    }
