#!/usr/bin/env python
"""
Load Test for Governance System
Tests concurrent writes, performance under load, and stability
"""

import sys
import sqlite3
import time
import argparse
import threading
import random
import json
import statistics
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal")

# Performance tracking
class PerformanceMetrics:
    def __init__(self):
        self.latencies = []
        self.errors = []
        self.lock_errors = 0
        self.success_count = 0
        self.failed_count = 0
        self.start_time = None
        self.end_time = None
        self._lock = threading.Lock()
    
    def add_latency(self, latency_ms: float):
        with self._lock:
            self.latencies.append(latency_ms)
    
    def add_error(self, error: str):
        with self._lock:
            self.errors.append(error)
            if "database is locked" in str(error):
                self.lock_errors += 1
    
    def increment_success(self):
        with self._lock:
            self.success_count += 1
    
    def increment_failed(self):
        with self._lock:
            self.failed_count += 1
    
    def get_stats(self) -> Dict:
        with self._lock:
            if not self.latencies:
                return {
                    'total_requests': 0,
                    'success_count': self.success_count,
                    'failed_count': self.failed_count,
                    'error_count': len(self.errors),
                    'lock_errors': self.lock_errors
                }
            
            return {
                'total_requests': len(self.latencies) + self.failed_count,
                'success_count': self.success_count,
                'failed_count': self.failed_count,
                'error_count': len(self.errors),
                'lock_errors': self.lock_errors,
                'avg_latency_ms': statistics.mean(self.latencies),
                'median_latency_ms': statistics.median(self.latencies),
                'p95_latency_ms': statistics.quantiles(self.latencies, n=20)[18] if len(self.latencies) > 20 else max(self.latencies),
                'p99_latency_ms': statistics.quantiles(self.latencies, n=100)[98] if len(self.latencies) > 100 else max(self.latencies),
                'min_latency_ms': min(self.latencies),
                'max_latency_ms': max(self.latencies),
                'throughput_rps': len(self.latencies) / ((self.end_time - self.start_time) if self.end_time else 1)
            }

# Fact generation
class FactGenerator:
    """Generate realistic test facts"""
    
    PREDICATES = [
        'IsA', 'HasPart', 'DependsOn', 'Requires', 'Uses',
        'LocatedAt', 'Causes', 'Produces', 'Contains', 'Supports'
    ]
    
    ENTITIES = [
        'System', 'Component', 'Module', 'Service', 'Database',
        'Cache', 'Queue', 'Worker', 'Controller', 'Model',
        'View', 'Router', 'Middleware', 'Logger', 'Monitor',
        'Validator', 'Parser', 'Serializer', 'Deserializer', 'Transformer'
    ]
    
    TYPES = [
        'Infrastructure', 'Application', 'Domain', 'Presentation',
        'Security', 'Monitoring', 'Testing', 'Configuration', 
        'Documentation', 'Deployment'
    ]
    
    @classmethod
    def generate_batch(cls, count: int, worker_id: int = 0) -> List[str]:
        """Generate a batch of test facts"""
        facts = []
        for i in range(count):
            predicate = random.choice(cls.PREDICATES)
            entity1 = f"{random.choice(cls.ENTITIES)}{worker_id}_{i}"
            
            if predicate == 'IsA':
                entity2 = random.choice(cls.TYPES)
            else:
                entity2 = f"{random.choice(cls.ENTITIES)}{random.randint(1, 100)}"
            
            fact = f"{predicate}({entity1}, {entity2})"
            facts.append(fact)
        
        return facts

# Worker functions
def governance_worker(worker_id: int, facts_per_worker: int, metrics: PerformanceMetrics) -> Dict:
    """Worker that uses TransactionalGovernanceEngine"""
    try:
        from application.transactional_governance_engine import TransactionalGovernanceEngine
        
        engine = TransactionalGovernanceEngine()
        facts = FactGenerator.generate_batch(facts_per_worker, worker_id)
        
        # Split into smaller batches for realistic load
        batch_size = min(10, facts_per_worker)
        batches = [facts[i:i+batch_size] for i in range(0, len(facts), batch_size)]
        
        worker_stats = {
            'worker_id': worker_id,
            'facts_attempted': len(facts),
            'facts_added': 0,
            'batches_processed': 0,
            'errors': []
        }
        
        context = {
            'worker_id': worker_id,
            'test_type': 'load_test',
            'harm_prob': 0.0001,
            'sustain_index': 0.95,
            'externally_legal': True
        }
        
        for batch in batches:
            start = time.perf_counter()
            try:
                result = engine.governed_add_facts_atomic(batch, context)
                duration_ms = (time.perf_counter() - start) * 1000
                
                metrics.add_latency(duration_ms)
                metrics.increment_success()
                worker_stats['facts_added'] += result
                worker_stats['batches_processed'] += 1
                
            except Exception as e:
                duration_ms = (time.perf_counter() - start) * 1000
                metrics.add_error(str(e))
                metrics.increment_failed()
                worker_stats['errors'].append(str(e)[:100])
        
        return worker_stats
        
    except Exception as e:
        metrics.add_error(f"Worker {worker_id} failed: {e}")
        metrics.increment_failed()
        return {
            'worker_id': worker_id,
            'facts_attempted': facts_per_worker,
            'facts_added': 0,
            'error': str(e)
        }

