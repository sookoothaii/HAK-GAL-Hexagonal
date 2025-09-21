#!/usr/bin/env python3
"""
HAK-GAL Predicate Seeder & Normalizer
======================================
Seeds the database with essential predicates to improve HRM confidence
Normalizes queries to use known predicates

Nach HAK/GAL Verfassung Artikel 7: Konjugierte Zustände
"""

import requests
import json
import sqlite3
from typing import Dict, List, Tuple

BACKEND_URL = 'http://localhost:5002'
DATABASE_PATH = r'D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db'

class PredicateManager:
    """Manages predicate normalization and seeding"""
    
    def __init__(self):
        # Mapping of new predicates to known ones
        self.predicate_mappings = {
            # Philosophy/History
            'Influenced': 'Causes',  # A influenced B → A causes changes in B
            'TeacherOf': 'Teaches',
            'StudentOf': 'LearnsFrom',
            
            # Geography
            'BornIn': 'LocatedIn',  # Person born in place
            'CapitalOf': 'IsA',  # Tokyo is a capital
            'Borders': 'AdjacentTo',
            
            # History/Military  
            'Conquered': 'Controls',  # Rome conquered Gaul → Rome controls Gaul
            'Ruled': 'Controls',
            'Defeated': 'Overcame',
            
            # Technology
            'RunsOn': 'Requires',  # Software runs on hardware
            'Uses': 'Requires',
            'DependsOn': 'Requires',
            
            # General relationships
            'MemberOf': 'PartOf',
            'BelongsTo': 'PartOf',
            'Contains': 'HasPart'
        }
        
        # Essential seed facts for common predicates
        self.seed_facts = [
            # Core philosophical facts
            ("IsA(Socrates, Philosopher).", "seed", 1.0),
            ("IsA(Plato, Philosopher).", "seed", 1.0),
            ("IsA(Aristotle, Philosopher).", "seed", 1.0),
            ("Teaches(Socrates, Plato).", "seed", 1.0),
            ("Teaches(Plato, Aristotle).", "seed", 1.0),
            
            # Influenced relationships (using Causes)
            ("Causes(Socrates, PlatonicPhilosophy).", "seed", 0.9),
            ("Causes(Plato, AristotelianThought).", "seed", 0.9),
            
            # Geographic facts
            ("LocatedIn(Berlin, Germany).", "seed", 1.0),
            ("LocatedIn(Paris, France).", "seed", 1.0),
            ("LocatedIn(Rome, Italy).", "seed", 1.0),
            ("LocatedIn(Tokyo, Japan).", "seed", 1.0),
            
            # Birth locations (using LocatedIn)
            ("LocatedIn(Napoleon, Corsica).", "seed", 0.9),
            ("LocatedIn(Socrates, Athens).", "seed", 0.9),
            
            # Historical conquests (using Controls)
            ("Controls(Rome, Gaul).", "seed", 0.8),
            ("Controls(Rome, Britain).", "seed", 0.8),
            ("Controls(Alexander, Persia).", "seed", 0.8),
            
            # Technology facts
            ("HasPart(Computer, CPU).", "seed", 1.0),
            ("HasPart(Computer, Memory).", "seed", 1.0),
            ("HasPart(Computer, Storage).", "seed", 1.0),
            ("Requires(Software, Hardware).", "seed", 1.0),
            ("IsA(Python, ProgrammingLanguage).", "seed", 1.0),
            
            # Science facts
            ("IsA(Water, Liquid).", "seed", 0.9),
            ("IsA(Birds, Animals).", "seed", 1.0),
            ("Causes(Gravity, Falling).", "seed", 1.0),
            ("HasProperty(Hydrogen, OneProton).", "seed", 1.0),
            
            # Additional relationship examples
            ("PartOf(CPU, Computer).", "seed", 1.0),
            ("AdjacentTo(France, Spain).", "seed", 1.0),
            ("AdjacentTo(Germany, France).", "seed", 1.0),
        ]
    
    def normalize_predicate(self, query: str) -> str:
        """
        Normalize unknown predicates to known ones
        Example: Influenced(A, B) → Causes(A, B)
        """
        # Extract predicate from query
        if '(' not in query:
            return query
        
        predicate = query.split('(')[0]
        args_part = query[query.index('('):]
        
        # Check if predicate needs normalization
        if predicate in self.predicate_mappings:
            normalized = self.predicate_mappings[predicate]
            normalized_query = normalized + args_part
            print(f"  📝 Normalized: {query} → {normalized_query}")
            return normalized_query
        
        return query
    
    def seed_database(self):
        """Seed database with essential facts"""
        print("🌱 SEEDING DATABASE WITH ESSENTIAL FACTS...")
        print("="*60)
        
        added = 0
        duplicates = 0
        errors = 0
        
        for fact, source, confidence in self.seed_facts:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/facts",
                    json={
                        'statement': fact,
                        'source': source,
                        'confidence': confidence
                    },
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    data = response.json()
                    if data.get('success'):
                        added += 1
                        print(f"  ✅ Added: {fact}")
                    else:
                        message = data.get('message', '')
                        if 'exists' in message.lower():
                            duplicates += 1
                            print(f"  🔄 Already exists: {fact}")
                        else:
                            errors += 1
                            print(f"  ❌ Error: {fact}")
                elif response.status_code == 409:
                    duplicates += 1
                    print(f"  🔄 Duplicate: {fact}")
                else:
                    errors += 1
                    print(f"  ❌ Failed ({response.status_code}): {fact}")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Exception: {fact} - {e}")
        
        print("\n" + "="*60)
        print(f"📊 SEEDING RESULTS:")
        print(f"  ✅ Added: {added}")
        print(f"  🔄 Duplicates: {duplicates}")
        print(f"  ❌ Errors: {errors}")
        print("="*60)
        
        return added, duplicates, errors
    
    def test_normalized_queries(self):
        """Test queries with normalization"""
        print("\n🧪 TESTING QUERIES WITH NORMALIZATION...")
        print("="*60)
        
        test_queries = [
            # Original problematic queries
            ("Influenced(Socrates, Plato).", "Causes(Socrates, PlatonicThought)."),
            ("BornIn(Napoleon, France).", "LocatedIn(Napoleon, France)."),
            ("Conquered(Rome, Gaul).", "Controls(Rome, Gaul)."),
            
            # Additional test cases
            ("TeacherOf(Socrates, Plato).", "Teaches(Socrates, Plato)."),
            ("Borders(France, Spain).", "AdjacentTo(France, Spain)."),
            ("RunsOn(Software, Hardware).", "Requires(Software, Hardware)."),
        ]
        
        for original, normalized in test_queries:
            print(f"\n📝 Testing: {original}")
            print(f"   Normalized: {normalized}")
            
            # Test original
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/reason",
                    json={'query': original},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    orig_conf = response.json().get('confidence', 0.0)
                    print(f"   Original confidence: {orig_conf:.1%}")
                else:
                    print(f"   Original failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   Original error: {e}")
            
            # Test normalized
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/reason",
                    json={'query': normalized},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    norm_conf = response.json().get('confidence', 0.0)
                    print(f"   Normalized confidence: {norm_conf:.1%}")
                    
                    if norm_conf > orig_conf:
                        improvement = (norm_conf - orig_conf) * 100
                        print(f"   ✅ Improvement: +{improvement:.1f}%")
                else:
                    print(f"   Normalized failed: HTTP {response.status_code}")
            except Exception as e:
                print(f"   Normalized error: {e}")
        
        print("\n" + "="*60)
    
    def analyze_current_predicates(self):
        """Analyze predicates currently in the database"""
        print("\n📊 ANALYZING CURRENT PREDICATES...")
        print("="*60)
        
        try:
            conn = sqlite3.connect(DATABASE_PATH)
            cursor = conn.cursor()
            
            # Get predicate distribution
            cursor.execute("""
                SELECT 
                    SUBSTR(statement, 1, INSTR(statement, '(') - 1) as predicate,
                    COUNT(*) as count
                FROM facts
                WHERE statement LIKE '%(%'
                GROUP BY predicate
                ORDER BY count DESC
                LIMIT 20
            """)
            
            predicates = cursor.fetchall()
            
            print("Top predicates in database:")
            known_predicates = set()
            for pred, count in predicates:
                if pred:
                    known_predicates.add(pred)
                    status = "✅" if count > 10 else "⚠️"
                    print(f"  {status} {pred}: {count:,} facts")
            
            # Check which problematic predicates are missing
            problematic = ['Influenced', 'BornIn', 'Conquered', 'TeacherOf', 'Borders', 'RunsOn']
            print(f"\nProblematic predicates status:")
            for pred in problematic:
                if pred in known_predicates:
                    print(f"  ✅ {pred} - EXISTS")
                else:
                    print(f"  ❌ {pred} - MISSING (causes 0% confidence)")
                    if pred in self.predicate_mappings:
                        print(f"     → Can normalize to: {self.predicate_mappings[pred]}")
            
            conn.close()
            
        except Exception as e:
            print(f"Error analyzing database: {e}")
        
        print("="*60)

def main():
    """Main execution"""
    print("\n🔧 HAK-GAL PREDICATE MANAGEMENT SYSTEM")
    print("="*60)
    
    manager = PredicateManager()
    
    # 1. Analyze current state
    manager.analyze_current_predicates()
    
    # 2. Seed essential facts
    print("\n💡 Seeding will add facts with KNOWN predicates")
    print("   This improves HRM confidence for future queries")
    
    response = input("\n🔧 Seed database with essential facts? (y/n): ")
    if response.lower() == 'y':
        manager.seed_database()
    
    # 3. Test normalization
    print("\n📝 Normalization maps unknown predicates to known ones")
    response = input("Test query normalization? (y/n): ")
    if response.lower() == 'y':
        manager.test_normalized_queries()
    
    print("\n✅ COMPLETE!")
    print("\n💡 RECOMMENDATIONS:")
    print("1. Use normalized predicates in queries for better confidence")
    print("2. Seed database regularly with common facts")
    print("3. Train HRM with diverse predicates for better recognition")
    print("="*60)

if __name__ == "__main__":
    main()
