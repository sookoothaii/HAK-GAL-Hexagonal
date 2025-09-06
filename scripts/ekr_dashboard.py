#!/usr/bin/env python3
"""
EKR Dashboard - Visual overview of the extended knowledge base
"""

import sqlite3
from datetime import datetime
from pathlib import Path
import json

def display_dashboard():
    """Display a comprehensive dashboard of the knowledge base"""
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    
    print("\n" + "="*80)
    print(" "*20 + "🎯 HAK-GAL EKR KNOWLEDGE BASE DASHBOARD")
    print("="*80)
    print(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"📁 Database: {db_path}")
    print("="*80)
    
    conn = sqlite3.connect(db_path)
    
    # 1. OVERALL STATISTICS
    print("\n📊 OVERALL STATISTICS")
    print("-"*40)
    
    # Original facts table
    try:
        count_v1 = conn.execute("SELECT COUNT(*) FROM facts").fetchone()[0]
        print(f"Original Facts (v1):     {count_v1:,}")
    except:
        count_v1 = 0
        print(f"Original Facts (v1):     No table")
    
    # Extended facts table
    try:
        count_v2 = conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
        print(f"Extended Facts (v2):     {count_v2:,}")
    except:
        count_v2 = 0
        print(f"Extended Facts (v2):     No table")
    
    print(f"{'─'*25}")
    print(f"TOTAL FACTS:            {count_v1 + count_v2:,}")
    
    # 2. COMPLEXITY DISTRIBUTION
    if count_v2 > 0:
        print("\n📈 COMPLEXITY DISTRIBUTION (Extended Facts)")
        print("-"*40)
        
        types = conn.execute("""
            SELECT fact_type, COUNT(*) as cnt 
            FROM facts_v2 
            GROUP BY fact_type
            ORDER BY cnt DESC
        """).fetchall()
        
        for fact_type, count in types:
            percentage = (count / count_v2 * 100)
            bar_length = int(percentage / 2)  # Scale to 50 chars max
            bar = "█" * bar_length + "░" * (50 - bar_length)
            print(f"{fact_type:10s} [{bar}] {count:3d} ({percentage:.1f}%)")
    
    # 3. RECENT ACTIVITY
    print("\n🕐 RECENT ACTIVITY")
    print("-"*40)
    
    try:
        # Last 5 extended facts
        recent = conn.execute("""
            SELECT statement, fact_type, created_at 
            FROM facts_v2 
            ORDER BY created_at DESC 
            LIMIT 5
        """).fetchall()
        
        if recent:
            print("Latest Extended Facts:")
            for stmt, ftype, created in recent:
                time_str = created.split()[1] if ' ' in created else created
                if len(stmt) > 50:
                    print(f"  [{ftype:7s}] {stmt[:50]}... ({time_str})")
                else:
                    print(f"  [{ftype:7s}] {stmt} ({time_str})")
    except:
        print("No recent extended facts")
    
    # 4. KNOWLEDGE DOMAINS (from formulas)
    print("\n🎓 KNOWLEDGE DOMAINS")
    print("-"*40)
    
    try:
        domains = conn.execute("""
            SELECT domain, COUNT(*) as cnt 
            FROM formulas 
            GROUP BY domain
        """).fetchall()
        
        if domains:
            print("Scientific Formulas by Domain:")
            for domain, count in domains:
                print(f"  • {domain}: {count} formulas")
        else:
            print("No formulas yet")
    except:
        print("Formula tracking not initialized")
    
    # 5. COMPLEX RELATIONS
    print("\n🔗 COMPLEX RELATIONS")
    print("-"*40)
    
    try:
        # Count n-ary relations with different arities
        nary_stats = conn.execute("""
            SELECT 
                COUNT(CASE WHEN json_array_length(json_extract(fact_json, '$.arguments')) = 3 THEN 1 END) as arity_3,
                COUNT(CASE WHEN json_array_length(json_extract(fact_json, '$.arguments')) = 4 THEN 1 END) as arity_4,
                COUNT(CASE WHEN json_array_length(json_extract(fact_json, '$.arguments')) >= 5 THEN 1 END) as arity_5plus
            FROM facts_v2 
            WHERE fact_type = 'nary'
        """).fetchone()
        
        if nary_stats and any(nary_stats):
            print("N-ary Relations by Argument Count:")
            print(f"  • 3 arguments: {nary_stats[0] or 0}")
            print(f"  • 4 arguments: {nary_stats[1] or 0}")
            print(f"  • 5+ arguments: {nary_stats[2] or 0}")
    except:
        pass
    
    # 6. TOP PREDICATES
    print("\n🏆 TOP PREDICATES")
    print("-"*40)
    
    try:
        # From extended facts
        predicates = conn.execute("""
            SELECT json_extract(fact_json, '$.predicate') as pred, COUNT(*) as cnt
            FROM facts_v2
            GROUP BY pred
            ORDER BY cnt DESC
            LIMIT 5
        """).fetchall()
        
        if predicates:
            print("Most Used Predicates (Extended):")
            for pred, count in predicates:
                if pred:
                    print(f"  {count:3d}x {pred}")
    except:
        pass
    
    # 7. SYSTEM CAPABILITIES
    print("\n✨ SYSTEM CAPABILITIES")
    print("-"*40)
    
    # Check capabilities before closing connection
    has_typed = conn.execute("SELECT COUNT(*) FROM facts_v2 WHERE fact_type='typed'").fetchone()[0] > 0
    has_formula = conn.execute("SELECT COUNT(*) FROM facts_v2 WHERE fact_type='formula'").fetchone()[0] > 0
    has_temporal = conn.execute("SELECT COUNT(*) FROM facts_v2 WHERE fact_type='temporal'").fetchone()[0] > 0
    has_graph = conn.execute("SELECT COUNT(*) FROM facts_v2 WHERE fact_type='graph'").fetchone()[0] > 0
    
    capabilities = [
        ("Binary Facts", "IsA(Entity, Class)", count_v1 > 0),
        ("N-ary Relations", "Connects(A, B, Type, Distance, Time)", count_v2 > 0),
        ("Typed Arguments", "Reaction(catalyst:Pt, substrate:H2)", has_typed),
        ("Formulas", "Formula(name:E=mc², expr:...)", has_formula),
        ("Temporal Logic", "Temporal(fact:X, time:T, duration:D)", has_temporal),
        ("Graph Structures", "Graph(nodes:[...], edges:[...])", has_graph),
    ]
    
    for capability, example, active in capabilities:
        status = "✅" if active else "⏳"
        print(f"{status} {capability:20s} {example[:40]}...")
    
    # 8. GROWTH METRICS
    print("\n📈 GROWTH METRICS")
    print("-"*40)
    
    try:
        # Get creation dates and count growth
        growth = conn.execute("""
            SELECT DATE(created_at) as day, COUNT(*) as cnt
            FROM facts_v2
            GROUP BY day
            ORDER BY day DESC
            LIMIT 7
        """).fetchall()
        
        if growth:
            print("Facts Added Per Day (Last 7 Days):")
            for day, count in growth:
                bar = "█" * min(count, 50)
                print(f"  {day}: {bar} {count}")
    except:
        print("No growth data available")
    
    # Close connection before recommendations
    conn.close()
    
    print("\n" + "="*80)
    print(" "*25 + "🚀 SYSTEM STATUS: OPERATIONAL")
    print("="*80)
    
    # Recommendations
    print("\n💡 RECOMMENDATIONS:")
    if count_v2 < 100:
        print("  • Generate more extended facts: python v6_autopilot_ekr_main_db.py --cycles 20")
    if not has_graph:
        print("  • Add graph structures for network analysis")
    if count_v1 > count_v2 * 10:
        print("  • Consider migrating more v1 facts to v2 format")
    
    print("\n✅ Dashboard generation complete!")


if __name__ == "__main__":
    display_dashboard()