def direct_db_worker(worker_id: int, facts_per_worker: int, metrics: PerformanceMetrics) -> Dict:
    """Worker that writes directly to database (baseline)"""
    try:
        conn = sqlite3.connect("hexagonal_kb.db", timeout=30.0)
        cursor = conn.cursor()
        
        facts = FactGenerator.generate_batch(facts_per_worker, worker_id)
        worker_stats = {
            'worker_id': worker_id,
            'facts_attempted': len(facts),
            'facts_added': 0,
            'errors': []
        }
        
        for fact in facts:
            start = time.perf_counter()
            try:
                # Parse fact
                predicate = fact[:fact.index('(')]
                args_str = fact[fact.index('(')+1:fact.rindex(')')]
                args = [a.strip() for a in args_str.split(',')]
                
                cursor.execute("""
                    INSERT OR IGNORE INTO facts_extended 
                    (statement, predicate, arg_count, arg1, arg2, fact_type, source, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, datetime('now'))
                """, (
                    fact,
                    predicate,
                    len(args),
                    args[0] if len(args) > 0 else None,
                    args[1] if len(args) > 1 else None,
                    'load_test',
                    f'worker_{worker_id}'
                ))
                
                duration_ms = (time.perf_counter() - start) * 1000
                metrics.add_latency(duration_ms)
                
                if cursor.rowcount > 0:
                    worker_stats['facts_added'] += 1
                    metrics.increment_success()
                    
            except sqlite3.OperationalError as e:
                if "database is locked" in str(e):
                    metrics.add_error(f"Lock error: {e}")
                    worker_stats['errors'].append("database locked")
                metrics.increment_failed()
            except Exception as e:
                metrics.add_error(str(e))
                metrics.increment_failed()
                worker_stats['errors'].append(str(e)[:50])
        
        conn.commit()
        conn.close()
        return worker_stats
        
    except Exception as e:
        metrics.add_error(f"Worker {worker_id} failed: {e}")
        return {
            'worker_id': worker_id,
            'facts_attempted': facts_per_worker,
            'facts_added': 0,
            'error': str(e)
        }

def run_load_test(total_facts: int, num_workers: int, use_governance: bool = True) -> Dict:
    """Run the load test"""
    print(f"\n{'='*60}")
    print(f"LOAD TEST: {total_facts} facts, {num_workers} workers")
    print(f"Mode: {'Governance Engine' if use_governance else 'Direct DB'}")
    print(f"{'='*60}\n")
    
    metrics = PerformanceMetrics()
    facts_per_worker = total_facts // num_workers
    
    print(f"Starting {num_workers} workers, {facts_per_worker} facts each...")
    
    metrics.start_time = time.time()
    
    # Run workers concurrently
    with ThreadPoolExecutor(max_workers=num_workers) as executor:
        if use_governance:
            futures = [
                executor.submit(governance_worker, i, facts_per_worker, metrics)
                for i in range(num_workers)
            ]
        else:
            futures = [
                executor.submit(direct_db_worker, i, facts_per_worker, metrics)
                for i in range(num_workers)
            ]
        
        # Collect results
        worker_results = []
        for future in as_completed(futures):
            try:
                result = future.result(timeout=60)
                worker_results.append(result)
                print(f"  Worker {result['worker_id']}: {result.get('facts_added', 0)}/{result['facts_attempted']} facts")
            except Exception as e:
                print(f"  Worker failed: {e}")
    
    metrics.end_time = time.time()
    
    # Calculate final statistics
    stats = metrics.get_stats()
    total_added = sum(r.get('facts_added', 0) for r in worker_results)
    
    print(f"\n{'='*60}")
    print("📊 LOAD TEST RESULTS")
    print(f"{'='*60}")
    
    print(f"\n📈 THROUGHPUT:")
    print(f"  Total facts attempted: {total_facts}")
    print(f"  Total facts added: {total_added}")
    print(f"  Success rate: {(total_added/total_facts*100):.1f}%")
    print(f"  Duration: {metrics.end_time - metrics.start_time:.2f}s")
    
    if 'throughput_rps' in stats:
        print(f"  Throughput: {stats['throughput_rps']:.1f} req/s")
    
    print(f"\n⏱️ LATENCY (ms):")
    if 'avg_latency_ms' in stats:
        print(f"  Average: {stats['avg_latency_ms']:.2f}")
        print(f"  Median: {stats['median_latency_ms']:.2f}")
        print(f"  P95: {stats['p95_latency_ms']:.2f}")
        print(f"  P99: {stats['p99_latency_ms']:.2f}")
        print(f"  Min: {stats['min_latency_ms']:.2f}")
        print(f"  Max: {stats['max_latency_ms']:.2f}")
    
    print(f"\n⚠️ ERRORS:")
    print(f"  Total errors: {stats['error_count']}")
    print(f"  Database locks: {stats['lock_errors']}")
    
    if metrics.errors and len(metrics.errors) > 0:
        print(f"\n  Sample errors:")
        for err in metrics.errors[:3]:
            print(f"    - {err[:100]}")
    
    # Performance rating
    print(f"\n🎯 PERFORMANCE RATING:")
    
    if stats['lock_errors'] == 0:
        print(f"  ✅ No database locks detected")
    else:
        print(f"  ❌ {stats['lock_errors']} database locks occurred")
    
    if 'avg_latency_ms' in stats:
        if stats['avg_latency_ms'] < 10:
            print(f"  ✅ Excellent latency (<10ms)")
        elif stats['avg_latency_ms'] < 50:
            print(f"  ✅ Good latency (<50ms)")
        elif stats['avg_latency_ms'] < 100:
            print(f"  ⚠️ Acceptable latency (<100ms)")
        else:
            print(f"  ❌ Poor latency (>{stats['avg_latency_ms']:.0f}ms)")
    
    success_rate = (total_added/total_facts*100) if total_facts > 0 else 0
    if success_rate >= 95:
        print(f"  ✅ Excellent success rate ({success_rate:.1f}%)")
    elif success_rate >= 80:
        print(f"  ⚠️ Good success rate ({success_rate:.1f}%)")
    else:
        print(f"  ❌ Poor success rate ({success_rate:.1f}%)")
    
    print(f"\n{'='*60}\n")
    
    return {
        'stats': stats,
        'worker_results': worker_results,
        'total_added': total_added,
        'success_rate': success_rate
    }

