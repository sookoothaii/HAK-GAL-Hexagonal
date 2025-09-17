#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PROOF OF CONCEPT: Extended Facts Demo
Zeigt die Möglichkeiten der erweiterten DB-Struktur
"""

import sqlite3
import json
from datetime import datetime

class ExtendedFactsDemo:
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        
    def demonstrate_multi_argument_facts(self):
        """Zeige Multi-Argument Fähigkeiten"""
        
        examples = [
            # 3-Argument Beispiele
            {
                'statement': 'Located(Eiffel_Tower, Paris, France)',
                'predicate': 'Located',
                'arg_count': 3,
                'arg1': 'Eiffel_Tower',
                'arg2': 'Paris', 
                'arg3': 'France',
                'fact_type': 'geographical',
                'domain': 'geography'
            },
            
            # 4-Argument Beispiele  
            {
                'statement': 'Transaction(Alice, Bob, 100EUR, 2025-09-15T20:00:00)',
                'predicate': 'Transaction',
                'arg_count': 4,
                'arg1': 'Alice',
                'arg2': 'Bob',
                'arg3': '100EUR',
                'arg4': '2025-09-15T20:00:00',
                'fact_type': 'financial',
                'domain': 'economics'
            },
            
            # 5-Argument Beispiele
            {
                'statement': 'ChemicalReaction(2H2, O2, 2H2O, combustion, exothermic)',
                'predicate': 'ChemicalReaction',
                'arg_count': 5,
                'arg1': '2H2',
                'arg2': 'O2',
                'arg3': '2H2O',
                'arg4': 'combustion',
                'arg5': 'exothermic',
                'fact_type': 'chemical',
                'domain': 'chemistry'
            },
            
            # >5 Argumente (JSON)
            {
                'statement': 'WeatherData(Berlin, 2025-09-15, 22C, 65%, 1013hPa, cloudy, 10km/h, NW)',
                'predicate': 'WeatherData',
                'arg_count': 8,
                'arg1': 'Berlin',
                'arg2': '2025-09-15',
                'arg3': '22C',
                'arg4': '65%',
                'arg5': '1013hPa',
                'args_json': json.dumps({
                    'arg6': 'cloudy',
                    'arg7': '10km/h', 
                    'arg8': 'NW'
                }),
                'fact_type': 'measurement',
                'domain': 'meteorology',
                'complexity': 3
            }
        ]
        
        print("=" * 60)
        print("MULTI-ARGUMENT FACTS EXAMPLES")
        print("=" * 60)
        
        for ex in examples:
            print(f"\n{ex['statement']}")
            print(f"  Domain: {ex.get('domain', 'general')}")
            print(f"  Type: {ex.get('fact_type', 'standard')}")
            print(f"  Args: {ex['arg_count']}")
            if ex['arg_count'] > 5:
                print(f"  Extended: {ex.get('args_json', '{}')}")
    
    def demonstrate_formulas(self):
        """Zeige Formel-Fähigkeiten"""
        
        formulas = [
            {
                'name': 'newtons_second_law',
                'expression': 'F = m * a',
                'domain': 'physics',
                'variables': json.dumps({
                    'F': 'Force in Newtons',
                    'm': 'Mass in kg',
                    'a': 'Acceleration in m/s²'
                }),
                'constants': json.dumps({})
            },
            
            {
                'name': 'ideal_gas_law',
                'expression': 'P * V = n * R * T',
                'domain': 'chemistry',
                'variables': json.dumps({
                    'P': 'Pressure in atm',
                    'V': 'Volume in L',
                    'n': 'Moles of gas',
                    'T': 'Temperature in K'
                }),
                'constants': json.dumps({
                    'R': '0.08206 L·atm/(mol·K)'
                })
            },
            
            {
                'name': 'quadratic_formula',
                'expression': 'x = (-b ± √(b² - 4ac)) / 2a',
                'domain': 'mathematics',
                'variables': json.dumps({
                    'x': 'Solution',
                    'a': 'Quadratic coefficient',
                    'b': 'Linear coefficient',
                    'c': 'Constant term'
                }),
                'constants': json.dumps({})
            },
            
            {
                'name': 'compound_interest',
                'expression': 'A = P(1 + r/n)^(nt)',
                'domain': 'finance',
                'variables': json.dumps({
                    'A': 'Final amount',
                    'P': 'Principal',
                    'r': 'Annual interest rate',
                    'n': 'Compounding frequency',
                    't': 'Time in years'
                }),
                'constants': json.dumps({})
            }
        ]
        
        print("\n" + "=" * 60)
        print("FORMULA EXAMPLES")
        print("=" * 60)
        
        for formula in formulas:
            print(f"\n{formula['name']}:")
            print(f"  {formula['expression']}")
            print(f"  Domain: {formula['domain']}")
            vars = json.loads(formula['variables'])
            print(f"  Variables: {', '.join(vars.keys())}")
            if formula['constants'] != '{}':
                consts = json.loads(formula['constants'])
                print(f"  Constants: {consts}")
    
    def demonstrate_complex_relations(self):
        """Zeige komplexe Relationen"""
        
        # Beispiel für fact_dependencies
        dependencies = [
            {
                'parent': 'Energy(System1, 500J, kinetic)',
                'child': 'Energy(System1, 500J, potential)',
                'type': 'energy_conversion',
                'strength': 1.0
            },
            {
                'parent': 'Temperature(Water, 100C)',
                'child': 'State(Water, gas)',
                'type': 'phase_transition',
                'strength': 0.95
            }
        ]
        
        # Beispiel für fact_relations
        relations = [
            {
                'relation_type': 'causal_chain',
                'entities': json.dumps([
                    'CO2_emissions',
                    'greenhouse_effect',
                    'global_warming',
                    'sea_level_rise'
                ]),
                'strength': 0.85,
                'context': 'climate_science'
            },
            {
                'relation_type': 'supply_chain',
                'entities': json.dumps([
                    'raw_materials',
                    'manufacturing',
                    'distribution',
                    'retail',
                    'consumer'
                ]),
                'strength': 1.0,
                'context': 'economics'
            }
        ]
        
        print("\n" + "=" * 60)
        print("COMPLEX RELATIONS EXAMPLES")
        print("=" * 60)
        
        print("\nDependencies:")
        for dep in dependencies:
            print(f"  {dep['parent']} --{dep['type']}--> {dep['child']}")
            print(f"    Strength: {dep['strength']}")
        
        print("\nMulti-Entity Relations:")
        for rel in relations:
            entities = json.loads(rel['entities'])
            print(f"  {rel['relation_type']}: {' → '.join(entities)}")
            print(f"    Context: {rel['context']}")
    
    def test_insert_extended_fact(self):
        """Test: Füge einen erweiterten Fakt hinzu"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Test-Fakt mit 4 Argumenten
            cursor.execute("""
                INSERT INTO facts_extended (
                    statement, predicate, arg_count,
                    arg1, arg2, arg3, arg4,
                    fact_type, domain, complexity, confidence
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                'TestReaction(H2SO4, NaOH, Na2SO4, H2O)',
                'TestReaction', 4,
                'H2SO4', 'NaOH', 'Na2SO4', 'H2O',
                'chemical', 'chemistry', 2, 0.95
            ))
            
            conn.commit()
            print("\n✅ Extended fact successfully inserted!")
            
            # Verify
            cursor.execute("""
                SELECT * FROM facts_extended 
                WHERE statement = 'TestReaction(H2SO4, NaOH, Na2SO4, H2O)'
            """)
            result = cursor.fetchone()
            if result:
                print("Verified in DB!")
            
        except sqlite3.IntegrityError:
            print("Fact already exists")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            conn.close()
    
    def show_current_capabilities(self):
        """Zeige was die DB JETZT schon kann"""
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check facts_extended
        cursor.execute("SELECT COUNT(*) FROM facts_extended")
        extended_count = cursor.fetchone()[0]
        
        # Check formulas
        cursor.execute("SELECT COUNT(*) FROM formulas")
        formula_count = cursor.fetchone()[0]
        
        # Check fact_arguments
        cursor.execute("SELECT COUNT(*) FROM fact_arguments")
        arg_count = cursor.fetchone()[0]
        
        conn.close()
        
        print("\n" + "=" * 60)
        print("CURRENT DATABASE CAPABILITIES")
        print("=" * 60)
        print(f"Extended Facts: {extended_count}")
        print(f"Formulas: {formula_count}")
        print(f"Fact Arguments: {arg_count}")
        print("\n✅ Database READY for multi-argument facts!")
        print("✅ Database READY for formulas!")
        print("✅ Database READY for complex relations!")
        print("\n❌ Engines NOT using these features yet!")

def main():
    demo = ExtendedFactsDemo()
    
    # Zeige Möglichkeiten
    demo.demonstrate_multi_argument_facts()
    demo.demonstrate_formulas()
    demo.demonstrate_complex_relations()
    demo.show_current_capabilities()
    
    # Optional: Test insert
    # demo.test_insert_extended_fact()

if __name__ == "__main__":
    main()
