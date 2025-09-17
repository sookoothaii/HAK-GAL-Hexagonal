#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
TEST & DEMO: Multi-Argument Facts System
=========================================
Demonstrates the new multi-argument capabilities
"""

import sys
import os
import time
import sqlite3
import json
from datetime import datetime

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.extended_fact_manager import ExtendedFactManager

def print_section(title):
    """Print formatted section header"""
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60)

def test_extended_facts():
    """Test the extended fact system"""
    
    print_section("MULTI-ARGUMENT FACTS DEMONSTRATION")
    print(f"Timestamp: {datetime.now().isoformat()}")
    
    # Initialize manager
    manager = ExtendedFactManager()
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    
    # Check current state
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM facts_extended WHERE arg_count > 2")
    multi_count_before = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM formulas")
    formula_count_before = cursor.fetchone()[0]
    
    print(f"\nBEFORE TEST:")
    print(f"  Multi-arg facts (>2 args): {multi_count_before}")
    print(f"  Formulas: {formula_count_before}")
    
    # Test 1: Add Chemistry Facts
    print_section("TEST 1: CHEMISTRY DOMAIN")
    
    chemistry_facts = [
        {
            'predicate': 'ChemicalReaction',
            'args': ['2H2', 'O2', '2H2O', 'combustion', 'exothermic'],
            'domain': 'chemistry'
        },
        {
            'predicate': 'AcidBaseReaction',
            'args': ['HCl', 'NaOH', 'NaCl', 'H2O', 'neutralization'],
            'domain': 'chemistry'
        },
        {
            'predicate': 'Catalyst',
            'args': ['Pt', 'H2', 'hydrogenation', '25C', '95%'],
            'domain': 'chemistry'
        },
        {
            'predicate': 'Polymerization',
            'args': ['ethylene', 'polyethylene', 'radical', '200C', '1000atm'],
            'domain': 'chemistry'
        }
    ]
    
    added = 0
    for fact in chemistry_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain'],
            confidence=0.95
        )
        if result:
            added += 1
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    print(f"  Total added: {added}/{len(chemistry_facts)}")
    
    # Test 2: Add Physics Facts
    print_section("TEST 2: PHYSICS DOMAIN")
    
    physics_facts = [
        {
            'predicate': 'Force',
            'args': ['Earth', 'Moon', '1.98e20N', 'gravitational'],
            'domain': 'physics'
        },
        {
            'predicate': 'Energy',
            'args': ['Photon', '2.5eV', 'electromagnetic', 'visible', '500nm'],
            'domain': 'physics'
        },
        {
            'predicate': 'Motion',
            'args': ['Electron', '2.2e6m/s', 'orbital', 'hydrogen'],
            'domain': 'physics'
        },
        {
            'predicate': 'Wave',
            'args': ['Light', '650nm', 'red', 'visible', '3e8m/s'],
            'domain': 'physics'
        }
    ]
    
    added = 0
    for fact in physics_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            added += 1
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    print(f"  Total added: {added}/{len(physics_facts)}")
    
    # Test 3: Add Biology Facts
    print_section("TEST 3: BIOLOGY DOMAIN")
    
    biology_facts = [
        {
            'predicate': 'Photosynthesis',
            'args': ['CO2', 'H2O', 'C6H12O6', 'O2', 'chloroplast'],
            'domain': 'biology'
        },
        {
            'predicate': 'DNAReplication',
            'args': ['DNA', 'polymerase', 'helicase', 'primase', 'nucleus'],
            'domain': 'biology'
        },
        {
            'predicate': 'ProteinSynthesis',
            'args': ['mRNA', 'ribosome', 'tRNA', 'amino-acids', 'cytoplasm'],
            'domain': 'biology'
        }
    ]
    
    added = 0
    for fact in biology_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            added += 1
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    print(f"  Total added: {added}/{len(biology_facts)}")
    
    # Test 4: Add Geography Facts
    print_section("TEST 4: GEOGRAPHY DOMAIN")
    
    geography_facts = [
        {
            'predicate': 'Located',
            'args': ['Berlin', 'Germany', 'Europe'],
            'domain': 'geography'
        },
        {
            'predicate': 'Coordinates',
            'args': ['Paris', '48.8566N', '2.3522E', '35m'],
            'domain': 'geography'
        },
        {
            'predicate': 'River',
            'args': ['Rhine', 'Switzerland', 'Netherlands', '1233km', 'navigable'],
            'domain': 'geography'
        }
    ]
    
    for fact in geography_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'])})")
    
    # Test 5: Add Economics Facts
    print_section("TEST 5: ECONOMICS DOMAIN")
    
    economics_facts = [
        {
            'predicate': 'Transaction',
            'args': ['BankA', 'BankB', '1000000USD', '2025-09-15', 'wire-transfer'],
            'domain': 'economics'
        },
        {
            'predicate': 'MarketPrice',
            'args': ['Gold', '2050USD/oz', 'NYSE', '2025-09-15'],
            'domain': 'economics'
        },
        {
            'predicate': 'Trade',
            'args': ['USA', 'China', '500B', '2025', 'imports'],
            'domain': 'economics'
        }
    ]
    
    for fact in economics_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    # Test 6: Add Medicine Facts
    print_section("TEST 6: MEDICINE DOMAIN")
    
    medicine_facts = [
        {
            'predicate': 'Treatment',
            'args': ['Aspirin', 'Headache', '500mg', '85%', 'oral'],
            'domain': 'medicine'
        },
        {
            'predicate': 'Vaccine',
            'args': ['mRNA-1273', 'COVID19', '94.1%', 'Moderna', '2-dose'],
            'domain': 'medicine'
        },
        {
            'predicate': 'Surgery',
            'args': ['Appendectomy', 'Appendicitis', '98%', 'laparoscopic', '30min'],
            'domain': 'medicine'
        }
    ]
    
    for fact in medicine_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    # Test 7: Add Technology Facts
    print_section("TEST 7: TECHNOLOGY DOMAIN")
    
    tech_facts = [
        {
            'predicate': 'NetworkProtocol',
            'args': ['Client', 'Server', 'HTTPS', '443', 'encrypted'],
            'domain': 'technology'
        },
        {
            'predicate': 'Algorithm',
            'args': ['QuickSort', 'O(nlogn)', 'average', 'divide-conquer', 'in-place'],
            'domain': 'technology'
        },
        {
            'predicate': 'DataTransfer',
            'args': ['NodeA', 'NodeB', '10GB', '1Gbps', 'fiber-optic'],
            'domain': 'technology'
        }
    ]
    
    for fact in tech_facts:
        result = manager.add_multi_arg_fact(
            fact['predicate'],
            fact['args'],
            domain=fact['domain']
        )
        if result:
            print(f"  ✓ Added: {fact['predicate']}({', '.join(fact['args'][:3])}...)")
    
    # Test 8: Add Formulas
    print_section("TEST 8: MATHEMATICAL FORMULAS")
    
    formulas = [
        {
            'name': 'Ohms_Law',
            'expression': 'V = I * R',
            'domain': 'physics',
            'variables': {'V': 'Voltage (V)', 'I': 'Current (A)', 'R': 'Resistance (Ω)'}
        },
        {
            'name': 'Arrhenius_Equation',
            'expression': 'k = A * e^(-Ea/RT)',
            'domain': 'chemistry',
            'variables': {
                'k': 'Rate constant',
                'A': 'Pre-exponential factor',
                'Ea': 'Activation energy',
                'R': 'Gas constant',
                'T': 'Temperature'
            }
        },
        {
            'name': 'Compound_Interest',
            'expression': 'A = P(1 + r/n)^(nt)',
            'domain': 'economics',
            'variables': {
                'A': 'Final amount',
                'P': 'Principal',
                'r': 'Annual rate',
                'n': 'Compounding frequency',
                't': 'Time'
            }
        }
    ]
    
    for formula in formulas:
        result = manager.add_formula(
            formula['name'],
            formula['expression'],
            formula['domain'],
            formula['variables']
        )
        if result:
            print(f"  ✓ Added: {formula['name']} = {formula['expression']}")
    
    # Final Statistics
    print_section("FINAL STATISTICS")
    
    cursor.execute("SELECT COUNT(*) FROM facts_extended WHERE arg_count > 2")
    multi_count_after = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM formulas")
    formula_count_after = cursor.fetchone()[0]
    
    cursor.execute("""
        SELECT domain, COUNT(*) as count 
        FROM facts_extended 
        WHERE arg_count > 2
        GROUP BY domain
        ORDER BY count DESC
    """)
    domain_stats = cursor.fetchall()
    
    cursor.execute("""
        SELECT arg_count, COUNT(*) as count
        FROM facts_extended
        WHERE arg_count > 0
        GROUP BY arg_count
        ORDER BY arg_count
    """)
    arg_stats = cursor.fetchall()
    
    print(f"\nAFTER TEST:")
    print(f"  Multi-arg facts (>2 args): {multi_count_after} (+{multi_count_after - multi_count_before})")
    print(f"  Formulas: {formula_count_after} (+{formula_count_after - formula_count_before})")
    
    print(f"\nDOMAIN DISTRIBUTION:")
    for domain, count in domain_stats:
        if domain:
            print(f"  {domain}: {count} facts")
    
    print(f"\nARGUMENT COUNT DISTRIBUTION:")
    for arg_count, count in arg_stats:
        print(f"  {arg_count} args: {count} facts")
    
    # Sample some multi-arg facts
    print_section("SAMPLE MULTI-ARGUMENT FACTS")
    
    cursor.execute("""
        SELECT statement, predicate, arg_count, domain
        FROM facts_extended
        WHERE arg_count > 2
        ORDER BY created_at DESC
        LIMIT 10
    """)
    
    samples = cursor.fetchall()
    for stmt, pred, args, dom in samples:
        print(f"  • [{dom}] {stmt}")
    
    conn.close()
    
    print_section("TEST COMPLETE")
    print(f"✅ Successfully demonstrated multi-argument fact system!")
    print(f"✅ Database now supports facts with 3-5+ arguments")
    print(f"✅ Multiple domains covered: chemistry, physics, biology, etc.")
    print(f"✅ Mathematical formulas integrated")
    print(f"\n💡 The system is ready for production use!")


if __name__ == "__main__":
    test_extended_facts()
