#!/usr/bin/env python3
"""
Query and explore extended facts from the main database
"""

import sqlite3
import json
from typing import List, Dict
from ekr_implementation import EKRDatabase, FactType

def explore_main_database():
    """Explore extended facts in main database"""
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    print(f"📚 Exploring Extended Knowledge in {db_path}")
    print("="*60)
    
    # Connect using EKRDatabase for full functionality
    db = EKRDatabase(db_path)
    
    # 1. Show overall statistics
    print("\n📊 Database Statistics:")
    
    try:
        total = db.conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
        print(f"Total extended facts: {total}")
    except:
        print("No extended facts table yet")
        return
    
    # 2. Show type distribution
    print("\n📈 Fact Types:")
    for fact_type in [FactType.BINARY, FactType.NARY, FactType.TYPED, 
                     FactType.FORMULA, FactType.TEMPORAL, FactType.GRAPH]:
        facts = db.query_by_type(fact_type)
        if facts:
            print(f"\n{fact_type.value.upper()} ({len(facts)} facts):")
            for fact in facts[:2]:  # Show first 2 of each type
                statement = fact['statement']
                if len(statement) > 70:
                    print(f"  • {statement[:70]}...")
                else:
                    print(f"  • {statement}")
    
    # 3. Query n-ary relations with high arity
    print("\n🔗 Complex N-ary Relations (4+ arguments):")
    complex_nary = db.query_nary_by_arity(4)
    for fact in complex_nary[:3]:
        print(f"  • {fact['statement'][:80]}...")
        print(f"    Arity: {fact.get('arity', 'unknown')}")
    
    # 4. Query formulas by domain
    print("\n📐 Mathematical Formulas:")
    for domain in ['Physics', 'Mathematics', 'Chemistry']:
        formulas = db.query_formulas_by_domain(domain)
        if formulas:
            print(f"\n{domain}:")
            for formula in formulas[:2]:
                print(f"  • {formula['name']}: {formula['expression']}")
    
    # 5. Search for typed arguments
    print("\n🏷️ Facts with Typed Arguments:")
    typed_facts = db.query_by_type(FactType.TYPED)
    for fact in typed_facts[:3]:
        data = json.loads(fact['fact_json'])
        roles = []
        for arg in data['arguments']:
            if isinstance(arg, dict) and 'role' in arg:
                roles.append(arg['role'])
        print(f"  • {fact['statement'][:60]}...")
        print(f"    Roles: {', '.join(roles)}")
    
    # 6. Custom queries
    print("\n🔍 Custom Queries:")
    
    # Find all facts about specific entities
    entity = "System"
    cursor = db.conn.execute("""
        SELECT statement FROM facts_v2 
        WHERE statement LIKE ? 
        LIMIT 5
    """, (f"%{entity}%",))
    
    results = cursor.fetchall()
    if results:
        print(f"\nFacts containing '{entity}':")
        for row in results:
            print(f"  • {row[0]}")
    
    # Find recent facts
    cursor = db.conn.execute("""
        SELECT statement, created_at FROM facts_v2 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    recent = cursor.fetchall()
    if recent:
        print(f"\nMost Recent Facts:")
        for row in recent:
            print(f"  • {row[0][:60]}... ({row[1]})")
    
    db.conn.close()
    
    print("\n" + "="*60)
    print("✅ Exploration complete!")


def semantic_search(query: str, limit: int = 5):
    """Simple semantic search in extended facts"""
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    
    print(f"\n🔎 Searching for: '{query}'")
    print("-"*40)
    
    # Search in both tables
    all_results = []
    
    # Search in facts_v2
    try:
        cursor = conn.execute("""
            SELECT statement, fact_type FROM facts_v2 
            WHERE statement LIKE ? 
            LIMIT ?
        """, (f"%{query}%", limit))
        
        for row in cursor:
            all_results.append((row[0], row[1], 'facts_v2'))
    except:
        pass
    
    # Search in original facts table
    try:
        cursor = conn.execute("""
            SELECT statement FROM facts 
            WHERE statement LIKE ? 
            LIMIT ?
        """, (f"%{query}%", limit))
        
        for row in cursor:
            all_results.append((row[0], 'binary', 'facts'))
    except:
        pass
    
    if all_results:
        print(f"Found {len(all_results)} results:")
        for statement, fact_type, table in all_results:
            print(f"  [{fact_type:8s}] {statement[:70]}...")
            print(f"             (from {table})")
    else:
        print(f"No results found for '{query}'")
    
    conn.close()


if __name__ == "__main__":
    # Explore the database
    explore_main_database()
    
    # Example searches
    print("\n" + "="*60)
    print("🔍 Example Searches:")
    semantic_search("Reaction")
    semantic_search("Formula")
    semantic_search("System")
