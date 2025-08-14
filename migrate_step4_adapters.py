#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIGRATION STEP 4: Create New Native Adapters
============================================
Use local modules instead of legacy
"""

import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def create_native_adapters():
    """Create adapters that use local modules"""
    
    print("="*60)
    print("[STEP 4] CREATING NATIVE ADAPTERS")
    print("="*60)
    
    # Create native adapters
    adapters_code = '''"""
Native Adapters for HEXAGONAL
==============================
No dependency on HAK_GAL_SUITE!
"""

import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Use local modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.ports.interfaces import FactRepository, ReasoningEngine
from core.domain.entities import Fact, ReasoningResult
from core.knowledge.k_assistant import get_k_assistant
from core.reasoning.hrm_system import get_hrm_instance

class NativeFactRepository(FactRepository):
    """Native implementation using local KAssistant"""
    
    def __init__(self, db_path: str = "k_assistant_dev.db"):
        self.k_assistant = get_k_assistant(db_path)
        
    def save(self, fact: Fact) -> bool:
        """Save a fact"""
        success, _ = self.k_assistant.add_fact(
            fact.statement,
            fact.confidence,
            fact.context.get('source', 'hexagonal')
        )
        return success
    
    def find_by_query(self, query: str, limit: int = 10) -> List[Fact]:
        """Search for facts"""
        results = self.k_assistant.search_facts(query, limit)
        
        facts = []
        for result in results:
            facts.append(Fact(
                statement=result['statement'],
                confidence=result.get('confidence', 1.0),
                context={'source': 'native'},
                created_at=datetime.now()
            ))
        return facts
    
    def find_all(self, limit: int = 100) -> List[Fact]:
        """Get all facts"""
        statements = self.k_assistant.get_all_facts(limit)
        
        facts = []
        for statement in statements:
            facts.append(Fact(
                statement=statement,
                confidence=1.0,
                context={'source': 'native'},
                created_at=datetime.now()
            ))
        return facts
    
    def exists(self, statement: str) -> bool:
        """Check if fact exists"""
        results = self.k_assistant.search_facts(statement, limit=1)
        return any(r['statement'] == statement for r in results)
    
    def count(self) -> int:
        """Count facts"""
        metrics = self.k_assistant.get_metrics()
        return metrics.get('fact_count', 0)
    
    def delete_by_statement(self, statement: str) -> int:
        """Delete a fact (not implemented in simplified version)"""
        # Would need to add delete method to KAssistant
        return 0
    
    def update_statement(self, old_statement: str, new_statement: str) -> int:
        """Update a fact (not implemented in simplified version)"""
        # Would need to add update method to KAssistant
        return 0

class NativeReasoningEngine(ReasoningEngine):
    """Native implementation using local HRM"""
    
    def __init__(self):
        self.hrm = get_hrm_instance()
    
    def compute_confidence(self, query: str) -> Dict[str, Any]:
        """Compute confidence for a query"""
        return self.hrm.reason(query)
    
    def analyze_statement(self, statement: str) -> Dict[str, Any]:
        """Analyze a statement"""
        return self.hrm.reason(statement)
'''
    
    # Save native adapters
    output_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/adapters/native_adapters.py")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(adapters_code)
    
    print(f"[OK] Created: {output_path}")
    
    print("\n" + "="*60)
    print("[SUCCESS] NATIVE ADAPTERS CREATED!")
    print("="*60)

if __name__ == '__main__':
    try:
        create_native_adapters()
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
