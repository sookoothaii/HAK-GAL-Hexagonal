#!/usr/bin/env python3
"""
INTELLIGENT FACT GENERATOR - Wissenschaftlich korrekte Faktengenerierung
=========================================================================
Ersetzt den fehlerhaften SimpleFactGenerator mit intelligenter, 
validierter Faktengenerierung.
"""

import os
import time
import random
import requests
import sqlite3
from typing import List, Dict, Tuple, Set, Optional
from collections import defaultdict

# Auth Token
AUTH_TOKEN = os.environ.get('HAKGAL_AUTH_TOKEN', '515f57956e7bd15ddc3817573598f190')
API_BASE = 'http://127.0.0.1:5002'

class IntelligentFactGenerator:
    """
    Intelligenter Faktengenerator mit wissenschaftlicher Validierung
    """
    
    def __init__(self):
        self.headers = {
            'Content-Type': 'application/json',
            'X-API-Key': AUTH_TOKEN
        }
        
        # Wissenschaftlich korrekte Fakten-Templates
        self.knowledge_base = self._initialize_knowledge_base()
        
        # Tracking
        self.generated_facts = set()
        self.stats = defaultdict(int)
        
    def _initialize_knowledge_base(self) -> Dict:
        """
        Initialisiert wissenschaftlich korrekte Fakten-Templates
        """
        return {
            'chemistry': {
                'molecules': {
                    'H2O': {
                        'consists_of': ['hydrogen', 'oxygen'],
                        'properties': ['polar', 'solvent', 'liquid'],
                        'type': 'molecule'
                    },
                    'CO2': {
                        'consists_of': ['carbon', 'oxygen'],
                        'properties': ['nonpolar', 'gas', 'greenhouse'],
                        'type': 'molecule'
                    },
                    'NH3': {
                        'consists_of': ['nitrogen', 'hydrogen'],
                        'properties': ['polar', 'basic', 'pungent'],
                        'type': 'molecule'
                    },
                    'CH4': {
                        'consists_of': ['carbon', 'hydrogen'],
                        'properties': ['nonpolar', 'gas', 'flammable'],
                        'type': 'molecule'
                    },
                    'NaCl': {
                        'consists_of': ['sodium', 'chlorine'],
                        'properties': ['ionic', 'crystalline', 'soluble'],
                        'type': 'compound'
                    }
                }
            },
            'biology': {
                'cellular': {
                    'cell': {
                        'has_parts': ['membrane', 'cytoplasm', 'ribosomes'],
                        'types': ['prokaryotic', 'eukaryotic'],
                        'functions': ['metabolism', 'reproduction', 'homeostasis']
                    },
                    'DNA': {
                        'consists_of': ['nucleotides', 'phosphate_backbone', 'bases'],
                        'has_parts': ['adenine', 'thymine', 'guanine', 'cytosine'],
                        'functions': ['heredity', 'protein_coding', 'replication']
                    },
                    'protein': {
                        'consists_of': ['amino_acids'],
                        'functions': ['catalysis', 'structure', 'transport', 'signaling'],
                        'synthesized_by': 'ribosomes'
                    },
                    'mitochondria': {
                        'function': 'energy_production',
                        'produces': 'ATP',
                        'has_parts': ['inner_membrane', 'outer_membrane', 'matrix']
                    }
                },
                'organisms': {
                    'bacteria': {
                        'type': 'prokaryote',
                        'lacks': ['nucleus', 'membrane_bound_organelles'],
                        'has': ['cell_wall', 'plasmids', 'flagella']
                    },
                    'virus': {
                        'consists_of': ['protein_coat', 'nucleic_acid'],
                        'requires': 'host_cell',
                        'lacks': ['metabolism', 'cellular_structure']
                    }
                }
            },
            'physics': {
                'particles': {
                    'electron': {
                        'properties': ['negative_charge', 'mass', 'spin'],
                        'type': 'lepton',
                        'location': 'electron_shell'
                    },
                    'proton': {
                        'properties': ['positive_charge', 'mass'],
                        'consists_of': ['quarks'],
                        'location': 'nucleus'
                    },
                    'photon': {
                        'properties': ['no_mass', 'speed_of_light', 'energy'],
                        'type': 'boson',
                        'carries': 'electromagnetic_force'
                    }
                },
                'forces': {
                    'gravity': {
                        'type': 'fundamental_force',
                        'affects': 'mass',
                        'range': 'infinite'
                    },
                    'electromagnetism': {
                        'type': 'fundamental_force',
                        'carrier': 'photon',
                        'affects': 'charge'
                    }
                }
            },
            'computer_science': {
                'algorithms': {
                    'quicksort': {
                        'type': 'sorting_algorithm',
                        'complexity': 'O(n_log_n)',
                        'uses': 'divide_and_conquer'
                    },
                    'dijkstra': {
                        'type': 'pathfinding_algorithm',
                        'finds': 'shortest_path',
                        'requires': 'weighted_graph'
                    }
                },
                'data_structures': {
                    'hash_table': {
                        'provides': 'O(1)_lookup',
                        'uses': 'hash_function',
                        'handles': 'collisions'
                    },
                    'binary_tree': {
                        'has_parts': ['root', 'left_subtree', 'right_subtree'],
                        'property': 'hierarchical',
                        'operations': ['insert', 'delete', 'search']
                    }
                },
                'networking': {
                    'TCP': {
                        'provides': 'reliable_transmission',
                        'uses': 'three_way_handshake',
                        'layer': 'transport'
                    },
                    'HTTP': {
                        'type': 'application_protocol',
                        'uses': 'TCP',
                        'methods': ['GET', 'POST', 'PUT', 'DELETE']
                    }
                }
            },
            'mathematics': {
                'calculus': {
                    'derivative': {
                        'measures': 'rate_of_change',
                        'inverse_of': 'integral',
                        'uses': 'limits'
                    },
                    'integral': {
                        'calculates': 'area_under_curve',
                        'inverse_of': 'derivative',
                        'types': ['definite', 'indefinite']
                    }
                },
                'algebra': {
                    'matrix': {
                        'operations': ['multiplication', 'inversion', 'transpose'],
                        'used_in': ['linear_systems', 'transformations'],
                        'has_property': 'determinant'
                    }
                }
            }
        }
    
    def generate_fact_from_knowledge(self, domain: str, max_attempts: int = 10) -> Optional[str]:
        """
        Generiert einen wissenschaftlich korrekten Fakt aus der Knowledge Base
        """
        if domain not in self.knowledge_base:
            return None
            
        for _ in range(max_attempts):
            # Wähle zufällige Kategorie
            category = random.choice(list(self.knowledge_base[domain].keys()))
            entities = self.knowledge_base[domain][category]
            
            # Wähle zufällige Entität
            entity = random.choice(list(entities.keys()))
            entity_data = entities[entity]
            
            # Generiere Fakt basierend auf verfügbaren Daten
            fact_type = random.choice(list(entity_data.keys()))
            
            if fact_type == 'consists_of':
                components = entity_data['consists_of']
                if len(components) == 2:
                    fact = f"ConsistsOf({entity}, {components[0]}, {components[1]})."
                elif len(components) == 1:
                    fact = f"ConsistsOf({entity}, {components[0]})."
                else:
                    fact = f"ConsistsOf({entity}, {', '.join(components[:3])})."
                    
            elif fact_type == 'properties':
                prop = random.choice(entity_data['properties'])
                fact = f"HasProperty({entity}, {prop})."
                
            elif fact_type == 'type':
                fact = f"IsTypeOf({entity}, {entity_data['type']})."
                
            elif fact_type == 'has_parts':
                parts = entity_data['has_parts']
                part = random.choice(parts)
                fact = f"HasPart({entity}, {part})."
                
            elif fact_type == 'functions' or fact_type == 'function':
                if isinstance(entity_data[fact_type], list):
                    function = random.choice(entity_data[fact_type])
                else:
                    function = entity_data[fact_type]
                fact = f"HasPurpose({entity}, {function})."
                
            elif fact_type == 'requires':
                fact = f"Requires({entity}, {entity_data['requires']})."
                
            elif fact_type == 'produces':
                fact = f"Produces({entity}, {entity_data['produces']})."
                
            elif fact_type == 'uses':
                fact = f"Uses({entity}, {entity_data['uses']})."
                
            elif fact_type == 'lacks':
                thing = random.choice(entity_data['lacks'])
                fact = f"Lacks({entity}, {thing})."
                
            elif fact_type == 'synthesized_by':
                fact = f"ProducedBy({entity}, {entity_data['synthesized_by']})."
                
            elif fact_type == 'affects':
                fact = f"Affects({entity_data.get('type', entity)}, {entity_data['affects']})."
                
            elif fact_type == 'complexity':
                fact = f"HasProperty({entity}, complexity_{entity_data['complexity']})."
                
            else:
                continue
                
            # Prüfe ob Fakt neu ist
            if fact not in self.generated_facts:
                self.generated_facts.add(fact)
                return fact
        
        return None
    
    def generate_cross_domain_fact(self) -> Optional[str]:
        """
        Generiert domänenübergreifende Verbindungen (vorsichtig!)
        """
        facts = [
            "Uses(machine_learning, matrix).",
            "Requires(quantum_computing, quantum_mechanics).",
            "Uses(cryptography, prime_numbers).",
            "DependsOn(neural_networks, calculus).",
            "Uses(protein_folding, algorithms).",
            "Requires(DNA_sequencing, computers).",
            "Uses(climate_modeling, differential_equations).",
            "DependsOn(drug_discovery, molecular_biology).",
            "Uses(particle_physics, statistics).",
            "Requires(space_exploration, physics)."
        ]
        
        available = [f for f in facts if f not in self.generated_facts]
        if available:
            fact = random.choice(available)
            self.generated_facts.add(fact)
            return fact
        
        return None
    
    def validate_fact(self, fact: str) -> bool:
        """
        Validiert einen Fakt auf offensichtliche Fehler
        """
        # Bekannte chemische Fehler
        invalid_combinations = [
            ('NH3', 'oxygen'),  # NH3 enthält keinen Sauerstoff
            ('H2O', 'carbon'),  # H2O enthält keinen Kohlenstoff  
            ('CH4', 'oxygen'),  # CH4 enthält keinen Sauerstoff
            ('CO2', 'hydrogen'),  # CO2 enthält keinen Wasserstoff in ConsistsOf
            ('virus', 'organ'),  # Viren haben keine Organe
            ('bacteria', 'nucleus')  # Bakterien haben keinen echten Zellkern
        ]
        
        fact_lower = fact.lower()
        for invalid in invalid_combinations:
            if invalid[0].lower() in fact_lower and invalid[1].lower() in fact_lower:
                if 'consistsof' in fact_lower or 'haspart' in fact_lower:
                    return False
        
        return True
    
    def add_fact_to_kb(self, fact: str) -> bool:
        """
        Fügt einen Fakt zur Knowledge Base hinzu
        """
        if not self.validate_fact(fact):
            self.stats['rejected_invalid'] += 1
            return False
        
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
                self.stats['duplicates'] += 1
                return False
            else:
                self.stats['api_errors'] += 1
                return False
                
        except Exception as e:
            self.stats['api_errors'] += 1
            print(f"API Error: {e}")
            return False
    
    def run(self, duration_minutes: float = 1.0):
        """
        Hauptgenerierungsschleife
        """
        print("="*80)
        print("INTELLIGENT FACT GENERATOR - Wissenschaftlich korrekte Faktengenerierung")
        print("="*80)
        print(f"Dauer: {duration_minutes} Minuten")
        print(f"API: {API_BASE}")
        print("Features: Wissenschaftliche Validierung, Keine falschen Kombinationen")
        print("-"*80)
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        domains = list(self.knowledge_base.keys())
        batch_count = 0
        
        while time.time() < end_time:
            batch_count += 1
            batch_facts = []
            
            # Generiere Batch von Fakten
            for _ in range(5):
                # 80% domänenspezifisch, 20% cross-domain
                if random.random() < 0.8:
                    domain = random.choice(domains)
                    fact = self.generate_fact_from_knowledge(domain)
                else:
                    fact = self.generate_cross_domain_fact()
                
                if fact:
                    batch_facts.append(fact)
            
            # Füge Fakten hinzu
            for fact in batch_facts:
                if self.add_fact_to_kb(fact):
                    print(f"✓ {fact}")
                time.sleep(0.1)  # Rate limiting
            
            # Statistik-Update
            if batch_count % 10 == 0:
                elapsed = (time.time() - start_time) / 60
                rate = self.stats['facts_added'] / elapsed if elapsed > 0 else 0
                print(f"\n📊 Zwischenstand: {self.stats['facts_added']} Fakten, "
                      f"{rate:.1f} Fakten/Min, "
                      f"{self.stats['rejected_invalid']} abgelehnt")
            
            # Pause zwischen Batches
            time.sleep(2)
        
        # Abschlussbericht
        total_time = (time.time() - start_time) / 60
        print("\n" + "="*80)
        print("GENERIERUNG ABGESCHLOSSEN")
        print("-"*80)
        print(f"✅ Fakten hinzugefügt: {self.stats['facts_added']}")
        print(f"❌ Ungültige abgelehnt: {self.stats['rejected_invalid']}")
        print(f"⚠️  Duplikate: {self.stats['duplicates']}")
        print(f"🔴 API Fehler: {self.stats['api_errors']}")
        print(f"⏱️  Zeit: {total_time:.1f} Minuten")
        print(f"📊 Rate: {self.stats['facts_added']/total_time:.1f} Fakten/Minute")
        print("="*80)
    
    def print_sample_facts(self, count: int = 10):
        """
        Zeigt Beispiel-Fakten zur Qualitätskontrolle
        """
        print(f"\n📝 Beispiel generierte Fakten:")
        domains = list(self.knowledge_base.keys())
        
        for i in range(count):
            domain = random.choice(domains)
            fact = self.generate_fact_from_knowledge(domain)
            if fact:
                valid = "✓" if self.validate_fact(fact) else "✗"
                print(f"{valid} {fact}")


def main():
    """
    Hauptfunktion zum Testen
    """
    generator = IntelligentFactGenerator()
    
    print("Teste Faktengenerierung...\n")
    generator.print_sample_facts(20)
    
    print("\n" + "-"*80)
    choice = input("Starte Generierung? (j/n): ")
    
    if choice.lower() == 'j':
        duration = float(input("Dauer in Minuten (Standard: 0.5): ") or "0.5")
        generator.run(duration_minutes=duration)


if __name__ == "__main__":
    main()
