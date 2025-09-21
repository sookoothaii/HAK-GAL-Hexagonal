#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
EMERGENCY FACT GENERATOR
========================
Generator der direkt mit der Datenbank arbeitet, falls das Backend nicht läuft
"""

import os
import time
import random
import sqlite3
import hashlib
from typing import List, Set, Tuple, Dict

# Database path
DB_PATH = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"

class EmergencyFactGenerator:
    """Emergency Fact Generator - works directly with database"""
    
    def __init__(self):
        # Balanced predicate weights
        self.predicates = {
            'IsA': 0.10,
            'HasProperty': 0.20,
            'HasPart': 0.08,
            'IsTypeOf': 0.08,
            'Causes': 0.08,
            'Requires': 0.07,
            'Uses': 0.07,
            'HasPurpose': 0.06,
            'ConsistsOf': 0.05,
            'DependsOn': 0.05,
            'IsSimilarTo': 0.04,
            'IsDefinedAs': 0.04,
            'HasLocation': 0.04,
            'WasDevelopedBy': 0.02,
            'StudiedBy': 0.02
        }
        
        # Entity pools
        self.entities = {
            'physics': ['photon', 'electron', 'neutron', 'proton', 'quark', 'boson', 
                       'velocity', 'mass', 'momentum', 'Einstein', 'Newton', 'energy',
                       'force', 'gravity', 'quantum', 'wave', 'particle', 'field'],
            'chemistry': ['H2O', 'CO2', 'O2', 'NH3', 'NaCl', 'CH4', 'hydrogen', 
                         'oxygen', 'carbon', 'nitrogen', 'sodium', 'chlorine',
                         'molecule', 'atom', 'bond', 'reaction', 'catalyst'],
            'biology': ['DNA', 'RNA', 'protein', 'cell', 'gene', 'enzyme', 'mitochondria',
                       'nucleus', 'chromosome', 'evolution', 'species', 'ecosystem'],
            'technology': ['computer', 'algorithm', 'data', 'network', 'software', 'hardware',
                          'AI', 'machine_learning', 'neural_network', 'blockchain', 'quantum_computing'],
            'geography': ['mountain', 'ocean', 'river', 'desert', 'forest', 'city', 'country',
                         'continent', 'climate', 'weather', 'ecosystem', 'biodiversity']
        }
        
        self.facts_generated = 0
        self.duplicates_prevented = 0
        
    def get_existing_facts(self) -> Set[str]:
        """Get all existing facts from database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT statement FROM facts")
            facts = {row[0] for row in cursor.fetchall()}
            conn.close()
            return facts
        except Exception as e:
            print(f"Error reading facts: {e}")
            return set()
    
    def add_fact_to_db(self, fact: str) -> bool:
        """Add fact directly to database"""
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            
            # Check if fact already exists
            cursor.execute("SELECT COUNT(*) FROM facts WHERE statement = ?", (fact,))
            if cursor.fetchone()[0] > 0:
                self.duplicates_prevented += 1
                conn.close()
                return False
            
            # Add new fact
            cursor.execute("INSERT INTO facts (statement, created_at) VALUES (?, datetime('now'))", (fact,))
            conn.commit()
            conn.close()
            self.facts_generated += 1
            return True
            
        except Exception as e:
            print(f"Error adding fact: {e}")
            return False
    
    def generate_fact(self) -> str:
        """Generate a single fact"""
        predicate = random.choices(
            list(self.predicates.keys()),
            weights=list(self.predicates.values())
        )[0]
        
        # Select random domain and entities
        domain = random.choice(list(self.entities.keys()))
        entities = self.entities[domain]
        
        if predicate in ['IsA', 'HasProperty', 'IsTypeOf']:
            subject = random.choice(entities)
            object_entity = random.choice(entities)
            return f"{predicate}({subject}, {object_entity})"
        elif predicate in ['HasPart', 'ConsistsOf', 'DependsOn']:
            whole = random.choice(entities)
            part = random.choice(entities)
            return f"{predicate}({whole}, {part})"
        elif predicate in ['Causes', 'Requires', 'Uses']:
            cause = random.choice(entities)
            effect = random.choice(entities)
            return f"{predicate}({cause}, {effect})"
        else:
            subject = random.choice(entities)
            object_entity = random.choice(entities)
            return f"{predicate}({subject}, {object_entity})"
    
    def run(self, duration_minutes: float = 10):
        """Run the emergency generator"""
        print("=" * 60)
        print("🚨 EMERGENCY FACT GENERATOR")
        print("=" * 60)
        print(f"Duration: {duration_minutes} minutes")
        print(f"Database: {DB_PATH}")
        print("=" * 60)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        # Get existing facts for duplicate prevention
        existing_facts = self.get_existing_facts()
        print(f"📊 Existing facts: {len(existing_facts)}")
        
        batch_size = 10
        batch_count = 0
        
        while time.time() < end_time:
            batch_count += 1
            batch_facts = []
            
            # Generate batch of facts
            for _ in range(batch_size):
                fact = self.generate_fact()
                if fact not in existing_facts:
                    batch_facts.append(fact)
                    existing_facts.add(fact)
            
            # Add facts to database
            for fact in batch_facts:
                self.add_fact_to_db(fact)
            
            # Progress report
            elapsed = (time.time() - start_time) / 60
            rate = self.facts_generated / elapsed if elapsed > 0 else 0
            
            print(f"📊 Batch {batch_count}: +{len(batch_facts)} facts | "
                  f"Total: {self.facts_generated} | Rate: {rate:.1f} facts/min")
            
            time.sleep(2)  # 2 second pause between batches
        
        # Final statistics
        elapsed = (time.time() - start_time) / 60
        rate = self.facts_generated / elapsed if elapsed > 0 else 0
        
        print("\n" + "=" * 60)
        print("🎯 EMERGENCY GENERATION COMPLETE")
        print("=" * 60)
        print(f"✅ Facts added: {self.facts_generated}")
        print(f"⚠️  Duplicates prevented: {self.duplicates_prevented}")
        print(f"⏱️  Total time: {elapsed:.1f} minutes")
        print(f"📊 Effective rate: {rate:.1f} facts/minute")
        print("=" * 60)

if __name__ == "__main__":
    generator = EmergencyFactGenerator()
    generator.run(duration_minutes=5)  # Run for 5 minutes






