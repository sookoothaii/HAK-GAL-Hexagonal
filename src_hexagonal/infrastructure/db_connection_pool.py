"""
Database Connection Pool for SQLite with better concurrency handling
"""

import sqlite3
import threading
import time
import queue
from contextlib import contextmanager
from typing import Optional, Any
import logging

logger = logging.getLogger(__name__)


class SQLiteConnectionPool:
    """
    Connection pool for SQLite with retry logic and WAL mode
    Handles database locking issues gracefully
    """
    
    def __init__(self, db_path: str, pool_size: int = 5, timeout: float = 30.0):
        self.db_path = db_path
        self.pool_size = pool_size
        self.timeout = timeout
        self._connections = queue.Queue(maxsize=pool_size)
        self._lock = threading.Lock()
        self._created_connections = 0
        
        # Initialize pool
        self._initialize_pool()
    
    def _initialize_pool(self):
        """Initialize the connection pool with WAL mode"""
        # Create first connection to set WAL mode
        conn = sqlite3.connect(self.db_path)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA cache_size=10000")
        conn.execute("PRAGMA temp_store=MEMORY")
        conn.execute("PRAGMA busy_timeout=30000")  # 30 second timeout
        conn.commit()
        self._connections.put(conn)
        self._created_connections = 1
        
        logger.info(f"Connection pool initialized with WAL mode for {self.db_path}")
    
    def _create_connection(self) -> sqlite3.Connection:
        """Create a new database connection"""
        conn = sqlite3.connect(self.db_path, timeout=self.timeout)
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.execute("PRAGMA busy_timeout=30000")
        return conn
    
    @contextmanager
    def get_connection(self, max_retries: int = 3):
        """
        Get a connection from the pool with retry logic
        
        Usage:
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(...)
        """
        connection = None
        attempts = 0
        
        while attempts < max_retries:
            try:
                # Try to get connection from pool
                if self._connections.empty() and self._created_connections < self.pool_size:
                    with self._lock:
                        if self._created_connections < self.pool_size:
                            connection = self._create_connection()
                            self._created_connections += 1
                else:
                    connection = self._connections.get(timeout=self.timeout)
                
                # Test connection
                connection.execute("SELECT 1")
                
                yield connection
                
                # Return connection to pool
                self._connections.put(connection)
                return
                
            except sqlite3.OperationalError as e:
                attempts += 1
                if "database is locked" in str(e):
                    logger.warning(f"Database locked, retry {attempts}/{max_retries}")
                    time.sleep(0.1 * attempts)  # Exponential backoff
                    
                    if connection:
                        try:
                            connection.close()
                        except:
                            pass
                        self._created_connections -= 1
                        connection = None
                else:
                    raise
            except Exception as e:
                if connection:
                    self._connections.put(connection)
                raise
        
        raise sqlite3.OperationalError(f"Database locked after {max_retries} retries")
    
    def execute_with_retry(self, query: str, params: tuple = (), max_retries: int = 3) -> Any:
        """
        Execute a query with automatic retry on lock
        """
        with self.get_connection(max_retries) as conn:
            cursor = conn.cursor()
            result = cursor.execute(query, params)
            conn.commit()
            return result.fetchall()
    
    def close_all(self):
        """Close all connections in the pool"""
        while not self._connections.empty():
            try:
                conn = self._connections.get_nowait()
                conn.close()
            except:
                pass
        
        self._created_connections = 0
        logger.info("All connections closed")


class PooledTransactionalGovernanceEngine:
    """
    Enhanced TransactionalGovernanceEngine with connection pooling
    """
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
        
        # Use connection pool instead of direct connections
        self.connection_pool = SQLiteConnectionPool(self.db_path, pool_size=10)
        
        # Initialize other components...
        from application.hardened_audit_logger import HardenedAuditLogger
        from application.hardened_policy_guard import HardenedPolicyGuard
        from application.transactional_governance_engine import StrictFactValidator
        
        self.audit_logger = HardenedAuditLogger()
        self.policy_guard = HardenedPolicyGuard()
        self.validator = StrictFactValidator()
        
        logger.info(f"PooledTransactionalGovernanceEngine initialized with connection pool")
    
    def add_facts_with_pool(self, facts: list, context: dict) -> int:
        """
        Add facts using connection pool to avoid locking
        """
        added = 0
        
        for fact in facts:
            try:
                # Check if fact already exists
                with self.connection_pool.get_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT COUNT(*) FROM facts_extended WHERE statement = ?",
                        (fact.rstrip('.'),)
                    )
                    exists = cursor.fetchone()[0] > 0
                
                if not exists:
                    # Add fact
                    with self.connection_pool.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("""
                            INSERT INTO facts_extended 
                            (statement, predicate, arg_count, fact_type, confidence, source, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, datetime('now'))
                        """, (
                            fact.rstrip('.'),
                            fact.split('(')[0] if '(' in fact else 'Unknown',
                            2,  # Default
                            'governed',
                            0.9,
                            'PooledEngine'
                        ))
                        conn.commit()
                        added += 1
                        
            except sqlite3.IntegrityError:
                # Duplicate - skip
                logger.debug(f"Duplicate fact skipped: {fact}")
            except Exception as e:
                logger.error(f"Failed to add fact: {e}")
        
        return added


# Global pool instance for reuse
_global_pool = None

def get_global_pool(db_path: str = None) -> SQLiteConnectionPool:
    """Get or create global connection pool"""
    global _global_pool
    if _global_pool is None:
        db_path = db_path or "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
        _global_pool = SQLiteConnectionPool(db_path)
    return _global_pool
