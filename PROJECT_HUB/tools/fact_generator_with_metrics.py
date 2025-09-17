#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HAK/GAL Fact Generator with Live Metrics
========================================

Generiert Multi-Argument Facts und zeigt Live-Metriken an.
Verwendet die Extended Engine mit Governance Bypass für Testing.

Usage:
    python fact_generator_with_metrics.py [--count N] [--interval SECONDS] [--domains DOMAIN1,DOMAIN2]
    
Examples:
    python fact_generator_with_metrics.py --count 50 --interval 2
    python fact_generator_with_metrics.py --domains chemistry,physics --count 20
"""

import sys
import os
import time
import argparse
import codecs
from datetime import datetime
from collections import defaultdict, Counter
import sqlite3

# Add src_hexagonal to path
sys.path.append('src_hexagonal')

def setup_environment():
    """Setup environment for fact generation"""
    os.environ['GOVERNANCE_BYPASS'] = 'true'
    print("🔧 Environment: GOVERNANCE_BYPASS=true")

def get_db_stats():
    """Get current database statistics"""
    try:
        conn = sqlite3.connect('hexagonal_kb.db')
        cursor = conn.cursor()
        
        # Total facts
        cursor.execute('SELECT COUNT(*) FROM facts_extended')
        total_facts = cursor.fetchone()[0]
        
        # Multi-arg facts
        cursor.execute('SELECT COUNT(*) FROM facts_extended WHERE arg_count > 2')
        multi_arg_facts = cursor.fetchone()[0]
        
        # Recent facts (last hour)
        cursor.execute('''
            SELECT COUNT(*) FROM facts_extended 
            WHERE created_at >= datetime('now', '-1 hour')
        ''')
        recent_facts = cursor.fetchone()[0]
        
        # Top predicates
        cursor.execute('''
            SELECT predicate, COUNT(*) as count 
            FROM facts_extended 
            GROUP BY predicate 
            ORDER BY count DESC 
            LIMIT 5
        ''')
        top_predicates = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_facts': total_facts,
            'multi_arg_facts': multi_arg_facts,
            'recent_facts': recent_facts,
            'top_predicates': top_predicates
        }
    except Exception as e:
        print(f"❌ Error getting DB stats: {e}")
        return None

def print_header():
    """Print header with current time"""
    print("=" * 80)
    print(f"🧠 HAK/GAL FACT GENERATOR WITH METRICS")
    print(f"⏰ Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)

def print_metrics(stats, generated_count, success_count, error_count, start_time):
    """Print current metrics"""
    elapsed = time.time() - start_time
    rate = generated_count / elapsed if elapsed > 0 else 0
    
    print(f"\n📊 LIVE METRICS:")
    print(f"   Generated: {generated_count} facts")
    print(f"   Success: {success_count} facts")
    print(f"   Errors: {error_count} facts")
    print(f"   Rate: {rate:.1f} facts/sec")
    print(f"   Elapsed: {elapsed:.1f}s")
    
    if stats:
        print(f"\n🗄️  DATABASE:")
        print(f"   Total Facts: {stats['total_facts']:,}")
        print(f"   Multi-Arg Facts: {stats['multi_arg_facts']:,}")
        print(f"   Recent (1h): {stats['recent_facts']:,}")
        
        if stats['top_predicates']:
            print(f"\n🏆 TOP PREDICATES:")
            for predicate, count in stats['top_predicates']:
                print(f"   {predicate}: {count}")

def print_fact_details(facts, predicate_stats, domain_stats):
    """Print detailed fact analysis"""
    print(f"\n🔍 FACT ANALYSIS:")
    
    # Argument count distribution
    arg_counts = Counter()
    for fact in facts:
        # Count arguments by counting commas + 1
        arg_count = fact.count(',') + 1
        arg_counts[arg_count] += 1
    
    print(f"   Argument Distribution:")
    for arg_count, count in sorted(arg_counts.items()):
        print(f"     {arg_count} args: {count} facts")
    
    # Predicate distribution
    if predicate_stats:
        print(f"   Predicate Distribution:")
        for predicate, count in predicate_stats.most_common(5):
            print(f"     {predicate}: {count}")
    
    # Domain distribution
    if domain_stats:
        print(f"   Domain Distribution:")
        for domain, count in domain_stats.most_common():
            print(f"     {domain}: {count}")

def main():
    parser = argparse.ArgumentParser(description='Generate facts with live metrics')
    parser.add_argument('--count', type=int, default=20, help='Number of facts to generate')
    parser.add_argument('--interval', type=float, default=1.0, help='Interval between generations (seconds)')
    parser.add_argument('--domains', type=str, help='Comma-separated domains (chemistry,physics,biology,etc.)')
    parser.add_argument('--verbose', action='store_true', help='Show individual facts')
    
    args = parser.parse_args()
    
    # Setup
    setup_environment()
    print_header()
    
    try:
        from infrastructure.engines.aethelred_extended_fixed import AethelredExtendedEngine
        
        # Initialize engine
        print("🚀 Initializing Extended Engine...")
        engine = AethelredExtendedEngine()
        print("✅ Engine initialized successfully")
        
        # Get initial stats
        initial_stats = get_db_stats()
        if initial_stats:
            print(f"\n📈 INITIAL DATABASE STATE:")
            print(f"   Total Facts: {initial_stats['total_facts']:,}")
            print(f"   Multi-Arg Facts: {initial_stats['multi_arg_facts']:,}")
        
        # Generation loop
        all_facts = []
        predicate_stats = Counter()
        domain_stats = Counter()
        success_count = 0
        error_count = 0
        start_time = time.time()
        
        print(f"\n🎯 GENERATING {args.count} FACTS...")
        print(f"   Interval: {args.interval}s")
        if args.domains:
            print(f"   Domains: {args.domains}")
        
        for i in range(args.count):
            try:
                # Generate facts
                facts = engine.generate_facts()
                all_facts.extend(facts)
                
                # Add to database
                batch_success = 0
                for fact in facts:
                    try:
                        result = engine.add_fact(fact)
                        if result:
                            success_count += 1
                            batch_success += 1
                            
                            # Extract predicate for stats
                            predicate = fact.split('(')[0]
                            predicate_stats[predicate] += 1
                            
                            if args.verbose:
                                print(f"   ✅ {fact}")
                        else:
                            error_count += 1
                            if args.verbose:
                                print(f"   ❌ Failed: {fact}")
                    except Exception as e:
                        error_count += 1
                        if args.verbose:
                            print(f"   ❌ Error: {fact} - {e}")
                
                # Show progress
                generated_count = len(all_facts)
                print(f"   Round {i+1}/{args.count}: Generated {len(facts)} facts, Added {batch_success} to DB")
                
                # Show metrics every 5 rounds or at the end
                if (i + 1) % 5 == 0 or i == args.count - 1:
                    current_stats = get_db_stats()
                    print_metrics(current_stats, generated_count, success_count, error_count, start_time)
                
                # Wait between generations
                if i < args.count - 1:
                    time.sleep(args.interval)
                    
            except Exception as e:
                print(f"❌ Error in round {i+1}: {e}")
                error_count += 1
                time.sleep(args.interval)
        
        # Final summary
        print("\n" + "=" * 80)
        print("🎉 GENERATION COMPLETE!")
        print("=" * 80)
        
        final_stats = get_db_stats()
        if final_stats:
            print(f"\n📊 FINAL RESULTS:")
            print(f"   Facts Generated: {len(all_facts)}")
            print(f"   Facts Added to DB: {success_count}")
            print(f"   Errors: {error_count}")
            print(f"   Success Rate: {(success_count/(success_count+error_count)*100):.1f}%")
            
            print(f"\n📈 DATABASE GROWTH:")
            if initial_stats:
                total_growth = final_stats['total_facts'] - initial_stats['total_facts']
                multi_growth = final_stats['multi_arg_facts'] - initial_stats['multi_arg_facts']
                print(f"   Total Facts: +{total_growth} (now {final_stats['total_facts']:,})")
                print(f"   Multi-Arg Facts: +{multi_growth} (now {final_stats['multi_arg_facts']:,})")
        
        # Detailed analysis
        print_fact_details(all_facts, predicate_stats, domain_stats)
        
        # Show recent facts
        print(f"\n🆕 RECENT FACTS ADDED:")
        recent_facts = all_facts[-10:] if len(all_facts) > 10 else all_facts
        for i, fact in enumerate(recent_facts, 1):
            print(f"   {i:2d}. {fact}")
        
        print(f"\n⏱️  Total Time: {time.time() - start_time:.1f}s")
        print(f"📈 Average Rate: {success_count/(time.time() - start_time):.1f} facts/sec")
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("Make sure you're in the correct directory and venv_hexa is activated")
    except Exception as e:
        print(f"❌ Unexpected Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
