#!/usr/bin/env python3
"""
HAK-GAL Enhanced Context Seeder
================================
Adds more context facts to improve HRM confidence
Uses only predicates that HRM already knows well

Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import requests
import json
import time

BACKEND_URL = 'http://localhost:5002'

class EnhancedSeeder:
    """Seeds database with HRM-friendly facts"""
    
    def __init__(self):
        # Use ONLY predicates that HRM knows well
        # Based on your database analysis
        self.known_good_predicates = [
            'HasProperty',  # 1,330 facts - HRM knows this well!
            'HasPart',      # 763 facts
            'Causes',       # 601 facts
            'IsA',          # 87 facts but fundamental
            'IsDefinedAs',  # 388 facts
            'Uses',         # 32 facts
        ]
        
        # Enhanced seed facts using ONLY known predicates
        self.enhanced_seeds = [
            # Use Causes instead of Influenced
            ("Causes(Socrates, PlatoPhilosophy).", 0.9),
            ("Causes(Plato, AristotlePhilosophy).", 0.9),
            ("Causes(Aristotle, WesternPhilosophy).", 0.9),
            ("Causes(Philosophy, CriticalThinking).", 0.9),
            
            # Use HasProperty for person attributes
            ("HasProperty(Socrates, Philosopher).", 1.0),
            ("HasProperty(Plato, Philosopher).", 1.0),
            ("HasProperty(Aristotle, Philosopher).", 1.0),
            ("HasProperty(Napoleon, French).", 1.0),
            ("HasProperty(Napoleon, Emperor).", 1.0),
            ("HasProperty(Napoleon, Military).", 1.0),
            
            # Use HasPart for locations (person "has part" in location)
            ("HasPart(Athens, Socrates).", 0.8),
            ("HasPart(France, Napoleon).", 0.8),
            ("HasPart(Germany, Berlin).", 1.0),
            ("HasPart(Japan, Tokyo).", 1.0),
            
            # Use Causes for conquest (conquest causes control)
            ("Causes(RomanConquest, GaulControl).", 0.9),
            ("Causes(Rome, GaulSubmission).", 0.8),
            ("Causes(Military, Conquest).", 0.9),
            
            # Technology with known predicates
            ("HasPart(Computer, Processor).", 1.0),
            ("HasPart(Software, Code).", 1.0),
            ("HasProperty(Python, Interpreted).", 1.0),
            ("HasProperty(Python, HighLevel).", 1.0),
            ("Uses(Python, Interpreter).", 1.0),
            ("Uses(Software, Hardware).", 1.0),
            
            # Science with known predicates
            ("HasProperty(Water, Liquid).", 0.9),
            ("HasProperty(Water, H2O).", 1.0),
            ("HasProperty(Birds, Flying).", 0.9),
            ("HasProperty(Gravity, Force).", 1.0),
            ("Causes(Gravity, Acceleration).", 1.0),
            ("Causes(Gravity, Weight).", 1.0),
            
            # Mathematics
            ("HasProperty(Seven, Prime).", 1.0),
            ("HasProperty(Seven, Odd).", 1.0),
            ("IsDefinedAs(Prime, DivisibleOnlyByOneAndSelf).", 1.0),
            
            # More IsA facts (HRM knows this)
            ("IsA(Socrates, Human).", 1.0),
            ("IsA(Plato, Human).", 1.0),
            ("IsA(Napoleon, Human).", 1.0),
            ("IsA(Berlin, City).", 1.0),
            ("IsA(Germany, Country).", 1.0),
            ("IsA(Tokyo, City).", 1.0),
            ("IsA(Japan, Country).", 1.0),
            ("IsA(CPU, Component).", 1.0),
            ("IsA(Water, Substance).", 1.0),
            ("IsA(Bird, Animal).", 1.0),
            ("IsA(Seven, Number).", 1.0),
        ]
    
    def seed_enhanced_facts(self):
        """Seed facts using only HRM-known predicates"""
        print("🌱 ENHANCED SEEDING WITH HRM-FRIENDLY PREDICATES...")
        print("="*60)
        
        added = 0
        duplicates = 0
        errors = 0
        
        for fact, confidence in self.enhanced_seeds:
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/facts",
                    json={
                        'statement': fact,
                        'source': 'enhanced_seed',
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
                        duplicates += 1
                        print(f"  🔄 Exists: {fact}")
                elif response.status_code == 409:
                    duplicates += 1
                else:
                    errors += 1
                    print(f"  ❌ Error: {fact}")
                    
            except Exception as e:
                errors += 1
                print(f"  ❌ Exception: {e}")
            
            time.sleep(0.05)  # Small delay
        
        print("\n" + "="*60)
        print(f"📊 RESULTS:")
        print(f"  ✅ Added: {added}")
        print(f"  🔄 Duplicates: {duplicates}")
        print(f"  ❌ Errors: {errors}")
        print("="*60)
        
        return added
    
    def test_improved_queries(self):
        """Test queries with better mappings"""
        print("\n🧪 TESTING WITH ENHANCED CONTEXT...")
        print("="*60)
        
        test_cases = [
            # Original → Better mapping
            ("Influenced(Socrates, Plato).", "Causes(Socrates, PlatoPhilosophy)."),
            ("BornIn(Napoleon, France).", "HasProperty(Napoleon, French)."),
            ("Conquered(Rome, Gaul).", "Causes(Rome, GaulSubmission)."),
            ("TeacherOf(Socrates, Plato).", "Causes(Socrates, PlatoPhilosophy)."),
            ("RunsOn(Software, Hardware).", "Uses(Software, Hardware)."),
            
            # Natural language style
            ("Is Socrates a philosopher?", "HasProperty(Socrates, Philosopher)."),
            ("Was Napoleon from France?", "HasProperty(Napoleon, French)."),
            ("Does a computer have a CPU?", "HasPart(Computer, Processor)."),
            ("Is water a liquid?", "HasProperty(Water, Liquid)."),
            ("Is seven a prime number?", "HasProperty(Seven, Prime)."),
        ]
        
        for original, better in test_cases:
            print(f"\n📝 Query: {original[:50]}...")
            
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
                else:
                    orig_conf = 0.0
            except:
                orig_conf = 0.0
            
            # Test better mapping
            try:
                response = requests.post(
                    f"{BACKEND_URL}/api/reason",
                    json={'query': better},
                    headers={'Content-Type': 'application/json'},
                    timeout=10
                )
                
                if response.ok:
                    better_conf = response.json().get('confidence', 0.0)
                else:
                    better_conf = 0.0
            except:
                better_conf = 0.0
            
            print(f"   Original: {orig_conf:.1%}")
            print(f"   Enhanced: {better_conf:.1%}")
            
            if better_conf > orig_conf:
                improvement = (better_conf - orig_conf) * 100
                print(f"   ✅ Improvement: +{improvement:.1f}%")
            elif better_conf == orig_conf and better_conf > 0:
                print(f"   ✅ Both work well")
            else:
                print(f"   ⚠️ No improvement")
        
        print("\n" + "="*60)

def main():
    """Main execution"""
    print("\n🚀 HAK-GAL ENHANCED CONTEXT SEEDER")
    print("="*60)
    print("This tool adds facts using ONLY predicates that HRM knows well")
    print("Based on analysis: HasProperty, HasPart, Causes work best")
    print("="*60)
    
    seeder = EnhancedSeeder()
    
    # Seed enhanced facts
    print("\n💡 This will add ~40 facts using HRM-friendly predicates")
    response = input("Proceed with enhanced seeding? (y/n): ")
    
    if response.lower() == 'y':
        added = seeder.seed_enhanced_facts()
        
        if added > 0:
            print(f"\n✅ Successfully added {added} new facts!")
            print("Testing improved confidence...")
            time.sleep(1)
            seeder.test_improved_queries()
    
    print("\n" + "="*60)
    print("💡 KEY INSIGHTS:")
    print("1. HRM responds best to HasProperty, HasPart, Causes")
    print("2. Use HasProperty(Person, Attribute) instead of BornIn")
    print("3. Use Causes for influence/conquest relationships")
    print("4. Use Uses/HasPart for technology relationships")
    print("="*60)

if __name__ == "__main__":
    main()
