#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OPTIMIZED FACT GENERATOR - Intelligent fact generation with duplicate prevention
=============================================================================
Generates balanced, unique facts with proper predicate distribution
"""

import os
import time
import random
import requests
import json
import hashlib
from typing import List, Set, Tuple, Dict

# Auth Token aus Environment
AUTH_TOKEN = os.environ.get('HAKGAL_AUTH_TOKEN', '515f57956e7bd15ddc3817573598f190')
API_BASE = 'http://127.0.0.1:5002'

class SimpleFactGenerator:
    """Optimized Fact Generator with duplicate prevention and balanced predicates"""
    
    def __init__(self):
        # Balanced predicate weights (reduced HasProperty dominance)
        self.predicates = {
            'IsA': 0.10,
            'HasProperty': 0.20,  # Reduced from 80% to 20%
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
        
        # Domain-specific entity pools (expanded)
        self.entities = {
            'physics': ['photon', 'electron', 'neutron', 'proton', 'quark', 'boson', 
                       'velocity', 'mass', 'momentum', 'Einstein', 'Newton', 'energy',
                       'force', 'gravity', 'quantum', 'wave', 'particle', 'field'],
            'chemistry': ['H2O', 'CO2', 'O2', 'NH3', 'NaCl', 'CH4', 'hydrogen', 
                         'oxygen', 'carbon', 'nitrogen', 'sodium', 'chlorine',
                         'molecule', 'atom', 'ion', 'bond', 'reaction', 'catalyst'],
            'biology': ['DNA', 'RNA', 'protein', 'cell', 'enzyme', 'virus', 'bacteria',
                       'mitochondria', 'nucleus', 'ribosome', 'chromosome', 'fungi',
                       'organism', 'tissue', 'organ', 'species', 'ecosystem', 'gene'],
            'technology': ['AI', 'blockchain', 'HTTP', 'SQL', 'NoSQL', 'TCP/IP', 
                          'GraphQL', 'encryption', 'API', 'server', 'client', 'cloud',
                          'algorithm', 'database', 'network', 'protocol', 'security', 'framework'],
            'mathematics': ['integral', 'derivative', 'limit', 'matrix', 'vector', 
                           'prime', 'integer', 'graph', 'topology', 'algebra', 
                           'calculus', 'Euler', 'Gauss', 'theorem', 'equation',
                           'function', 'set', 'proof', 'axiom']
        }
        
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': AUTH_TOKEN
        }
        
        # Track normalized facts to prevent duplicates
        self.generated_normalized = set()
        
        # Statistics
        self.stats = {
            'facts_added': 0,
            'duplicates_prevented': 0,
            'api_errors': 0,
            'predicate_counts': {}
        }
    
    def normalize_fact(self, fact: str) -> str:
        """Normalize fact by sorting arguments to detect duplicates"""
        if '(' in fact and ')' in fact:
            prefix = fact[:fact.index('(')]
            args_str = fact[fact.index('(')+1:fact.rindex(')')]
            suffix = fact[fact.rindex(')'):]
            
            # Split arguments and sort
            args = [arg.strip() for arg in args_str.split(',')]
            args_sorted = sorted(args)
            
            # Reconstruct normalized
            return f"{prefix}({','.join(args_sorted)}){suffix}"
        else:
            # Predicate form
            parts = fact.split()
            if len(parts) >= 3:
                return ' '.join([parts[0], parts[1]] + sorted(parts[2:]))
            return fact
    
    def generate_fact(self) -> Tuple[str, Dict]:
        """Generate a unique, balanced fact"""
        max_attempts = 20
        
        for _ in range(max_attempts):
            # Select predicate based on weights
            predicate = random.choices(
                list(self.predicates.keys()),
                weights=list(self.predicates.values())
            )[0]
            
            # Select domain
            domain = random.choice(list(self.entities.keys()))
            
            # Generate fact based on predicate type
            if predicate == 'IsA':
                entity = random.choice(self.entities[domain])
                categories = ['concept', 'element', 'system', 'method', 'structure', 'principle']
                category = random.choice(categories)
                fact = f"IsA({entity}, {category})."
                
            elif predicate == 'HasProperty':
                entity = random.choice(self.entities[domain])
                properties = ['stable', 'reactive', 'complex', 'fundamental', 'essential', 
                             'variable', 'dynamic', 'static', 'critical', 'optimal']
                prop = random.choice(properties)
                fact = f"HasProperty({entity}, {prop})."
                
            elif predicate in ['HasPart', 'Causes', 'Requires', 'Uses', 'DependsOn']:
                subj = random.choice(self.entities[domain])
                obj = random.choice(self.entities[domain])
                if subj != obj:
                    fact = f"{predicate}({subj}, {obj})."
                else:
                    continue
                    
            elif predicate in ['IsTypeOf', 'IsSimilarTo', 'IsDefinedAs']:
                entities = random.sample(self.entities[domain], min(2, len(self.entities[domain])))
                if len(entities) == 2:
                    fact = f"{predicate}({entities[0]}, {entities[1]})."
                else:
                    continue
                    
            elif predicate == 'HasPurpose':
                entity = random.choice(self.entities[domain])
                purposes = ['computation', 'storage', 'transmission', 'analysis', 
                           'synthesis', 'regulation', 'protection', 'conversion']
                purpose = random.choice(purposes)
                fact = f"HasPurpose({entity}, {purpose})."
                
            elif predicate == 'ConsistsOf':
                whole = random.choice(self.entities[domain])
                parts = random.sample(self.entities[domain], min(2, len(self.entities[domain])))
                if whole not in parts:
                    fact = f"ConsistsOf({whole}, {', '.join(parts)})."
                else:
                    continue
                    
            elif predicate == 'HasLocation':
                entity = random.choice(self.entities[domain])
                locations = ['system', 'network', 'cell', 'space', 'layer', 'region']
                location = random.choice(locations)
                fact = f"HasLocation({entity}, {location})."
                
            elif predicate in ['WasDevelopedBy', 'StudiedBy']:
                entity = random.choice(self.entities[domain])
                developers = ['Einstein', 'Newton', 'Turing', 'Darwin', 'Curie', 'Bohr']
                developer = random.choice(developers)
                fact = f"{predicate}({entity}, {developer})."
                
            else:
                # Fallback pattern
                entities = random.sample(self.entities[domain], min(2, len(self.entities[domain])))
                if len(entities) >= 2:
                    fact = f"{predicate}({entities[0]}, {entities[1]})."
                else:
                    continue
            
            # Check for duplicate
            normalized = self.normalize_fact(fact)
            if normalized not in self.generated_normalized:
                self.generated_normalized.add(normalized)
                
                # Track predicate usage
                if predicate not in self.stats['predicate_counts']:
                    self.stats['predicate_counts'][predicate] = 0
                self.stats['predicate_counts'][predicate] += 1
                
                metadata = {
                    'domain': domain,
                    'predicate': predicate,
                    'confidence': random.uniform(0.85, 0.99),
                    'normalized': normalized
                }
                
                return fact, metadata
        
        # Failed to generate unique fact
        self.stats['duplicates_prevented'] += 1
        return None, None
    
    def add_fact(self, fact: str) -> bool:
        """Add fact via API"""
        try:
            response = requests.post(
                f"{API_BASE}/api/facts",
                json={'statement': fact},
                headers=self.headers,
                timeout=5
            )
            
            if response.status_code in [200, 201]:
                self.stats['facts_added'] += 1
                return True
            elif response.status_code == 409:
                self.stats['duplicates_prevented'] += 1
                return False
            else:
                self.stats['api_errors'] += 1
                return False
                
        except Exception as e:
            self.stats['api_errors'] += 1
            return False
    
    def print_stats(self):
        """Print current statistics"""
        print("\n📊 Generator Statistics:")
        print(f"  ✅ Facts added: {self.stats['facts_added']}")
        print(f"  ⚠️  Duplicates prevented: {self.stats['duplicates_prevented']}")
        print(f"  ❌ API errors: {self.stats['api_errors']}")
        
        if self.stats['predicate_counts']:
            print("\n📈 Predicate Distribution:")
            total = sum(self.stats['predicate_counts'].values())
            for pred, count in sorted(self.stats['predicate_counts'].items(), 
                                     key=lambda x: -x[1])[:10]:
                pct = (count / total) * 100 if total > 0 else 0
                expected = self.predicates.get(pred, 0) * 100
                print(f"    {pred:20s}: {count:4d} ({pct:5.1f}% actual, {expected:5.1f}% target)")
    
    def run(self, duration_minutes=1):
        """Main generation loop"""
        print("="*60)
        print("OPTIMIZED FACT GENERATOR")
        print("="*60)
        print(f"Duration: {duration_minutes} minutes")
        print(f"API: {API_BASE}")
        print("Features: Duplicate prevention, Balanced predicates")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        batch_count = 0
        
        while time.time() < end_time:
            # Generate batch
            batch_size = 10
            batch_added = 0
            
            for _ in range(batch_size):
                fact, metadata = self.generate_fact()
                if fact:
                    if self.add_fact(fact):
                        batch_added += 1
                    
                    # Small delay between facts
                    time.sleep(0.05)
            
            batch_count += 1
            
            # Progress update every 5 batches
            if batch_count % 5 == 0:
                elapsed = (time.time() - start_time) / 60
                rate = self.stats['facts_added'] / elapsed if elapsed > 0 else 0
                print(f"\n⏱️  Progress: {self.stats['facts_added']} facts in {elapsed:.1f} min ({rate:.1f} facts/min)")
            
            # Pause between batches
            if time.time() < end_time:
                time.sleep(1)
        
        # Final report
        total_time = (time.time() - start_time) / 60
        print("\n" + "="*60)
        print("GENERATION COMPLETE")
        self.print_stats()
        print(f"\n⏱️  Total time: {total_time:.1f} minutes")
        print(f"📊 Effective rate: {self.stats['facts_added']/total_time:.1f} facts/minute")
        print("="*60)


if __name__ == "__main__":
    # Set environment
    os.environ['HAKGAL_AUTH_TOKEN'] = '515f57956e7bd15ddc3817573598f190'
    
    # Start generator
    generator = SimpleFactGenerator()
    generator.run(duration_minutes=0.5)  # 30 second test
