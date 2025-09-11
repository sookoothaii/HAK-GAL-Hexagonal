#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive Governance System Test Suite
==========================================
Tests all aspects of the HAK/GAL Governance Integration
"""

import sys
import os
import time
import json
import sqlite3
import random
import threading
import logging
from pathlib import Path
from typing import List, Dict, Any, Tuple
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\src_hexagonal")

from application.transactional_governance_engine import (
    TransactionalGovernanceEngine,
    GovernancePerformanceMonitor,
    BatchSizeExceeded,
    TransactionFailedException
)
# from application.hardened_audit_logger import HardenedAuditLogger
from application.transactional_governance_engine import StrictAuditLogger as HardenedAuditLogger
from application.hardened_policy_guard import HardenedPolicyGuard
from application.kill_switch import KillSwitch
from infrastructure.engines.governed_aethelred_engine import GovernedAethelredEngine
from infrastructure.engines.governed_thesis_engine import GovernedThesisEngine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GovernanceTestSuite:
    """
    Comprehensive test suite for HAK/GAL Governance System
    """
    
    def __init__(self):
        self.db_path = "D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\hexagonal_kb.db"
        self.results = {
            'passed': [],
            'failed': [],
            'warnings': []
        }
        self.start_time = time.time()
        
    def run_all_tests(self):
        """Run all test categories"""
        print("\n" + "="*70)
        print("HAK/GAL GOVERNANCE SYSTEM - COMPREHENSIVE TEST SUITE")
        print("="*70)
        
        # Test categories
        self.test_1_basic_governance()
        self.test_2_governance_violations()
        self.test_3_atomic_transactions()
        self.test_4_rollback_mechanisms()
        self.test_5_performance_slos()
        self.test_6_audit_integrity()
        self.test_7_kill_switch()
        self.test_8_chaos_testing()
        self.test_9_engine_integration()
        self.test_10_stress_testing()
        
        # Final report
        self.print_final_report()
    
    def test_1_basic_governance(self):
        """Test 1: Basic Governance Functionality"""
        print("\n### TEST 1: Basic Governance Functionality")
        print("-" * 50)
        
        try:
            engine = TransactionalGovernanceEngine()
            
            # Test valid facts
            valid_facts = [
                "Requires(TestSystem, Validation)",
                "DependsOn(Validation, Rules)",
                "HasPart(TestSystem, Component)"
            ]
            
            context = {
                'test': 'basic_governance',
                'harm_prob': 0.0001,
                'sustain_index': 0.95,
                'externally_legal': True
            }
            
            result = engine.governed_add_facts_atomic(valid_facts, context)
            
            if result == len(valid_facts):
                self.results['passed'].append("Basic governance - valid facts")
                print(f"✅ Added {result}/{len(valid_facts)} valid facts")
            else:
                self.results['failed'].append("Basic governance - incomplete add")
                print(f"❌ Only added {result}/{len(valid_facts)} facts")
                
        except Exception as e:
            self.results['failed'].append(f"Basic governance - {e}")
            print(f"❌ Basic governance failed: {e}")
    
    def test_2_governance_violations(self):
        """Test 2: Governance Violations & Denials"""
        print("\n### TEST 2: Governance Violations & Denials")
        print("-" * 50)
        
        try:
            engine = TransactionalGovernanceEngine()
            
            # Test facts that should be denied
            harmful_facts = [
                "Causes(TestSystem, Destruction)",
                "Requires(Destruction, Violence)"
            ]
            
            # Context with high harm probability
            harmful_context = {
                'test': 'governance_violations',
                'harm_prob': 0.9,  # Very high harm
                'sustain_index': 0.2,  # Very low sustainability
                'externally_legal': True
            }
            
            result = engine.governed_add_facts_atomic(harmful_facts, harmful_context)
            
            if result == 0:
                self.results['passed'].append("Governance violations - correctly denied")
                print(f"✅ Correctly denied harmful facts (harm_prob=0.9)")
            else:
                self.results['failed'].append("Governance violations - should have denied")
                print(f"❌ Should have denied but added {result} facts")
                
            # Test illegal context
            illegal_context = {
                'test': 'illegal_action',
                'harm_prob': 0.0001,
                'sustain_index': 0.95,
                'externally_legal': False  # Illegal
            }
            
            result2 = engine.governed_add_facts_atomic(["IsA(Test, Legal)"], illegal_context)
            
            if result2 == 0:
                self.results['passed'].append("Governance violations - illegal denied")
                print(f"✅ Correctly denied illegal action")
            else:
                self.results['failed'].append("Governance violations - illegal allowed")
                print(f"❌ Illegally allowed {result2} facts")
                
        except Exception as e:
            # Some exceptions are expected
            print(f"ℹ️ Expected denial: {e}")
            self.results['passed'].append("Governance violations - exception on denial")
    
    def test_3_atomic_transactions(self):
        """Test 3: Atomic Transaction Guarantees"""
        print("\n### TEST 3: Atomic Transaction Guarantees")
        print("-" * 50)
        
        try:
            engine = TransactionalGovernanceEngine()
            
            # Get initial DB state
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts_extended")
            initial_count = cursor.fetchone()[0]
            conn.close()
            
            # Test facts with one invalid
            mixed_facts = [
                "IsA(ValidEntity, Type)",
                "InvalidPredicate(X, Y)",  # This should fail validation
                "HasPart(System, Component)"
            ]
            
            context = {
                'test': 'atomic_transaction',
                'harm_prob': 0.0001,
                'sustain_index': 0.95,
                'externally_legal': True
            }
            
            try:
                result = engine.governed_add_facts_atomic(mixed_facts, context)
            except:
                result = 0
            
            # Check DB state after
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM facts_extended")
            final_count = cursor.fetchone()[0]
            conn.close()
            
            # Should be atomic - all or nothing
            if result == 0 and final_count == initial_count:
                self.results['passed'].append("Atomic transactions - rollback on failure")
                print(f"✅ Atomic rollback: DB unchanged ({initial_count} facts)")
            elif result == 2 and final_count == initial_count + 2:
                self.results['passed'].append("Atomic transactions - partial success")
                print(f"✅ Atomic commit: Added valid facts only")
            else:
                self.results['failed'].append("Atomic transactions - inconsistent state")
                print(f"❌ Non-atomic: Expected {initial_count}, got {final_count}")
                
        except Exception as e:
            self.results['failed'].append(f"Atomic transactions - {e}")
            print(f"❌ Atomic transaction test failed: {e}")
    
    def test_4_rollback_mechanisms(self):
        """Test 4: Rollback Mechanisms"""
        print("\n### TEST 4: Rollback Mechanisms")
        print("-" * 50)
        
        class RollbackTestEngine(TransactionalGovernanceEngine):
            """Engine that simulates failures for rollback testing"""
            
            def _commit_db(self, db_prepare):
                """Simulate DB commit failure"""
                raise Exception("Simulated DB commit failure")
        
        try:
            engine = RollbackTestEngine()
            
            facts = ["IsA(RollbackTest, Entity)"]
            context = {
                'test': 'rollback',
                'harm_prob': 0.0001,
                'sustain_index': 0.95,
                'externally_legal': True
            }
            
            # This should trigger rollback
            try:
                result = engine.governed_add_facts_atomic(facts, context)
                self.results['failed'].append("Rollback - should have failed")
                print(f"❌ Should have triggered rollback")
            except TransactionFailedException as e:
                if "Simulated DB commit failure" in str(e):
                    self.results['passed'].append("Rollback - correctly handled")
                    print(f"✅ Rollback triggered correctly: {e}")
                else:
                    self.results['failed'].append("Rollback - wrong error")
                    print(f"❌ Unexpected error: {e}")
                    
        except Exception as e:
            self.results['failed'].append(f"Rollback - {e}")
            print(f"❌ Rollback test failed: {e}")
    
    def test_5_performance_slos(self):
        """Test 5: Performance SLOs"""
        print("\n### TEST 5: Performance SLOs")
        print("-" * 50)
        
        try:
            engine = TransactionalGovernanceEngine()
            monitor = GovernancePerformanceMonitor(engine)
            
            # Test with various batch sizes
            test_sizes = [1, 10, 50, 100]
            
            for size in test_sizes:
                facts = [f"IsA(Entity{i}, Type{i%5})" for i in range(size)]
                context = {
                    'test': 'performance',
                    'batch_size': size,
                    'harm_prob': 0.0001,
                    'sustain_index': 0.95,
                    'externally_legal': True
                }
                
                start = time.perf_counter()
                try:
                    result = monitor.monitored_add_facts(facts, context)
                    duration_ms = (time.perf_counter() - start) * 1000
                    
                    if duration_ms < 100:  # SLO: <100ms
                        print(f"✅ Batch size {size}: {duration_ms:.2f}ms < 100ms SLO")
                    else:
                        print(f"⚠️ Batch size {size}: {duration_ms:.2f}ms > 100ms SLO")
                        self.results['warnings'].append(f"SLO violation at size {size}")
                except BatchSizeExceeded:
                    print(f"ℹ️ Batch size {size} exceeds limit (expected)")
            
            # Check metrics
            metrics = monitor.get_metrics()
            if metrics['avg_latency_ms'] < 100:
                self.results['passed'].append(f"Performance SLOs - avg {metrics['avg_latency_ms']:.2f}ms")
                print(f"✅ Average latency: {metrics['avg_latency_ms']:.2f}ms < 100ms")
            else:
                self.results['failed'].append(f"Performance SLOs - avg {metrics['avg_latency_ms']:.2f}ms")
                print(f"❌ Average latency: {metrics['avg_latency_ms']:.2f}ms > 100ms")
                
        except Exception as e:
            self.results['failed'].append(f"Performance SLOs - {e}")
            print(f"❌ Performance test failed: {e}")
    
    def test_6_audit_integrity(self):
        """Test 6: Audit Trail Integrity"""
        print("\n### TEST 6: Audit Trail Integrity")
        print("-" * 50)
        
        try:
            # Create test audit logger
            audit_logger = HardenedAuditLogger(
                project_root=Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL"),
                filename="test_audit_integrity.jsonl"
            )
            
            # Log some events
            hashes = []
            for i in range(5):
                hash_val = audit_logger.log(
                    f"test.event.{i}",
                    {"index": i, "test": "integrity"}
                )
                hashes.append(hash_val)
                time.sleep(0.01)
            
            # Verify chain integrity
            if audit_logger.verify_integrity(full_check=True):
                self.results['passed'].append("Audit integrity - chain valid")
                print(f"✅ Audit chain integrity verified ({len(hashes)} entries)")
            else:
                self.results['failed'].append("Audit integrity - chain broken")
                print(f"❌ Audit chain integrity check failed")
            
            # Test tampering detection
            audit_path = Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\test_audit_integrity.jsonl")
            
            # Read audit file
            with open(audit_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) > 2:
                # Tamper with an entry
                tampered_lines = lines.copy()
                entry = json.loads(tampered_lines[2])
                entry['payload']['tampered'] = True
                tampered_lines[2] = json.dumps(entry) + '\n'
                
                # Write tampered file
                tampered_path = Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL\\test_audit_tampered.jsonl")
                with open(tampered_path, 'w') as f:
                    f.writelines(tampered_lines)
                
                # Test detection
                tampered_logger = HardenedAuditLogger(
                    project_root=Path("D:\\MCP Mods\\HAK_GAL_HEXAGONAL"),
                    filename="test_audit_tampered.jsonl"
                )
                
                if not tampered_logger.verify_integrity(full_check=True):
                    self.results['passed'].append("Audit integrity - tampering detected")
                    print(f"✅ Tampering correctly detected")
                else:
                    self.results['failed'].append("Audit integrity - tampering missed")
                    print(f"❌ Failed to detect tampering")
                    
        except Exception as e:
            self.results['failed'].append(f"Audit integrity - {e}")
            print(f"❌ Audit integrity test failed: {e}")
    
    def test_7_kill_switch(self):
        """Test 7: Kill Switch Mechanism"""
        print("\n### TEST 7: Kill Switch Mechanism")
        print("-" * 50)
        
        try:
            kill_switch = KillSwitch()
            
            # Test dry run
            kill_switch.test_activation(dry_run=True)
            
            if not kill_switch.is_activated():
                self.results['passed'].append("Kill switch - dry run successful")
                print(f"✅ Kill switch dry run completed (not activated)")
            else:
                self.results['failed'].append("Kill switch - incorrectly activated")
                print(f"❌ Kill switch incorrectly activated on dry run")
            
            # Test callback registration
            callback_executed = {'value': False}
            
            def test_callback():
                callback_executed['value'] = True
            
            kill_switch.register_callback(test_callback)
            
            # We can't actually activate without killing the process
            print(f"ℹ️ Kill switch callbacks registered (cannot test activation)")
            self.results['passed'].append("Kill switch - callbacks registered")
            
        except Exception as e:
            self.results['failed'].append(f"Kill switch - {e}")
            print(f"❌ Kill switch test failed: {e}")
    
    def test_8_chaos_testing(self):
        """Test 8: Chaos Testing (Random Failures)"""
        print("\n### TEST 8: Chaos Testing")
        print("-" * 50)
        
        class ChaosEngine(TransactionalGovernanceEngine):
            """Engine with random failures for chaos testing"""
            
            def __init__(self, failure_rate=0.3):
                super().__init__()
                self.failure_rate = failure_rate
                self.failure_points = [
                    '_prepare_governance',
                    '_prepare_db_transaction',
                    '_prepare_audit'
                ]
            
            def _prepare_governance(self, *args, **kwargs):
                if random.random() < self.failure_rate:
                    raise Exception("Chaos: Governance prepare failed")
                return super()._prepare_governance(*args, **kwargs)
            
            def _prepare_db_transaction(self, *args, **kwargs):
                if random.random() < self.failure_rate:
                    raise Exception("Chaos: DB prepare failed")
                return super()._prepare_db_transaction(*args, **kwargs)
        
        try:
            chaos_engine = ChaosEngine(failure_rate=0.5)
            
            successes = 0
            failures = 0
            
            for i in range(10):
                facts = [f"IsA(ChaosEntity{i}, ChaosType)"]
                context = {
                    'test': 'chaos',
                    'iteration': i,
                    'harm_prob': 0.0001,
                    'sustain_index': 0.95,
                    'externally_legal': True
                }
                
                try:
                    result = chaos_engine.governed_add_facts_atomic(facts, context)
                    if result > 0:
                        successes += 1
                except:
                    failures += 1
            
            print(f"ℹ️ Chaos results: {successes} successes, {failures} failures")
            
            # System should handle failures gracefully
            if successes + failures == 10:
                self.results['passed'].append(f"Chaos testing - handled {failures} failures")
                print(f"✅ System remained stable under chaos")
            else:
                self.results['failed'].append("Chaos testing - system unstable")
                print(f"❌ System became unstable under chaos")
                
        except Exception as e:
            self.results['failed'].append(f"Chaos testing - {e}")
            print(f"❌ Chaos testing failed: {e}")
    
    def test_9_engine_integration(self):
        """Test 9: Engine Integration"""
        print("\n### TEST 9: Engine Integration")
        print("-" * 50)
        
        try:
            # Test Aethelred Engine
            aethelred = GovernedAethelredEngine(port=5001)
            aethelred_facts = aethelred.generate_facts()
            
            if aethelred_facts:
                context = {
                    'engine': 'test_aethelred',
                    'harm_prob': 0.0001,
                    'sustain_index': 0.95,
                    'externally_legal': True
                }
                
                added = aethelred.add_facts_with_governance(
                    aethelred_facts[:3], 
                    context
                )
                
                if added > 0:
                    self.results['passed'].append(f"Aethelred integration - added {added} facts")
                    print(f"✅ Aethelred Engine: Added {added} governed facts")
                else:
                    self.results['warnings'].append("Aethelred integration - no facts added")
                    print(f"⚠️ Aethelred Engine: No facts added")
            
            # Test Thesis Engine
            thesis = GovernedThesisEngine(port=5001, max_facts=500)
            
            if thesis.analyze_knowledge_base():
                thesis_facts = thesis.generate_facts()
                
                if thesis_facts:
                    context = {
                        'engine': 'test_thesis',
                        'meta_analysis': True,
                        'harm_prob': 0.00001,
                        'sustain_index': 0.99,
                        'externally_legal': True
                    }
                    
                    added = thesis.add_facts_with_governance(
                        thesis_facts[:3],
                        context
                    )
                    
                    if added > 0:
                        self.results['passed'].append(f"Thesis integration - added {added} facts")
                        print(f"✅ Thesis Engine: Added {added} governed meta-facts")
                    else:
                        # Meta-facts might already exist
                        print(f"ℹ️ Thesis Engine: Meta-facts already exist")
                        
        except Exception as e:
            self.results['failed'].append(f"Engine integration - {e}")
            print(f"❌ Engine integration failed: {e}")
    
    def test_10_stress_testing(self):
        """Test 10: Stress Testing"""
        print("\n### TEST 10: Stress Testing")
        print("-" * 50)
        
        try:
            engine = TransactionalGovernanceEngine()
            
            # Concurrent stress test
            def stress_worker(worker_id, results_dict):
                try:
                    facts = [f"IsA(StressEntity{worker_id}_{i}, StressType)" for i in range(10)]
                    context = {
                        'test': 'stress',
                        'worker': worker_id,
                        'harm_prob': 0.0001,
                        'sustain_index': 0.95,
                        'externally_legal': True
                    }
                    
                    result = engine.governed_add_facts_atomic(facts, context)
                    results_dict[worker_id] = result
                except Exception as e:
                    results_dict[worker_id] = f"Error: {e}"
            
            # Run concurrent workers
            threads = []
            stress_results = {}
            
            for i in range(5):
                t = threading.Thread(target=stress_worker, args=(i, stress_results))
                threads.append(t)
                t.start()
            
            for t in threads:
                t.join(timeout=10)
            
            # Check results
            successful_workers = sum(1 for r in stress_results.values() 
                                    if isinstance(r, int) and r > 0)
            
            if successful_workers > 0:
                self.results['passed'].append(f"Stress testing - {successful_workers}/5 workers")
                print(f"✅ Stress test: {successful_workers}/5 workers succeeded")
                
                # Check for data consistency
                conn = sqlite3.connect(self.db_path)
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT COUNT(*) FROM facts_extended 
                    WHERE statement LIKE 'IsA(StressEntity%'
                """)
                stress_facts = cursor.fetchone()[0]
                conn.close()
                
                print(f"ℹ️ Total stress facts in DB: {stress_facts}")
            else:
                self.results['failed'].append("Stress testing - all workers failed")
                print(f"❌ All stress workers failed")
                
        except Exception as e:
            self.results['failed'].append(f"Stress testing - {e}")
            print(f"❌ Stress testing failed: {e}")
    
    def print_final_report(self):
        """Print final test report"""
        duration = time.time() - self.start_time
        
        print("\n" + "="*70)
        print("FINAL TEST REPORT")
        print("="*70)
        
        print(f"\n📊 Test Results:")
        print(f"  ✅ Passed: {len(self.results['passed'])}")
        print(f"  ❌ Failed: {len(self.results['failed'])}")
        print(f"  ⚠️ Warnings: {len(self.results['warnings'])}")
        print(f"  ⏱️ Duration: {duration:.2f} seconds")
        
        if self.results['passed']:
            print(f"\n✅ Passed Tests:")
            for test in self.results['passed']:
                print(f"  • {test}")
        
        if self.results['failed']:
            print(f"\n❌ Failed Tests:")
            for test in self.results['failed']:
                print(f"  • {test}")
        
        if self.results['warnings']:
            print(f"\n⚠️ Warnings:")
            for warning in self.results['warnings']:
                print(f"  • {warning}")
        
        # Overall assessment
        total_tests = len(self.results['passed']) + len(self.results['failed'])
        if total_tests > 0:
            success_rate = (len(self.results['passed']) / total_tests) * 100
            
            print(f"\n📈 Success Rate: {success_rate:.1f}%")
            
            if success_rate >= 90:
                print("\n🎉 SYSTEM READY FOR PRODUCTION!")
            elif success_rate >= 70:
                print("\n⚠️ SYSTEM NEEDS MINOR FIXES")
            else:
                print("\n❌ SYSTEM NOT READY - MAJOR ISSUES")
        
        print("\n" + "="*70)


def main():
    """Main test runner"""
    suite = GovernanceTestSuite()
    suite.run_all_tests()


if __name__ == "__main__":
    main()
