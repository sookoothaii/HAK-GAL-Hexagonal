"""
Optimized Knowledge Generator with duplicate prevention and predicate balancing
"""
import random
import hashlib
from typing import List, Set, Tuple
import json

class OptimizedKnowledgeGenerator:
    def __init__(self):
        # Balanced predicate weights (HasProperty reduced from 80% to 20%)
        self.predicates = {
            'IsA': 0.10,
            'HasProperty': 0.20,  # Reduced from 80%!
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
        
        # Domain-specific entity pools
        self.entities = {
            'physics': ['photon', 'electron', 'neutron', 'proton', 'quark', 'boson', 
                       'velocity', 'mass', 'momentum', 'Einstein', 'Newton'],
            'chemistry': ['H2O', 'CO2', 'O2', 'NH3', 'NaCl', 'CH4', 'hydrogen', 
                         'oxygen', 'carbon', 'nitrogen', 'sodium', 'chlorine'],
            'biology': ['DNA', 'RNA', 'protein', 'cell', 'enzyme', 'virus', 'bacteria',
                       'mitochondria', 'nucleus', 'ribosome', 'chromosome', 'fungi'],
            'technology': ['AI', 'blockchain', 'HTTP', 'SQL', 'NoSQL', 'TCP/IP', 
                          'GraphQL', 'encryption', 'API', 'server', 'client', 'cloud'],
            'mathematics': ['integral', 'derivative', 'limit', 'matrix', 'vector', 
                           'prime', 'integer', 'graph', 'topology', 'algebra', 
                           'calculus', 'Euler', 'Gauss']
        }
        
        # Track generated normalized facts to prevent duplicates
        self.generated_normalized = set()
    
    def normalize_arguments(self, args: List[str]) -> str:
        """Normalize by sorting arguments"""
        return ','.join(sorted(args))
    
    def generate_fact(self) -> Tuple[str, dict]:
        """Generate a unique, balanced fact"""
        max_attempts = 10
        
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
                category = random.choice(['concept', 'element', 'system', 'method', 'structure'])
                fact = f"{entity} IsA {category}"
                
            elif predicate == 'HasProperty':
                entity = random.choice(self.entities[domain])
                properties = ['stable', 'reactive', 'complex', 'fundamental', 'essential', 'variable']
                prop = random.choice(properties)
                fact = f"{entity} HasProperty {prop}"
                
            elif predicate == 'HasPart':
                whole = random.choice(self.entities[domain])
                part = random.choice(self.entities[domain])
                if whole != part:
                    fact = f"{whole} HasPart {part}"
                else:
                    continue
                    
            elif predicate == 'Causes':
                cause = random.choice(self.entities[domain])
                effect = random.choice(self.entities[domain])
                if cause != effect:
                    fact = f"{cause} Causes {effect}"
                else:
                    continue
                    
            elif predicate == 'Requires':
                process = random.choice(self.entities[domain])
                requirement = random.choice(self.entities[domain])
                if process != requirement:
                    fact = f"{process} Requires {requirement}"
                else:
                    continue
                    
            elif predicate == 'Uses':
                system = random.choice(self.entities[domain])
                resource = random.choice(self.entities[domain])
                if system != resource:
                    fact = f"{system} Uses {resource}"
                else:
                    continue
                    
            elif predicate == 'DependsOn':
                dependent = random.choice(self.entities[domain])
                dependency = random.choice(self.entities[domain])
                if dependent != dependency:
                    fact = f"{dependent} DependsOn {dependency}"
                else:
                    continue
                    
            else:
                # Generic pattern for other predicates
                subj = random.choice(self.entities[domain])
                obj = random.choice(self.entities[domain])
                if subj != obj:
                    fact = f"{subj} {predicate} {obj}"
                else:
                    continue
            
            # Check for duplicate (normalized)
            normalized = self.normalize_fact(fact)
            if normalized not in self.generated_normalized:
                self.generated_normalized.add(normalized)
                
                metadata = {
                    'domain': domain,
                    'predicate': predicate,
                    'confidence': random.uniform(0.85, 0.99)
                }
                
                return fact, metadata
        
        return None, None
    
    def normalize_fact(self, fact: str) -> str:
        """Normalize fact for duplicate detection"""
        if '(' in fact and ')' in fact:
            # Handle functional form
            prefix = fact[:fact.index('(')]
            args_str = fact[fact.index('(')+1:fact.rindex(')')]
            args = [arg.strip() for arg in args_str.split(',')]
            return f"{prefix}({self.normalize_arguments(args)})"
        else:
            # Handle predicate form
            parts = fact.split()
            if len(parts) >= 3:
                # Sort object arguments if multiple
                return ' '.join(parts)
            return fact
    
    def generate_batch(self, count: int) -> List[Tuple[str, dict]]:
        """Generate batch of unique facts"""
        facts = []
        for _ in range(count):
            fact, meta = self.generate_fact()
            if fact:
                facts.append((fact, meta))
        return facts

# Test the generator
if __name__ == "__main__":
    generator = OptimizedKnowledgeGenerator()
    
    print("="*60)
    print("OPTIMIZED GENERATOR TEST")
    print("="*60)
    
    # Generate test batch
    batch = generator.generate_batch(100)
    
    # Analyze predicate distribution
    predicate_counts = {}
    for fact, meta in batch:
        pred = meta['predicate']
        predicate_counts[pred] = predicate_counts.get(pred, 0) + 1
    
    print(f"Generated: {len(batch)} unique facts")
    print(f"\nPredicate distribution:")
    for pred, count in sorted(predicate_counts.items(), key=lambda x: -x[1]):
        expected_pct = generator.predicates[pred] * 100
        actual_pct = (count / len(batch)) * 100
        print(f"  {pred:20s}: {count:3d} ({actual_pct:5.1f}% actual vs {expected_pct:5.1f}% expected)")
    
    print(f"\nNo duplicates: {len(generator.generated_normalized)} unique normalized facts")
    
    # Show sample facts
    print(f"\nSample facts:")
    for fact, meta in batch[:10]:
        print(f"  {fact} [domain: {meta['domain']}, confidence: {meta['confidence']:.2f}]")
    
    print("="*60)