def main():
    parser = argparse.ArgumentParser(description='Load test the governance system')
    parser.add_argument('--facts', type=int, default=100, help='Total number of facts to insert')
    parser.add_argument('--workers', type=int, default=5, help='Number of concurrent workers')
    parser.add_argument('--mode', choices=['governance', 'direct', 'both'], default='direct',
                       help='Test mode: governance engine, direct DB, or both')
    
    args = parser.parse_args()
    
    print("\n🚀 HAK/GAL GOVERNANCE LOAD TEST")
    print("================================")
    
    # Check database
    db_path = Path("hexagonal_kb.db")
    if not db_path.exists():
        print("❌ Database not found. Please run the system first.")
        sys.exit(1)
    
    # Check WAL mode
    conn = sqlite3.connect(str(db_path))
    mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
    print(f"📁 Database: {db_path} (mode: {mode})")
    
    # Get initial count
    initial_count = conn.execute("SELECT COUNT(*) FROM facts_extended").fetchone()[0]
    print(f"📊 Initial facts: {initial_count}")
    conn.close()
    
    # Run tests based on mode
    if args.mode == 'both':
        # Run both tests for comparison
        print("\n--- DIRECT DATABASE TEST ---")
        direct_results = run_load_test(args.facts, args.workers, use_governance=False)
        
        print("\n--- GOVERNANCE ENGINE TEST ---")
        gov_results = run_load_test(args.facts, args.workers, use_governance=True)
        
        # Compare results
        print("\n📊 COMPARISON")
        print("="*60)
        print(f"{'Metric':<30} {'Direct DB':<15} {'Governance':<15}")
        print("-"*60)
        
        if 'avg_latency_ms' in direct_results['stats'] and 'avg_latency_ms' in gov_results['stats']:
            print(f"{'Avg Latency (ms)':<30} {direct_results['stats']['avg_latency_ms']:<15.2f} {gov_results['stats']['avg_latency_ms']:<15.2f}")
            print(f"{'P99 Latency (ms)':<30} {direct_results['stats']['p99_latency_ms']:<15.2f} {gov_results['stats']['p99_latency_ms']:<15.2f}")
        
        print(f"{'Success Rate (%)':<30} {direct_results['success_rate']:<15.1f} {gov_results['success_rate']:<15.1f}")
        print(f"{'Database Locks':<30} {direct_results['stats']['lock_errors']:<15} {gov_results['stats']['lock_errors']:<15}")
        print("="*60)
        
    else:
        use_governance = (args.mode == 'governance')
        results = run_load_test(args.facts, args.workers, use_governance=use_governance)
    
    # Final database count
    conn = sqlite3.connect(str(db_path))
    final_count = conn.execute("SELECT COUNT(*) FROM facts_extended").fetchone()[0]
    print(f"\n📊 Final facts in database: {final_count} (added: {final_count - initial_count})")
    conn.close()

if __name__ == "__main__":
    main()
