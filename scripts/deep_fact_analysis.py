#!/usr/bin/env python
"""
DEEP FACT ANALYSIS - Findet ALLE problematischen Facts
========================================================
Inkl. Code-Snippets, Dateipfade, etc.
"""

import sqlite3
from pathlib import Path
import json

def deep_fact_analysis():
    """Tiefgehende Analyse ALLER Facts"""
    
    print("="*70)
    print("🔍 DEEP FACT ANALYSIS - Finding ALL Problems")
    print("="*70)
    
    db_path = Path("hexagonal_kb.db")
    
    if not db_path.exists():
        print("❌ Database not found!")
        return
    
    with sqlite3.connect(str(db_path)) as conn:
        # Get ALL facts
        cursor = conn.execute("SELECT rowid, statement FROM facts ORDER BY rowid DESC LIMIT 500")
        all_facts = cursor.fetchall()
        
        print(f"\n📊 Analyzing last 500 facts...")
        
        # Categories
        code_facts = []
        path_facts = []
        import_facts = []
        typescript_facts = []
        normal_facts = []
        weird_facts = []
        
        for rowid, statement in all_facts:
            # Check for code/path patterns
            if any(x in statement for x in ['\\\\', '/', '.tsx', '.ts', '.js', 'frontend', 'src']):
                path_facts.append((rowid, statement))
            elif 'import ' in statement or 'export ' in statement or 'from ' in statement:
                import_facts.append((rowid, statement))
            elif any(x in statement for x in ['const ', 'let ', 'var ', 'function ', 'class ', '=>']):
                typescript_facts.append((rowid, statement))
            elif any(x in statement for x in ['console.', 'document.', 'window.', 'React.', 'useState']):
                code_facts.append((rowid, statement))
            elif '(' in statement and ')' in statement:
                # Check if it's a normal predicate
                predicate = statement[:statement.index('(')] if '(' in statement else ''
                if predicate in ['IsA', 'HasProperty', 'Causes', 'RelatedTo', 'Contains', 'PartOf', 
                               'UsedFor', 'LocatedIn', 'CreatedBy', 'Requires', 'Influences']:
                    normal_facts.append((rowid, statement))
                else:
                    weird_facts.append((rowid, statement))
            else:
                weird_facts.append((rowid, statement))
        
        # Report findings
        print("\n" + "="*70)
        print("PROBLEMATIC FACTS FOUND:")
        print("="*70)
        
        if path_facts:
            print(f"\n❌ FILE PATHS AS FACTS: {len(path_facts)}")
            for rowid, stmt in path_facts[:3]:
                print(f"   [{rowid}] {stmt[:100]}...")
        
        if import_facts:
            print(f"\n❌ IMPORT STATEMENTS AS FACTS: {len(import_facts)}")
            for rowid, stmt in import_facts[:3]:
                print(f"   [{rowid}] {stmt[:100]}...")
        
        if typescript_facts:
            print(f"\n❌ TYPESCRIPT CODE AS FACTS: {len(typescript_facts)}")
            for rowid, stmt in typescript_facts[:3]:
                print(f"   [{rowid}] {stmt[:100]}...")
        
        if code_facts:
            print(f"\n❌ CODE SNIPPETS AS FACTS: {len(code_facts)}")
            for rowid, stmt in code_facts[:3]:
                print(f"   [{rowid}] {stmt[:100]}...")
        
        if weird_facts:
            print(f"\n⚠️ WEIRD/UNKNOWN FACTS: {len(weird_facts)}")
            for rowid, stmt in weird_facts[:3]:
                print(f"   [{rowid}] {stmt[:100]}...")
        
        print(f"\n✅ NORMAL FACTS: {len(normal_facts)}")
        
        # Calculate problem severity
        total = len(all_facts)
        bad_count = len(path_facts) + len(import_facts) + len(typescript_facts) + len(code_facts)
        
        print("\n" + "="*70)
        print("SEVERITY ASSESSMENT:")
        print("="*70)
        print(f"Total Facts Analyzed: {total}")
        print(f"❌ Bad Facts (Code/Paths): {bad_count} ({bad_count/total*100:.1f}%)")
        print(f"⚠️ Weird Facts: {len(weird_facts)} ({len(weird_facts)/total*100:.1f}%)")
        print(f"✅ Normal Facts: {len(normal_facts)} ({len(normal_facts)/total*100:.1f}%)")
        
        if bad_count > 50:
            print("\n🚨 CRITICAL: Database is polluted with CODE!")
            print("   The engines are reading TypeScript files and storing them as facts!")
            print("\n   IMMEDIATE ACTION REQUIRED:")
            print("   1. STOP THE GOVERNOR NOW!")
            print("   2. Run: python emergency_remove_code_facts.py")
            print("   3. Fix the engines to prevent this!")
        
        # Save detailed report
        report = {
            'path_facts': len(path_facts),
            'import_facts': len(import_facts),
            'typescript_facts': len(typescript_facts),
            'code_facts': len(code_facts),
            'weird_facts': len(weird_facts),
            'normal_facts': len(normal_facts),
            'samples': {
                'paths': [stmt[:200] for _, stmt in path_facts[:5]],
                'imports': [stmt[:200] for _, stmt in import_facts[:5]],
                'code': [stmt[:200] for _, stmt in code_facts[:5]]
            }
        }
        
        with open('deep_analysis_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        print(f"\n📁 Detailed report saved: deep_analysis_report.json")
        
        return bad_count

if __name__ == "__main__":
    bad_count = deep_fact_analysis()
    
    if bad_count and bad_count > 50:
        print("\n" + "="*70)
        print("🚨 EMERGENCY: YOUR DATABASE IS FULL OF CODE!")
        print("="*70)
        print("Run IMMEDIATELY: python emergency_remove_code_facts.py")
