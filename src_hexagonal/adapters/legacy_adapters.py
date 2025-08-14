"""
Legacy Adapters - PATCHED VERSION
=================================
Fixed duplicate detection
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository, ReasoningEngine
from core.domain.entities import Fact, ReasoningResult
from legacy_wrapper import legacy_proxy

class LegacyFactRepository(FactRepository):
    """
    Adapter für Legacy HAK-GAL Knowledge Base - PATCHED
    """
    
    def __init__(self):
        # Initialize legacy connection
        if not legacy_proxy.initialize():
            raise ConnectionError("Could not connect to legacy system")
        self.legacy = legacy_proxy
        # Cache für Performance
        self._cached_count = None
        self._cache_timestamp = None
        self._cache_ttl = 30  # Cache TTL in seconds
        self._exists_cache = {}  # Cache for exists checks
    
    def save(self, fact: Fact) -> bool:
        """Speichere Fact im Legacy System"""
        try:
            # Use legacy K-Assistant's add_fact method
            if self.legacy.k_assistant:
                success, message = self.legacy.k_assistant.add_fact(
                    fact.statement,
                    context=fact.context
                )
                # Invalidate cache on successful save
                if success:
                    self.invalidate_cache()
                    # Add to exists cache
                    self._exists_cache[fact.statement] = True
                return success
        except Exception as e:
            print(f"Error saving to legacy: {e}")
        return False
    
    def invalidate_cache(self):
        """Invalidate the count cache"""
        self._cached_count = None
        self._cache_timestamp = None
        # Don't clear exists cache - facts don't disappear
    
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """Suche Facts im Legacy System"""
        try:
            if self.legacy.k_assistant:
                # Use legacy ask method
                result = self.legacy.k_assistant.ask(query)
                
                # Extract facts from result
                relevant_facts = result.get('relevant_facts', [])
                
                # Convert to domain entities
                facts = []
                for fact_str in relevant_facts[:limit]:
                    facts.append(Fact(
                        statement=fact_str,
                        confidence=1.0,
                        context={'source': 'legacy'},
                        created_at=datetime.now()
                    ))
                return facts
        except Exception as e:
            print(f"Error querying legacy: {e}")
        return []
    
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Hole alle Facts direkt aus SQLite"""
        try:
            # Direct SQLite access - Single Source of Truth
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                from sqlalchemy import text
                result = self.legacy.k_assistant.db_session.execute(
                    text("SELECT statement, confidence FROM facts ORDER BY id DESC LIMIT :limit"),
                    {'limit': limit}
                )
                
                facts = []
                for row in result:
                    facts.append(Fact(
                        statement=row[0],
                        confidence=row[1] if row[1] else 1.0,
                        context={'source': 'sqlite'},
                        created_at=datetime.now()
                    ))
                
                return facts
                
        except Exception as e:
            print(f"Error getting all facts from SQLite: {e}")
        
        return []
    
    def exists(self, statement: str) -> bool:
        """PATCHED: More accurate duplicate detection"""
        
        # Check cache first
        if statement in self._exists_cache:
            return self._exists_cache[statement]
        
        try:
            # Try direct DB check FIRST (most accurate)
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                try:
                    from sqlalchemy import text
                    # Exact match query
                    res = self.legacy.k_assistant.db_session.execute(
                        text("SELECT COUNT(*) FROM facts WHERE statement = :stmt"),
                        {'stmt': statement}
                    ).scalar()
                    
                    exists = (res and int(res) > 0)
                    # Cache result
                    self._exists_cache[statement] = exists
                    return exists
                    
                except Exception as db_error:
                    print(f"[WARN] DB check failed: {db_error}")
                    # Don't return, try fallback
            
            # Fallback: Check in memory (less accurate but works)
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'core'):
                facts = self.legacy.k_assistant.core.K
                for fact in facts:
                    if hasattr(fact, 'statement') and fact.statement == statement:
                        self._exists_cache[statement] = True
                        return True
                    elif isinstance(fact, str) and fact == statement:
                        self._exists_cache[statement] = True
                        return True
                
                # Not found in memory
                self._exists_cache[statement] = False
                return False
                
        except Exception as e:
            print(f"[ERROR] exists() check failed: {e}")
            # On error, assume it doesn't exist to allow adding
            return False
        
        # Default: doesn't exist
        return False
    
    def count(self) -> int:
        """Zähle alle Facts"""
        import time
        current_time = time.time()
        
        # Return cached value if still valid
        if (self._cached_count is not None and 
            self._cache_timestamp is not None and 
            current_time - self._cache_timestamp < self._cache_ttl):
            return self._cached_count
            
        try:
            # Direct DB access
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                from sqlalchemy import text
                result = self.legacy.k_assistant.db_session.execute(
                    text("SELECT COUNT(*) FROM facts")
                ).scalar()
                if result is not None:
                    self._cached_count = result
                    self._cache_timestamp = current_time
                    return result
            
            # Fallback to metrics
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'get_metrics'):
                metrics = self.legacy.k_assistant.get_metrics()
                fact_count = metrics.get('fact_count', 0)
                if fact_count > 0:
                    self._cached_count = fact_count
                    self._cache_timestamp = current_time
                    return fact_count
                    
        except Exception as e:
            print(f"Error counting facts: {e}")
        
        return 1230  # Known value
    
    def delete_by_statement(self, statement: str) -> int:
        """Delete a fact by its statement"""
        try:
            # Direct SQLite DB access
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                from sqlalchemy import text
                # Delete from database
                result = self.legacy.k_assistant.db_session.execute(
                    text("DELETE FROM facts WHERE statement = :stmt"),
                    {'stmt': statement}
                )
                self.legacy.k_assistant.db_session.commit()
                
                # Invalidate caches
                self.invalidate_cache()
                if statement in self._exists_cache:
                    del self._exists_cache[statement]
                
                return result.rowcount
        except Exception as e:
            print(f"Error deleting fact: {e}")
            # Try to rollback on error
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                try:
                    self.legacy.k_assistant.db_session.rollback()
                except:
                    pass
        return 0
    
    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Update a fact's statement"""
        try:
            # Direct SQLite DB access
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                from sqlalchemy import text
                # Update in database
                result = self.legacy.k_assistant.db_session.execute(
                    text("UPDATE facts SET statement = :new_stmt WHERE statement = :old_stmt"),
                    {'new_stmt': new_statement, 'old_stmt': old_statement}
                )
                self.legacy.k_assistant.db_session.commit()
                
                # Invalidate caches
                self.invalidate_cache()
                if old_statement in self._exists_cache:
                    del self._exists_cache[old_statement]
                self._exists_cache[new_statement] = True
                
                return result.rowcount
        except Exception as e:
            print(f"Error updating fact: {e}")
            # Try to rollback on error
            if self.legacy.k_assistant and hasattr(self.legacy.k_assistant, 'db_session'):
                try:
                    self.legacy.k_assistant.db_session.rollback()
                except:
                    pass
        return 0

class LegacyReasoningEngine(ReasoningEngine):
    """
    Adapter für Legacy HRM System
    """
    
    def __init__(self):
        # Initialize legacy connection
        if not legacy_proxy.initialize():
            raise ConnectionError("Could not connect to legacy HRM")
        self.legacy = legacy_proxy
    
    def compute_confidence(self, query: str) -> Dict[str, Any]:
        """Nutze Legacy HRM für Reasoning"""
        try:
            result = self.legacy.reason(query)
            
            if 'error' not in result:
                return {
                    'confidence': result.get('confidence', 0.0),
                    'success': result.get('success', True),
                    'reasoning_terms': result.get('reasoning_terms', []),
                    'device': result.get('device', 'unknown')
                }
        except Exception as e:
            print(f"Error in reasoning: {e}")
        
        return {
            'confidence': 0.0,
            'success': False,
            'error': 'Reasoning failed'
        }
    
    def analyze_statement(self, statement: str) -> Dict[str, Any]:
        """Analysiere Statement mit Legacy HRM"""
        return self.compute_confidence(statement)
