#!/usr/bin/env python3
"""
v6_autopilot with EKR Integration - CORRECTED VERSION
Works with actual EKRDatabase implementation
"""

import json
import random
import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

# Import the EKR components
from ekr_implementation import EKRParser, EKRDatabase, FactType
from ekr_fact_generator import EKRFactGenerator

class EKREnhancedAutopilot:
    """Enhanced autopilot with Extended Knowledge Representation"""
    
    def __init__(self, db_path: str = "hak_gal_ekr.db"):
        # Initialize database (schema is created automatically in __init__)
        self.db = EKRDatabase(db_path)
        self.parser = EKRParser()
        self.generator = EKRFactGenerator()
        
        # Statistics tracking
        self.stats = {
            'total_facts': 0,
            'binary_facts': 0,
            'nary_facts': 0,
            'typed_facts': 0,
            'formula_facts': 0,
            'temporal_facts': 0,
            'graph_facts': 0,
            'errors': 0,
            'start_time': datetime.now()
        }
        
        # Verify database is working
        self._check_database()
    
    def _check_database(self):
        """Verify database is properly initialized"""
        try:
            # Check facts_v2 table (the actual table name!)
            count = self.db.conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
            print(f"📊 Database initialized with {count} existing facts")
        except sqlite3.OperationalError as e:
            print(f"⚠️ Database error: {e}")
            print("🔧 Creating tables...")
            self.db._init_schema()
            print("✅ Database tables created")
    
    def generate_batch(self, complexity_distribution: Dict[str, float] = None) -> List[str]:
        """Generate a batch of facts with specified complexity distribution"""
        if complexity_distribution is None:
            # Default distribution favoring complex facts
            complexity_distribution = {
                'binary': 0.1,   # 10% simple facts
                'nary': 0.25,    # 25% n-ary relations
                'typed': 0.25,   # 25% typed arguments
                'formula': 0.2,  # 20% formulas
                'temporal': 0.2  # 20% temporal facts
            }
        
        batch_size = 10
        facts = []
        
        for fact_type, proportion in complexity_distribution.items():
            count = int(batch_size * proportion)
            
            if fact_type == 'binary':
                # Generate simple facts
                for _ in range(count):
                    entity = f"Entity{random.randint(1, 1000)}"
                    category = random.choice(['System', 'Process', 'Component', 'Algorithm'])
                    facts.append(f"IsA({entity}, {category}).")
                    
            elif fact_type == 'nary':
                for _ in range(count):
                    facts.append(self.generator.generate_nary_fact())
                    
            elif fact_type == 'typed':
                for _ in range(count):
                    facts.append(self.generator.generate_typed_fact())
                    
            elif fact_type == 'formula':
                for _ in range(count):
                    facts.append(self.generator.generate_formula_fact())
                    
            elif fact_type == 'temporal':
                for _ in range(count):
                    facts.append(self.generator.generate_temporal_fact())
        
        return facts
    
    def store_facts(self, facts: List[str]) -> Dict[str, int]:
        """Store facts in database and return statistics"""
        results = {
            'stored': 0,
            'duplicates': 0,
            'errors': 0
        }
        
        for fact in facts:
            try:
                # Check if already exists in facts_v2
                existing = self.db.conn.execute(
                    "SELECT id FROM facts_v2 WHERE statement = ?", 
                    (fact,)
                ).fetchone()
                
                if existing:
                    results['duplicates'] += 1
                else:
                    # Use the actual add_fact method signature
                    fact_id = self.db.add_fact(statement=fact, source="v6_autopilot")
                    
                    if fact_id:
                        results['stored'] += 1
                        # Parse to get type for stats
                        parsed = self.parser.parse(fact)
                        self.update_stats(parsed.fact_type.value)
                        
            except Exception as e:
                results['errors'] += 1
                self.stats['errors'] += 1
                # More detailed error reporting
                print(f"  ⚠️ Error: {str(e)[:60]}")
        
        return results
    
    def update_stats(self, fact_type: str):
        """Update statistics for fact type"""
        self.stats['total_facts'] += 1
        
        if fact_type == 'binary':
            self.stats['binary_facts'] += 1
        elif fact_type == 'nary':
            self.stats['nary_facts'] += 1
        elif fact_type == 'typed':
            self.stats['typed_facts'] += 1
        elif fact_type == 'formula':
            self.stats['formula_facts'] += 1
        elif fact_type == 'temporal':
            self.stats['temporal_facts'] += 1
        elif fact_type == 'graph':
            self.stats['graph_facts'] += 1
    
    def run_cycle(self):
        """Run one generation cycle"""
        print(f"\n🔄 Generation Cycle at {datetime.now().strftime('%H:%M:%S')}")
        
        # Generate facts
        facts = self.generate_batch()
        print(f"  📝 Generated {len(facts)} facts")
        
        # Store facts
        results = self.store_facts(facts)
        print(f"  ✅ Stored: {results['stored']}")
        if results['duplicates'] > 0:
            print(f"  ⚠️  Duplicates: {results['duplicates']}")
        
        if results['errors'] > 0:
            print(f"  ❌ Errors: {results['errors']}")
        
        # Show sample of successfully stored facts
        if results['stored'] > 0:
            print("  📋 Sample new facts:")
            shown = 0
            for fact in facts:
                if shown >= 3:
                    break
                # Verify it was stored
                exists = self.db.conn.execute(
                    "SELECT id FROM facts_v2 WHERE statement = ?", 
                    (fact,)
                ).fetchone()
                if exists:
                    if len(fact) > 60:
                        print(f"     • {fact[:60]}...")
                    else:
                        print(f"     • {fact}")
                    shown += 1
        
        return results
    
    def show_statistics(self):
        """Display current statistics"""
        runtime = (datetime.now() - self.stats['start_time']).total_seconds()
        
        print("\n" + "="*60)
        print("📊 EKR Autopilot Statistics")
        print("="*60)
        print(f"Runtime: {runtime:.0f} seconds")
        print(f"Total Facts Generated: {self.stats['total_facts']}")
        
        if self.stats['total_facts'] > 0:
            print("\nComplexity Distribution:")
            print(f"  • Binary (Simple):  {self.stats['binary_facts']} ({self.stats['binary_facts']/self.stats['total_facts']*100:.1f}%)")
            print(f"  • N-ary Relations:  {self.stats['nary_facts']} ({self.stats['nary_facts']/self.stats['total_facts']*100:.1f}%)")
            print(f"  • Typed Arguments:  {self.stats['typed_facts']} ({self.stats['typed_facts']/self.stats['total_facts']*100:.1f}%)")
            print(f"  • Formulas:         {self.stats['formula_facts']} ({self.stats['formula_facts']/self.stats['total_facts']*100:.1f}%)")
            print(f"  • Temporal:         {self.stats['temporal_facts']} ({self.stats['temporal_facts']/self.stats['total_facts']*100:.1f}%)")
            print(f"  • Graph:            {self.stats['graph_facts']} ({self.stats['graph_facts']/self.stats['total_facts']*100:.1f}%)")
        
        if self.stats['errors'] > 0:
            print(f"\n⚠️  Total Errors: {self.stats['errors']}")
        
        # Database statistics
        try:
            total_in_db = self.db.conn.execute("SELECT COUNT(*) FROM facts_v2").fetchone()[0]
            print(f"\n💾 Total Facts in Database: {total_in_db}")
            
            # Show complexity breakdown in DB
            print("\n📈 Database Breakdown by Type:")
            for fact_type in ['binary', 'nary', 'typed', 'formula', 'temporal', 'graph']:
                count = self.db.conn.execute(
                    "SELECT COUNT(*) FROM facts_v2 WHERE fact_type = ?", 
                    (fact_type,)
                ).fetchone()[0]
                if count > 0:
                    percentage = (count / total_in_db * 100) if total_in_db > 0 else 0
                    print(f"   - {fact_type:10s}: {count:4d} ({percentage:.1f}%)")
        except Exception as e:
            print(f"⚠️  Could not retrieve database statistics: {e}")
        
        # Performance metrics
        if runtime > 0 and self.stats['total_facts'] > 0:
            print(f"\n⚡ Performance:")
            print(f"   Facts/second: {self.stats['total_facts']/runtime:.2f}")
            total_attempted = self.stats['total_facts'] + self.stats['errors']
            if total_attempted > 0:
                print(f"   Success rate: {(self.stats['total_facts']/total_attempted)*100:.1f}%")
    
    def show_sample_facts(self, count: int = 5):
        """Show sample facts from database"""
        print(f"\n📚 Sample Facts from Database:")
        
        for fact_type in [FactType.NARY, FactType.TYPED, FactType.FORMULA]:
            facts = self.db.query_by_type(fact_type)
            if facts:
                print(f"\n{fact_type.value.title()} Facts:")
                for fact in facts[:count]:
                    statement = fact['statement']
                    if len(statement) > 70:
                        print(f"  • {statement[:70]}...")
                    else:
                        print(f"  • {statement}")
    
    def run(self, cycles: int = 10, delay: float = 5.0):
        """Run the autopilot for specified cycles"""
        print("🚀 Starting EKR Enhanced Autopilot")
        print(f"   Cycles: {cycles}")
        print(f"   Delay: {delay}s between cycles")
        print(f"   Database: {self.db.conn.execute('PRAGMA database_list').fetchone()[2]}")
        print("="*60)
        
        try:
            for i in range(cycles):
                print(f"\n[Cycle {i+1}/{cycles}]")
                self.run_cycle()
                
                if i < cycles - 1:
                    time.sleep(delay)
        
        except KeyboardInterrupt:
            print("\n\n⏹️  Autopilot stopped by user")
        
        finally:
            self.show_statistics()
            
            # Show some sample facts
            if self.stats['total_facts'] > 0:
                self.show_sample_facts(3)
            
            # Close database connection
            self.db.conn.close()
            print("\n✅ EKR Autopilot session complete!")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='EKR Enhanced Autopilot')
    parser.add_argument('--cycles', type=int, default=10, help='Number of cycles')
    parser.add_argument('--delay', type=float, default=5.0, help='Delay between cycles')
    parser.add_argument('--db', type=str, default='hak_gal_ekr.db', help='Database path')
    
    args = parser.parse_args()
    
    # Initialize and run
    autopilot = EKREnhancedAutopilot(args.db)
    autopilot.run(cycles=args.cycles, delay=args.delay)


if __name__ == "__main__":
    main()
