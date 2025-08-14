"""
SQLite Adapter - Production Database Implementation
=====================================================
Nach HAK/GAL Verfassung: Primary data source using SQLite
"""

import sqlite3
import json
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository
from core.domain.entities import Fact

class SQLiteFactRepository(FactRepository):
    """
    SQLite Implementation des FactRepository
    Uses production database k_assistant.db
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Use production database instead of dev
            db_path = Path(__file__).parent.parent.parent / "k_assistant.db"
        
        self.db_path = str(db_path)
        self._ensure_table()
        print(f"[SQLite] Using database: {self.db_path}")
        print(f"[SQLite] Facts count: {self.count()}")
    
    def _ensure_table(self):
        """Stelle sicher dass Table existiert"""
        with sqlite3.connect(self.db_path) as conn:
            # Check if table exists and has the right structure
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts'")
            if cursor.fetchone():
                # Table exists, check columns
                cursor = conn.execute("PRAGMA table_info(facts)")
                columns = {row[1] for row in cursor}
                
                # If old structure, migrate
                if 'context' not in columns:
                    print("[SQLite] Migrating table structure...")
                    conn.execute('''
                        ALTER TABLE facts ADD COLUMN context TEXT DEFAULT '{}'
                    ''')
                    conn.execute('''
                        ALTER TABLE facts ADD COLUMN fact_metadata TEXT DEFAULT '{}'
                    ''')
                    conn.commit()
            else:
                # Create new table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS facts (
                        statement TEXT PRIMARY KEY,
                        context TEXT DEFAULT '{}',
                        fact_metadata TEXT DEFAULT '{}'
                    )
                ''')
                conn.commit()
    
    def save(self, fact: Fact) -> bool:
        """Speichere Fact in SQLite"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    'INSERT OR IGNORE INTO facts (statement, context, fact_metadata) VALUES (?, ?, ?)',
                    (
                        fact.statement,
                        json.dumps(fact.context if fact.context else {}),
                        json.dumps(fact.metadata if fact.metadata else {})
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"[SQLite] Save error: {e}")
            return False
    
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """Suche Facts mit LIKE Query"""
        facts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT statement FROM facts WHERE statement LIKE ? LIMIT ?',
                    (f'%{query}%', limit)
                )
                
                for row in cursor:
                    facts.append(Fact(
                        statement=row[0],
                        context={},
                        metadata={},
                        confidence=1.0
                    ))
        except Exception as e:
            print(f"[SQLite] Query error: {e}")
        
        return facts
    
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts"""
        facts = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT statement FROM facts LIMIT ?',
                    (limit,)
                )
                
                for row in cursor:
                    facts.append(Fact(
                        statement=row[0],
                        context={},
                        metadata={},
                        confidence=1.0
                    ))
        except Exception as e:
            print(f"[SQLite] Find_all error: {e}")
        
        return facts
    
    def exists(self, statement: str) -> bool:
        """Prüfe ob Fact existiert"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute(
                    'SELECT COUNT(*) FROM facts WHERE statement = ?',
                    (statement,)
                )
                count = cursor.fetchone()[0]
                return count > 0
        except Exception as e:
            print(f"[SQLite] Exists error: {e}")
            return False
    
    def count(self) -> int:
        """Zähle alle Facts"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM facts')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"[SQLite] Count error: {e}")
            return 0

    def delete_by_statement(self, statement: str) -> int:
        """Lösche exakt passendes Statement."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute('DELETE FROM facts WHERE statement = ?', (statement,))
                conn.commit()
                return cur.rowcount or 0
        except Exception as e:
            print(f"[SQLite] Delete error: {e}")
            return 0

    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Ersetze exakt passendes Statement."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cur = conn.execute(
                    'UPDATE facts SET statement = ? WHERE statement = ?',
                    (new_statement, old_statement)
                )
                conn.commit()
                return cur.rowcount or 0
        except Exception as e:
            print(f"[SQLite] Update error: {e}")
            return 0
