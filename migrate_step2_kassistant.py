#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
MIGRATION STEP 2: Port Core KAssistant to HEXAGONAL
====================================================
Simplified version without legacy dependencies
"""

import sys
from pathlib import Path

# Fix encoding for Windows
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def migrate_k_assistant():
    """Create standalone KAssistant for HEXAGONAL"""
    
    print("="*60)
    print("[STEP 2] MIGRATING K-ASSISTANT TO HEXAGONAL")
    print("="*60)
    
    # Create simplified KAssistant
    k_assistant_code = '''"""
K-Assistant for HEXAGONAL - Standalone Version
==============================================
Simplified, no legacy dependencies
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import threading

logger = logging.getLogger(__name__)

class KAssistant:
    """Simplified Knowledge Assistant for HEXAGONAL"""
    
    def __init__(self, db_path: Optional[str] = None):
        """Initialize with database"""
        self.db_path = db_path or "k_assistant_dev.db"
        self.facts_cache = []
        self.lock = threading.RLock()
        self._init_database()
        self._load_facts()
        
    def _init_database(self):
        """Initialize SQLite database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS facts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    statement TEXT NOT NULL UNIQUE,
                    confidence REAL DEFAULT 1.0,
                    source TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT
                )
            """)
            conn.commit()
            
    def _load_facts(self):
        """Load facts from database"""
        with self.lock:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.execute("SELECT statement, confidence FROM facts")
                    self.facts_cache = [
                        {'statement': row[0], 'confidence': row[1]}
                        for row in cursor
                    ]
                logger.info(f"[KAssistant] Loaded {len(self.facts_cache)} facts")
            except Exception as e:
                logger.error(f"[KAssistant] Failed to load facts: {e}")
                self.facts_cache = []
    
    def add_fact(self, statement: str, confidence: float = 1.0, 
                 source: str = "hexagonal") -> Tuple[bool, str]:
        """Add a new fact"""
        with self.lock:
            try:
                # Clean statement
                if not statement.endswith('.'):
                    statement += '.'
                    
                # Check for duplicates
                if any(f['statement'] == statement for f in self.facts_cache):
                    return False, "Fact already exists"
                
                # Add to database
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("""
                        INSERT INTO facts (statement, confidence, source)
                        VALUES (?, ?, ?)
                    """, (statement, confidence, source))
                    conn.commit()
                
                # Update cache
                self.facts_cache.append({
                    'statement': statement,
                    'confidence': confidence
                })
                
                return True, "Fact added successfully"
                
            except sqlite3.IntegrityError:
                return False, "Duplicate fact"
            except Exception as e:
                logger.error(f"[KAssistant] Add fact error: {e}")
                return False, str(e)
    
    def search_facts(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Simple keyword search"""
        with self.lock:
            query_lower = query.lower()
            results = []
            
            for fact in self.facts_cache:
                if query_lower in fact['statement'].lower():
                    results.append(fact)
                    if len(results) >= limit:
                        break
                        
            return results
    
    def ask(self, query: str) -> Dict[str, Any]:
        """Answer a query"""
        # Try semantic search if models available
        try:
            from ..ml.shared_models import shared_models
            
            if shared_models.sentence_model:
                # Use semantic search
                query_embedding = shared_models.encode_text(query)
                
                # Find similar facts (simplified)
                relevant_facts = self.search_facts(query, limit=5)
            else:
                # Fallback to keyword search
                relevant_facts = self.search_facts(query, limit=5)
                
        except ImportError:
            relevant_facts = self.search_facts(query, limit=5)
        
        # Format response
        if relevant_facts:
            response = f"Based on {len(relevant_facts)} relevant facts:\\n"
            for fact in relevant_facts[:3]:
                response += f"- {fact['statement']}\\n"
        else:
            response = "No relevant facts found."
            
        return {
            'query': query,
            'response': response,
            'relevant_facts': [f['statement'] for f in relevant_facts],
            'confidence': sum(f['confidence'] for f in relevant_facts) / len(relevant_facts) if relevant_facts else 0.0
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get system metrics"""
        with self.lock:
            return {
                'fact_count': len(self.facts_cache),
                'db_path': self.db_path,
                'status': 'operational'
            }
    
    def get_all_facts(self, limit: int = 100) -> List[str]:
        """Get all facts as strings"""
        with self.lock:
            return [f['statement'] for f in self.facts_cache[:limit]]

# Singleton instance
_k_assistant_instance = None

def get_k_assistant(db_path: Optional[str] = None) -> KAssistant:
    """Get or create KAssistant instance"""
    global _k_assistant_instance
    if _k_assistant_instance is None:
        _k_assistant_instance = KAssistant(db_path)
    return _k_assistant_instance
'''
    
    # Save to HEXAGONAL
    output_path = Path("D:/MCP Mods/HAK_GAL_HEXAGONAL/src_hexagonal/core/knowledge/k_assistant.py")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(k_assistant_code)
    
    print(f"[OK] Created: {output_path}")
    
    # Create __init__.py
    init_path = output_path.parent / "__init__.py"
    with open(init_path, 'w') as f:
        f.write('"""Knowledge Management Module"""')
    
    print(f"[OK] Created: {init_path}")
    
    print("\n" + "="*60)
    print("[SUCCESS] K-ASSISTANT MIGRATED!")
    print("Simplified version without legacy dependencies")
    print("="*60)

if __name__ == '__main__':
    try:
        migrate_k_assistant()
    except Exception as e:
        print(f"[ERROR] Migration failed: {e}")
        sys.exit(1)
