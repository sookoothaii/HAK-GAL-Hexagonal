#!/usr/bin/env python3
"""
HAK_GAL Performance Claims Verification
======================================
Wissenschaftliche Validierung der Performance-Optimierungen
"""

import sqlite3
import time
import os
import sys
from pathlib import Path

# Add src_hexagonal to path
sys.path.insert(0, str(Path(__file__).parent / 'src_hexagonal'))

class PerformanceVerifier:
    def __init__(self, db_path="hexagonal_kb.db"):
        self.db_path = db_path
        self.results = {}
        
    def test_query_performance(self):
        """Test: Query-Performance < 2ms"""
        print("\n=== TEST 1: Query-Performance < 2ms ===")
        
        queries = [
            ("Predicate Search", "SELECT * FROM facts WHERE predicate = 'knows' LIMIT 10"),
            ("Source Search", "SELECT * FROM facts WHERE source = 'manual' LIMIT 10"),
            ("Confidence Filter", "SELECT * FROM facts WHERE confidence > 0.8 LIMIT 10"),
            ("Composite Query", "SELECT * FROM facts WHERE predicate = 'knows' AND confidence > 0.8 LIMIT 10"),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            for name, query in queries:
                # Warm up
                conn.execute(query).fetchall()
                
                # Measure
                start = time.perf_counter()
                conn.execute(query).fetchall()
                elapsed_ms = (time.perf_counter() - start) * 1000
                
                print(f"{name}: {elapsed_ms:.2f}ms {'✓' if elapsed_ms < 2 else '✗'}")
                self.results[f"query_{name}"] = elapsed_ms < 2
                
    def test_index_existence(self):
        """Test: 15 neue Indizes vorhanden"""
        print("\n=== TEST 2: Index-Existenz ===")
        
        expected_indexes = [
            'idx_facts_source',
            'idx_facts_confidence',
            'idx_facts_predicate_source',
            'idx_facts_predicate_confidence',
            'idx_facts_ext_source',
            'idx_facts_ext_created_at',
            'idx_facts_ext_predicate_source',
            'idx_facts_ext_type_domain',
            'idx_tool_perf_tool_name',
            'idx_tool_perf_timestamp',
            'idx_tool_perf_success',
            'idx_fact_relations_type',
            'idx_fact_relations_created_at',
            'idx_discovered_topics_type',
            'idx_discovered_topics_explored'
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
            existing_indexes = [row[0] for row in cursor.fetchall()]
            
            found_count = 0
            for idx in expected_indexes:
                if idx in existing_indexes:
                    found_count += 1
                    print(f"✓ {idx} found")
                else:
                    print(f"✗ {idx} NOT FOUND")
                    
            print(f"\nTotal: {found_count}/{len(expected_indexes)} indexes found")
            self.results['indexes_found'] = found_count == len(expected_indexes)
            
    def test_batch_query_performance(self):
        """Test: Batch Query 29% schneller"""
        print("\n=== TEST 3: Batch Query Performance ===")
        
        # Test N+1 queries
        predicates = ['knows', 'hasProperty', 'isLocatedIn']
        
        with sqlite3.connect(self.db_path) as conn:
            # N+1 approach
            start = time.perf_counter()
            for pred in predicates:
                conn.execute("SELECT * FROM facts WHERE predicate = ? LIMIT 10", (pred,)).fetchall()
            n1_time = time.perf_counter() - start
            
            # Batch approach
            placeholders = ','.join(['?' for _ in predicates])
            start = time.perf_counter()
            conn.execute(f"SELECT * FROM facts WHERE predicate IN ({placeholders}) LIMIT 30", predicates).fetchall()
            batch_time = time.perf_counter() - start
            
            improvement = ((n1_time - batch_time) / n1_time) * 100 if n1_time > 0 else 0
            
            print(f"N+1 queries: {n1_time*1000:.2f}ms")
            print(f"Batch query: {batch_time*1000:.2f}ms")
            print(f"Improvement: {improvement:.1f}% {'✓' if improvement > 20 else '✗'}")
            
            self.results['batch_improvement'] = improvement > 20
            
    def test_database_stats(self):
        """Test: Datenbank-Statistiken"""
        print("\n=== TEST 4: Datenbank-Statistiken ===")
        
        with sqlite3.connect(self.db_path) as conn:
            # Count facts
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts")
            fact_count = cursor.fetchone()[0]
            
            # Database size
            db_size_mb = os.path.getsize(self.db_path) / (1024 * 1024)
            
            # Count indexes
            cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE type='index'")
            index_count = cursor.fetchone()[0]
            
            print(f"Facts: {fact_count}")
            print(f"Database size: {db_size_mb:.2f} MB")
            print(f"Total indexes: {index_count}")
            
            # Verify claims
            self.results['facts_count'] = fact_count > 4000
            self.results['db_size'] = db_size_mb > 3.0
            
    def test_query_plan_optimization(self):
        """Test: EXPLAIN QUERY PLAN zeigt Index-Nutzung"""
        print("\n=== TEST 5: Query Plan Optimization ===")
        
        test_queries = [
            ("Source query", "SELECT * FROM facts WHERE source = 'manual'"),
            ("Predicate query", "SELECT * FROM facts WHERE predicate = 'knows'"),
            ("Composite query", "SELECT * FROM facts WHERE predicate = 'knows' AND source = 'manual'"),
        ]
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            uses_index = True
            for name, query in test_queries:
                cursor.execute(f"EXPLAIN QUERY PLAN {query}")
                plan = cursor.fetchall()
                plan_text = str(plan)
                
                if 'USING INDEX' in plan_text or 'SEARCH' in plan_text:
                    print(f"✓ {name}: Uses index")
                else:
                    print(f"✗ {name}: NO INDEX USED")
                    uses_index = False
                    
            self.results['query_plan_optimized'] = uses_index
            
    def test_cache_implementation(self):
        """Test: Cache-Implementierung vorhanden"""
        print("\n=== TEST 6: Cache-Implementierung ===")
        
        # Check if cache files exist
        cache_files = [
            'safe_memory_cache.py',
            'mcp_cache_integration.py'
        ]
        
        all_exist = True
        for file in cache_files:
            if Path(file).exists():
                print(f"✓ {file} exists")
            else:
                print(f"✗ {file} NOT FOUND")
                all_exist = False
                
        self.results['cache_implemented'] = all_exist
        
    def run_all_tests(self):
        """Führe alle Tests aus und erstelle Zusammenfassung"""
        print("=" * 60)
        print("HAK_GAL PERFORMANCE CLAIMS VERIFICATION")
        print("=" * 60)
        
        self.test_query_performance()
        self.test_index_existence()
        self.test_batch_query_performance()
        self.test_database_stats()
        self.test_query_plan_optimization()
        self.test_cache_implementation()
        
        # Summary
        print("\n" + "=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        passed = sum(1 for v in self.results.values() if v)
        total = len(self.results)
        
        for test, result in self.results.items():
            print(f"{test}: {'✓ PASSED' if result else '✗ FAILED'}")
            
        print(f"\nTotal: {passed}/{total} tests passed ({(passed/total)*100:.1f}%)")
        
        # Overall verdict
        if passed == total:
            print("\n✅ ALL CLAIMS VERIFIED - Der technische Bericht ist korrekt!")
        elif passed >= total * 0.8:
            print("\n⚠️  MOSTLY VERIFIED - Die meisten Claims sind korrekt")
        else:
            print("\n❌ VERIFICATION FAILED - Viele Claims konnten nicht bestätigt werden")
            
        return self.results

if __name__ == "__main__":
    verifier = PerformanceVerifier()
    results = verifier.run_all_tests()
