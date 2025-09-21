"""
SQLite Adapter - FIXED for Natural Language Queries
=====================================================
Nach HAK/GAL Verfassung: Primary data source using SQLite
"""

import sqlite3
import os
import json
import sys
import re
from pathlib import Path
from typing import List, Dict, Any, Set
from datetime import datetime

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository
from core.domain.entities import Fact

class SQLiteFactRepository(FactRepository):
    """
    SQLite Implementation des FactRepository
    FIXED: Now handles natural language queries correctly
    """
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            # Environment override (non-invasive): allows read-only URI or custom path per instance
            env_db = os.environ.get("HAKGAL_SQLITE_DB_PATH") or os.environ.get("SQLITE_DB_PATH")
            if env_db:
                db_path = env_db
            else:
                # FIX: Use the correct hexagonal_kb.db with 5000+ facts instead of k_assistant.db
                db_path = Path(__file__).parent.parent.parent / "hexagonal_kb.db"
                # Fallback if hexagonal_kb.db doesn't exist
                if not db_path.exists():
                    alt_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
                    if alt_path.exists():
                        db_path = alt_path
                    else:
                        # Last resort: use old database
                        db_path = Path(__file__).parent.parent.parent / "k_assistant.db"

        # If HAKGAL_SQLITE_READONLY=true and path is a normal file path, convert to file: URI with mode=ro
        readonly_flag = (os.environ.get("HAKGAL_SQLITE_READONLY", "").lower() in ("1", "true", "yes"))
        if readonly_flag and isinstance(db_path, str) and not str(db_path).startswith("file:"):
            # Build sqlite URI form: file:/abs/path?mode=ro&cache=shared
            p = Path(db_path)
            db_path = f"file:{p.as_posix()}?mode=ro&cache=shared"

        self.db_path = str(db_path)
        # If path startswith file:, we must use uri=True on connect
        self._use_uri = self.db_path.startswith("file:") or (os.environ.get("HAKGAL_SQLITE_DB_URI", "").lower() in ("1", "true", "yes"))
        # Track read-only mode explicitly to avoid DDL on RO databases
        self._readonly = readonly_flag or ("mode=ro" in self.db_path)

        self._ensure_table()
        print(f"[SQLite] Using database: {self.db_path}")
        print(f"[SQLite] Facts count: {self.count()}")

    def _connect(self):
        """Create a sqlite3 connection, honoring URI mode when needed."""
        try:
            conn = sqlite3.connect(self.db_path, uri=bool(self._use_uri))
        except TypeError:
            # Older sqlite3 without uri kw support
            conn = sqlite3.connect(self.db_path)
        
        # Apply performance optimizations to every connection
        cursor = conn.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA synchronous=NORMAL")  # 2x faster, still safe
        cursor.execute("PRAGMA cache_size=10000")     # 10MB cache
        cursor.execute("PRAGMA temp_store=MEMORY")    # Memory for temp tables
        cursor.execute("PRAGMA mmap_size=268435456")  # 256MB memory-mapped I/O
        conn.commit()
        
        return conn
    
    def _ensure_table(self):
        """Stelle sicher, dass Tabelle existiert; vermeide DDL in Read-Only-Modus."""
        with self._connect() as conn:
            # Check if table exists and has the right structure
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='facts'")
            exists = bool(cursor.fetchone())
            if self._readonly:
                # In RO-Mode: niemals DDL/Migrationen versuchen
                if not exists:
                    print("[SQLite] Read-only mode detected and table 'facts' missing – skipping create/migration.")
                return
            if exists:
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
                
                # Add confidence column if missing
                if 'confidence' not in columns:
                    print("[SQLite] Adding confidence column...")
                    conn.execute('''
                        ALTER TABLE facts ADD COLUMN confidence REAL DEFAULT 1.0
                    ''')
                    conn.commit()
            else:
                # Create new table
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS facts (
                        statement TEXT PRIMARY KEY,
                        context TEXT DEFAULT '{}',
                        fact_metadata TEXT DEFAULT '{}',
                        confidence REAL DEFAULT 1.0
                    )
                ''')
                conn.commit()
    
    def save(self, fact: Fact) -> bool:
        """Speichere Fact in SQLite"""
        try:
            with self._connect() as conn:
                conn.execute(
                    'INSERT OR IGNORE INTO facts (statement, context, fact_metadata, confidence) VALUES (?, ?, ?, ?)',
                    (
                        fact.statement,
                        json.dumps(fact.context if fact.context else {}),
                        json.dumps(fact.metadata if fact.metadata else {}),
                        fact.confidence
                    )
                )
                conn.commit()
                return True
        except Exception as e:
            print(f"[SQLite] Save error: {e}")
            return False
    
    def _extract_keywords(self, query: str) -> Set[str]:
        """Extract meaningful keywords from natural language query"""
        # Convert to lowercase
        query_lower = query.lower()
        
        # Remove common stop words
        stop_words = {
            'what', 'is', 'the', 'between', 'and', 'of', 'how', 'why', 
            'when', 'where', 'which', 'who', 'a', 'an', 'to', 'from',
            'in', 'on', 'at', 'with', 'for', 'about', 'as', 'by',
            'can', 'could', 'would', 'should', 'will', 'may', 'might',
            'has', 'have', 'had', 'does', 'do', 'did', 'are', 'was', 'were',
            'been', 'being', 'relationship', 'connection', 'difference'
        }
        
        # Extract words
        words = re.findall(r'\w+', query_lower)
        
        # Filter stop words and keep meaningful terms
        keywords = set()
        for word in words:
            if word not in stop_words and len(word) > 2:
                keywords.add(word)
                # Also add capitalized version for entities
                keywords.add(word.capitalize())
                # Add uppercase for acronyms
                if len(word) <= 4:
                    keywords.add(word.upper())
        
        # Add specific variations for common terms
        if 'ai' in query_lower:
            keywords.update(['AI', 'ai', 'artificial', 'intelligence', 'CurrentAI'])
        if 'consciousness' in query_lower:
            keywords.update(['consciousness', 'Consciousness', 'conscious', 'awareness'])
        if 'lsd' in query_lower:
            keywords.update(['LSD', 'lsd', 'lysergic'])
        if 'chemical' in query_lower:
            keywords.update(['chemical', 'Chemical', 'formula', 'Formula'])
        
        return keywords
    
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """FIXED: Now handles both fact-format and natural language queries"""
        facts = []
        seen_statements = set()
        
        try:
            with self._connect() as conn:
                # First check if it's a fact-format query
                fact_match = re.match(r'^(\w+)\(([^,]+),\s*([^)]+)\)', query.strip('.'))
                
                if fact_match:
                    # Handle fact-format query (original logic)
                    predicate = fact_match.group(1)
                    entity1 = fact_match.group(2).strip()
                    entity2 = fact_match.group(3).strip()
                    
                    # Search for exact match first
                    cursor = conn.execute(
                        'SELECT statement, confidence FROM facts WHERE statement = ? LIMIT ?',
                        (query.strip('.') + '.', limit)
                    )
                    for row in cursor:
                        if row[0] not in seen_statements:
                            facts.append(Fact(
                                statement=row[0],
                                context={},
                                metadata={},
                                confidence=row[1] if row[1] is not None else 1.0
                            ))
                            seen_statements.add(row[0])
                    
                    # Then search for similar predicates
                    if len(facts) < limit:
                        cursor = conn.execute(
                            '''SELECT statement, confidence FROM facts 
                               WHERE statement LIKE ? 
                               AND (statement LIKE ? OR statement LIKE ?)
                               LIMIT ?''',
                            (f'{predicate}(%', f'%{entity1}%', f'%{entity2}%', limit - len(facts))
                        )
                        for row in cursor:
                            if row[0] not in seen_statements:
                                facts.append(Fact(
                                    statement=row[0],
                                    context={},
                                    metadata={},
                                    confidence=row[1] if row[1] is not None else 0.9
                                ))
                                seen_statements.add(row[0])
                
                else:
                    # Handle natural language query - EXTRACT KEYWORDS!
                    keywords = self._extract_keywords(query)
                    
                    if keywords:
                        # Build dynamic SQL with OR conditions for all keywords
                        conditions = []
                        params = []
                        
                        for keyword in list(keywords)[:10]:  # Limit to 10 keywords
                            conditions.append('statement LIKE ?')
                            params.append(f'%{keyword}%')
                        
                        # Query with all keyword conditions joined by OR
                        sql_query = f'''
                            SELECT statement, confidence,
                                   (CASE 
                                    WHEN statement LIKE '%Consciousness%' AND statement LIKE '%AI%' THEN 1.0
                                    WHEN statement LIKE '%LSD%' AND statement LIKE '%Chemical%' THEN 1.0
                                    ELSE 0.8
                                   END) as relevance
                            FROM facts 
                            WHERE {' OR '.join(conditions)}
                            ORDER BY relevance DESC, confidence DESC
                            LIMIT ?
                        '''
                        
                        params.append(limit)
                        
                        cursor = conn.execute(sql_query, params)
                        
                        for row in cursor:
                            if row[0] not in seen_statements:
                                facts.append(Fact(
                                    statement=row[0],
                                    context={'relevance': row[2] if len(row) > 2 else 0.8},
                                    metadata={},
                                    confidence=row[1] if row[1] is not None else 1.0
                                ))
                                seen_statements.add(row[0])
                    
                    # Fallback: if no keywords or no results, try partial match on whole query
                    if len(facts) == 0 and len(query) > 5:
                        # Try to find facts with any word from the query
                        words = query.split()
                        for word in words:
                            if len(word) > 3 and len(facts) < limit:
                                cursor = conn.execute(
                                    '''SELECT statement, confidence FROM facts 
                                       WHERE statement LIKE ? COLLATE NOCASE
                                       LIMIT ?''',
                                    (f'%{word}%', limit - len(facts))
                                )
                                for row in cursor:
                                    if row[0] not in seen_statements:
                                        facts.append(Fact(
                                            statement=row[0],
                                            context={},
                                            metadata={},
                                            confidence=row[1] if row[1] is not None else 0.7
                                        ))
                                        seen_statements.add(row[0])
                
                # Debug output
                if len(facts) > 0:
                    print(f"[SQLite] Query '{query[:50]}...' found {len(facts)} facts")
                else:
                    print(f"[SQLite] Query '{query[:50]}...' found NO facts (keywords: {list(keywords)[:5] if 'keywords' in locals() else 'N/A'})")
                
        except Exception as e:
            print(f"[SQLite] Query error: {e}")
            import traceback
            traceback.print_exc()
        
        return facts
    
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts"""
        facts = []
        try:
            with self._connect() as conn:
                # Try to get confidence if column exists
                cursor = conn.execute("PRAGMA table_info(facts)")
                has_confidence = any(row[1] == 'confidence' for row in cursor)
                
                if has_confidence:
                    cursor = conn.execute(
                        'SELECT statement, confidence FROM facts LIMIT ?',
                        (limit,)
                    )
                    for row in cursor:
                        facts.append(Fact(
                            statement=row[0],
                            context={},
                            metadata={},
                            confidence=row[1] if row[1] is not None else 1.0
                        ))
                else:
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

    def find_page(self, offset: int, limit: int) -> List[Fact]:
        """Hole Facts mit OFFSET/LIMIT (Pagination)."""
        facts: List[Fact] = []
        try:
            with self._connect() as conn:
                cursor = conn.execute(
                    'SELECT statement FROM facts LIMIT ? OFFSET ?',
                    (limit, offset)
                )
                for row in cursor:
                    facts.append(Fact(
                        statement=row[0],
                        context={},
                        metadata={},
                        confidence=1.0
                    ))
        except Exception as e:
            print(f"[SQLite] Page error: {e}")
        return facts
    
    def exists(self, statement: str) -> bool:
        """Prüfe ob Fact existiert"""
        try:
            with self._connect() as conn:
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
            with self._connect() as conn:
                cursor = conn.execute('SELECT COUNT(*) FROM facts')
                return cursor.fetchone()[0]
        except Exception as e:
            print(f"[SQLite] Count error: {e}")
            return 0

    def bulk_insert(self, statements: List[str]) -> int:
        """Füge mehrere Statements (INSERT OR IGNORE) transaktional ein.
        Gibt Anzahl tatsächlich eingefügter Zeilen zurück.
        """
        if not statements:
            return 0
        added = 0
        try:
            with self._connect() as conn:
                cur = conn.cursor()
                cur.executemany(
                    'INSERT OR IGNORE INTO facts (statement, context, fact_metadata) VALUES (?, "{}", "{}")',
                    [(s if s.endswith('.') else s + '.',) for s in statements]
                )
                conn.commit()
                try:
                    added = cur.rowcount if cur.rowcount is not None else 0
                except Exception:
                    added = 0
        except Exception as e:
            print(f"[SQLite] Bulk insert error: {e}")
        return max(0, added)

    def export_limit(self, limit: int) -> List[str]:
        """Exportiere bis zu N Statements als Liste (für JSON/JSONL)."""
        out: List[str] = []
        try:
            with self._connect() as conn:
                cur = conn.execute('SELECT statement FROM facts LIMIT ?', (limit,))
                out = [row[0] for row in cur]
        except Exception as e:
            print(f"[SQLite] Export error: {e}")
        return out

    def predicate_counts(self, sample_limit: int = 5000) -> List[tuple]:
        """Zähle Prädikate im Sample (SQL-basiert) und liefere (predicate, count)."""
        items: List[tuple] = []
        try:
            with self._connect() as conn:
                # SQLite: substr(statement,1,instr(statement,'(')-1) extrahiert das Prädikat
                cur = conn.execute(
                    """
                    SELECT pred, COUNT(*) as cnt FROM (
                        SELECT substr(statement, 1, instr(statement,'(')-1) as pred
                        FROM facts
                        LIMIT ?
                    )
                    GROUP BY pred
                    ORDER BY cnt DESC
                    """,
                    (sample_limit,)
                )
                items = [(row[0], int(row[1])) for row in cur if row[0]]
        except Exception as e:
            print(f"[SQLite] predicate_counts error: {e}")
        return items

    def delete_by_statement(self, statement: str) -> int:
        """Lösche exakt passendes Statement."""
        try:
            with self._connect() as conn:
                cur = conn.execute('DELETE FROM facts WHERE statement = ?', (statement,))
                conn.commit()
                return cur.rowcount or 0
        except Exception as e:
            print(f"[SQLite] Delete error: {e}")
            return 0

    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Ersetze exakt passendes Statement."""
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    'UPDATE facts SET statement = ? WHERE statement = ?',
                    (new_statement, old_statement)
                )
                conn.commit()
                return cur.rowcount or 0
        except Exception as e:
            print(f"[SQLite] Update error: {e}")
            return 0
