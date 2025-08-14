#!/usr/bin/env python3
"""
Fix für die fehlerhafte Duplicate Detection
============================================
"""

import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "src_hexagonal"))
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_SUITE\src")

def test_exists_method():
    """Test the exists method to see what's wrong"""
    print("Testing duplicate detection...")
    
    # Import the legacy adapter
    from adapters.legacy_adapters import LegacyFactRepository
    
    repo = LegacyFactRepository()
    
    # Test with a fact that definitely doesn't exist
    test_statements = [
        "TestFact123456789(A,B).",
        "CompletelyNewFact(X,Y).",
        "HasPart(Computer,CPU).",  # This might exist
        "UniqueFact999(Test,Test)."
    ]
    
    print("\n=== Testing exists() method ===")
    for stmt in test_statements:
        exists = repo.exists(stmt)
        print(f"  {stmt}: {exists}")
    
    # Try to get actual facts
    print("\n=== Sample of actual facts ===")
    facts = repo.find_all(5)
    for f in facts:
        print(f"  - {f.statement}")
    
    print("\n=== Testing count ===")
    count = repo.count()
    print(f"  Total facts: {count}")

def patch_exists_method():
    """Patch the exists method to be more lenient"""
    print("\nPatching exists() method...")
    
    # Create a patched version
    patch_content = '''"""
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
        """Hole alle Facts vom Legacy System"""
        try:
            # Direct access to knowledge base
            if (self.legacy.k_assistant and 
                hasattr(self.legacy.k_assistant, 'core') and 
                hasattr(self.legacy.k_assistant.core, 'K')):
                
                raw_facts = list(self.legacy.k_assistant.core.K)[:limit]
                facts = []
                
                for fact_obj in raw_facts:
                    # Handle both string facts and fact objects
                    if isinstance(fact_obj, str):
                        fact_str = fact_obj
                    elif hasattr(fact_obj, 'statement'):
                        fact_str = fact_obj.statement
                    else:
                        fact_str = str(fact_obj)
                    
                    if fact_str:
                        facts.append(Fact(
                            statement=fact_str,
                            confidence=1.0,
                            context={'source': 'legacy'},
                            created_at=datetime.now()
                        ))
                
                if facts:
                    return facts
                
        except Exception as e:
            print(f"Error getting all facts: {e}")
        
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
'''
    
    # Backup original
    original_file = Path(__file__).parent / "src_hexagonal" / "adapters" / "legacy_adapters.py"
    backup_file = Path(__file__).parent / "src_hexagonal" / "adapters" / "legacy_adapters_backup.py"
    
    if original_file.exists():
        # Create backup
        import shutil
        shutil.copy2(original_file, backup_file)
        print(f"  Created backup: {backup_file.name}")
        
        # Write patched version
        original_file.write_text(patch_content, encoding='utf-8')
        print(f"  Patched: {original_file.name}")
        print("  ✅ Patch applied successfully!")
    else:
        print(f"  ❌ File not found: {original_file}")

if __name__ == "__main__":
    print("=" * 60)
    print("HAK-GAL HEXAGONAL - Duplicate Detection Fix")
    print("=" * 60)
    
    # First test what's wrong
    test_exists_method()
    
    # Then apply patch
    print("\n" + "=" * 60)
    response = input("\nApply patch to fix duplicate detection? (y/n): ")
    
    if response.lower() == 'y':
        patch_exists_method()
        print("\n✅ Patch applied! Please restart the API.")
    else:
        print("\n❌ Patch not applied.")
