"""
HEXAGONAL Database Infrastructure
==================================
Database access layer for knowledge base
"""

import sqlite3
from pathlib import Path
from typing import List, Dict, Any, Optional
import json
import logging

logger = logging.getLogger(__name__)


class KnowledgeBaseRepository:
    """
    Repository for knowledge base access
    Implements database operations for facts
    """
    
    def __init__(self, db_path: str = None):
        """Initialize repository with database path"""
        if db_path is None:
            # Default to data directory
            db_path = Path(__file__).parent.parent.parent.parent / "data" / "k_assistant.db"
        
        self.db_path = Path(db_path)
        self.ensure_database()
        
    def ensure_database(self):
        """Ensure database exists with proper schema"""
        if not self.db_path.parent.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
        
        if not self.db_path.exists():
            self.create_database()
            logger.info(f"Created new database at {self.db_path}")
    
    def create_database(self):
        """Create database with schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Create facts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                statement TEXT NOT NULL UNIQUE,
                confidence REAL DEFAULT 1.0,
                source TEXT,
                context TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_statement ON facts(statement)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_confidence ON facts(confidence)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_facts_created ON facts(created_at)")
        
        conn.commit()
        conn.close()
    
    def add_fact(self, statement: str, confidence: float = 1.0, 
                 source: str = None, context: Dict = None) -> Dict[str, Any]:
        """
        Add a fact to the knowledge base
        
        Args:
            statement: Fact statement (e.g., "IsA(Socrates, Philosopher).")
            confidence: Confidence score (0-1)
            source: Source of the fact
            context: Additional context
            
        Returns:
            Created fact with ID
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        try:
            context_json = json.dumps(context) if context else None
            
            cursor.execute("""
                INSERT INTO facts (statement, confidence, source, context)
                VALUES (?, ?, ?, ?)
            """, (statement, confidence, source, context_json))
            
            conn.commit()
            fact_id = cursor.lastrowid
            
            return {
                'id': fact_id,
                'statement': statement,
                'confidence': confidence,
                'source': source,
                'context': context
            }
            
        except sqlite3.IntegrityError:
            # Duplicate fact
            cursor.execute("""
                SELECT id, confidence FROM facts WHERE statement = ?
            """, (statement,))
            
            existing = cursor.fetchone()
            if existing:
                return {
                    'id': existing[0],
                    'statement': statement,
                    'confidence': existing[1],
                    'duplicate': True
                }
        finally:
            conn.close()
    
    def get_facts(self, limit: int = 1000, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get facts from knowledge base
        
        Args:
            limit: Maximum number of facts
            offset: Offset for pagination
            
        Returns:
            List of facts
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, statement, confidence, source, context, created_at
            FROM facts
            ORDER BY id
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        facts = []
        for row in cursor.fetchall():
            fact = dict(row)
            if fact['context']:
                fact['context'] = json.loads(fact['context'])
            facts.append(fact)
        
        conn.close()
        return facts
    
    def search_facts(self, query: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Search facts by pattern
        
        Args:
            query: Search query
            limit: Maximum results
            
        Returns:
            Matching facts
        """
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Simple pattern matching (can be enhanced with FTS)
        cursor.execute("""
            SELECT id, statement, confidence, source, context, created_at
            FROM facts
            WHERE statement LIKE ?
            ORDER BY confidence DESC
            LIMIT ?
        """, (f"%{query}%", limit))
        
        facts = []
        for row in cursor.fetchall():
            fact = dict(row)
            if fact['context']:
                fact['context'] = json.loads(fact['context'])
            facts.append(fact)
        
        conn.close()
        return facts
    
    def get_fact_count(self) -> int:
        """Get total number of facts"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM facts")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def delete_fact(self, fact_id: int) -> bool:
        """Delete a fact by ID"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM facts WHERE id = ?", (fact_id,))
        deleted = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return deleted
    
    def update_confidence(self, fact_id: int, confidence: float) -> bool:
        """Update fact confidence"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE facts 
            SET confidence = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (confidence, fact_id))
        
        updated = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return updated
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        stats = {}
        
        # Total facts
        cursor.execute("SELECT COUNT(*) FROM facts")
        stats['total_facts'] = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM facts")
        stats['avg_confidence'] = cursor.fetchone()[0] or 0
        
        # Fact sources
        cursor.execute("""
            SELECT source, COUNT(*) as count 
            FROM facts 
            WHERE source IS NOT NULL 
            GROUP BY source
        """)
        stats['sources'] = dict(cursor.fetchall())
        
        # Recent facts
        cursor.execute("""
            SELECT COUNT(*) FROM facts 
            WHERE datetime(created_at) > datetime('now', '-1 hour')
        """)
        stats['recent_facts'] = cursor.fetchone()[0]
        
        conn.close()
        return stats


# Singleton instance
_repository_instance = None

def get_knowledge_repository(db_path: str = None) -> KnowledgeBaseRepository:
    """Get or create repository singleton"""
    global _repository_instance
    if _repository_instance is None:
        _repository_instance = KnowledgeBaseRepository(db_path)
    return _repository_instance
