#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
START MULTI-ARGUMENT FACT GENERATION
=====================================
Quick launcher for the extended fact generation system
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add paths
sys.path.insert(0, r"D:\MCP Mods\HAK_GAL_HEXAGONAL")

def start_extended_generation(duration_minutes=10, use_governor=True):
    """
    Start extended multi-argument fact generation
    
    Args:
        duration_minutes: How long to run
        use_governor: Whether to use Governor integration
    """
    print("="*60)
    print("MULTI-ARGUMENT FACT GENERATION SYSTEM")
    print("="*60)
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Duration: {duration_minutes} minutes")
    print(f"Governor: {'Enabled' if use_governor else 'Disabled'}")
    print("="*60)
    
    if use_governor:
        # Use Governor integration
        from src_hexagonal.adapters.governor_extended_adapter import GovernorExtendedAdapter
        
        adapter = GovernorExtendedAdapter()
        
        # Get recommendations
        recommendations = adapter.get_recommendations()
        print(f"\nStrategy: {recommendations['strategy']}")
        print("Current statistics:")
        for key, value in recommendations['statistics'].items():
            print(f"  {key}: {value}")
        
        # Start recommended engine
        engine_name = 'aethelred_extended'  # Force extended for multi-arg
        
        print(f"\nStarting {engine_name} engine...")
        process = adapter.start_engine(engine_name, duration_minutes, port=5001)
        
        if process:
            print(f"✓ Engine started (PID: {process.pid})")
            print(f"Running for {duration_minutes} minutes...")
            
            # Monitor progress
            start_time = time.time()
            try:
                while time.time() - start_time < duration_minutes * 60:
                    # Check if process is still running
                    if process.poll() is not None:
                        print("Engine finished early")
                        break
                    
                    # Progress update every 30 seconds
                    time.sleep(30)
                    elapsed = (time.time() - start_time) / 60
                    remaining = duration_minutes - elapsed
                    print(f"  Progress: {elapsed:.1f}/{duration_minutes} min ({remaining:.1f} min remaining)")
                    
            except KeyboardInterrupt:
                print("\nStopping engine...")
                adapter.stop_engine(engine_name)
                print("✓ Engine stopped by user")
                return
            
            # Stop engine
            adapter.stop_engine(engine_name)
            print("✓ Engine completed")
        else:
            print("✗ Failed to start engine")
            return
            
    else:
        # Direct execution without Governor
        from src_hexagonal.infrastructure.engines.aethelred_extended import AethelredExtendedEngine
        
        print("\nStarting Aethelred Extended Engine (direct mode)...")
        engine = AethelredExtendedEngine(port=5001)
        
        try:
            engine.run(duration_minutes=duration_minutes)
        except KeyboardInterrupt:
            print("\n✓ Stopped by user")
    
    # Show final statistics
    show_statistics()

def show_statistics():
    """Show database statistics after generation"""
    import sqlite3
    
    print("\n" + "="*60)
    print("GENERATION RESULTS")
    print("="*60)
    
    db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Get statistics
    cursor.execute("""
        SELECT 
            arg_count,
            COUNT(*) as count,
            AVG(confidence) as avg_confidence
        FROM facts_extended 
        GROUP BY arg_count 
        ORDER BY arg_count
    """)
    
    print("\nFacts by argument count:")
    total_multi = 0
    for row in cursor.fetchall():
        print(f"  {row[0]} args: {row[1]:,} facts (confidence: {row[2]:.2f})")
        if row[0] > 2:
            total_multi += row[1]
    
    # Domain distribution
    cursor.execute("""
        SELECT domain, COUNT(*) as count 
        FROM facts_extended 
        WHERE domain IS NOT NULL AND arg_count > 2
        GROUP BY domain 
        ORDER BY count DESC
        LIMIT 5
    """)
    
    print(f"\nTop domains (multi-arg facts):")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]:,} facts")
    
    # Recent examples
    cursor.execute("""
        SELECT statement 
        FROM facts_extended 
        WHERE arg_count >= 3 
        ORDER BY id DESC 
        LIMIT 3
    """)
    
    print(f"\nLatest multi-argument facts:")
    for row in cursor.fetchall():
        stmt = row[0]
        if len(stmt) > 80:
            stmt = stmt[:77] + "..."
        print(f"  - {stmt}")
    
    # Formulas
    cursor.execute("SELECT COUNT(*) FROM formulas")
    formula_count = cursor.fetchone()[0]
    print(f"\nTotal formulas: {formula_count}")
    
    # Summary
    cursor.execute("SELECT COUNT(*) FROM facts_extended")
    total_facts = cursor.fetchone()[0]
    
    multi_ratio = (total_multi / total_facts * 100) if total_facts > 0 else 0
    
    print(f"\n" + "="*60)
    print(f"SUMMARY:")
    print(f"  Total facts: {total_facts:,}")
    print(f"  Multi-arg facts (>2): {total_multi:,} ({multi_ratio:.1f}%)")
    print(f"  Formulas: {formula_count}")
    
    if multi_ratio < 5:
        print(f"\n💡 Recommendation: Continue running extended engine to increase multi-arg ratio")
    elif multi_ratio < 20:
        print(f"\n✓ Good progress! Multi-arg facts growing")
    else:
        print(f"\n🎉 Excellent! Strong multi-argument fact coverage")
    
    conn.close()

def test_quick():
    """Quick test of the system"""
    print("\n" + "="*60)
    print("QUICK SYSTEM TEST")
    print("="*60)
    
    from src_hexagonal.application.extended_fact_manager import ExtendedFactManager
    
    manager = ExtendedFactManager()
    
    # Generate sample facts
    print("\nGenerating sample facts...")
    domains = ['chemistry', 'physics', 'biology']
    total_added = 0
    
    for domain in domains:
        facts = manager.generate_domain_facts(domain, 3)
        for fact in facts:
            fact_id = manager.add_multi_arg_fact(
                fact['predicate'],
                fact['args'],
                domain=fact['domain'],
                confidence=0.95
            )
            if fact_id:
                total_added += 1
                print(f"  ✓ Added: {fact['predicate']}(...) [{domain}]")
    
    print(f"\n✓ Test complete: Added {total_added} multi-arg facts")
    return total_added > 0

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Multi-Argument Fact Generation System",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python start_multi_arg.py --test           # Run quick test
  python start_multi_arg.py --duration 5     # Run for 5 minutes
  python start_multi_arg.py --no-governor    # Run without Governor
  python start_multi_arg.py --stats          # Show statistics only
        """
    )
    
    parser.add_argument(
        '--duration', '-d',
        type=float,
        default=10,
        help='Duration in minutes (default: 10)'
    )
    
    parser.add_argument(
        '--no-governor',
        action='store_true',
        help='Run without Governor integration'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run quick test'
    )
    
    parser.add_argument(
        '--stats',
        action='store_true',
        help='Show statistics only'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    import logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if args.test:
        success = test_quick()
        sys.exit(0 if success else 1)
    
    if args.stats:
        show_statistics()
        sys.exit(0)
    
    # Run generation
    start_extended_generation(
        duration_minutes=args.duration,
        use_governor=not args.no_governor
    )


if __name__ == "__main__":
    main()
