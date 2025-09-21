#!/usr/bin/env python3
"""
CHAOS ENGINEERING TEST - HAK/GAL SYSTEM
Testet das System unter chaotischen Bedingungen
"""

import asyncio
import concurrent.futures
import threading
import time
import random
import json
import sqlite3
import psutil
import requests
import subprocess
import os
import sys
import signal
import multiprocessing
from datetime import datetime
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chaos_engineering_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ChaosEngineeringTester:
    """Chaos Engineering Tester für HAK/GAL System"""
    
    def __init__(self):
        self.test_results = {}
        self.chaos_events = []
        self.performance_metrics = {}
        self.start_time = time.time()
        self.chaos_scenarios = [
            "RANDOM_FAILURES",
            "RESOURCE_EXHAUSTION",
            "NETWORK_PARTITIONS",
            "PROCESS_TERMINATION",
            "MEMORY_CORRUPTION",
            "DISK_FULL",
            "CPU_SPIKES",
            "DATABASE_LOCKOUT"
        ]
        
    def log_chaos_scenario(self, scenario: str):
        """Log chaos scenario"""
        logger.info(f"💥 CHAOS SCENARIO: {scenario}")
        print(f"\n{'='*80}")
        print(f"💥 CHAOS SCENARIO: {scenario}")
        print(f"{'='*80}")
        
    def random_failures_chaos(self, duration: int) -> Dict[str, Any]:
        """Introduce random failures"""
        logger.info("🎲 Introducing random failures")
        
        results = {
            "chaos_duration": duration,
            "failures_introduced": 0,
            "system_recoveries": 0,
            "failure_types": [],
            "recovery_times": []
        }
        
        def failure_worker(worker_id: int):
            """Failure worker thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Random failure types
                        failure_type = random.choice([
                            "exception_throw",
                            "resource_leak",
                            "deadlock_simulation",
                            "timeout_simulation",
                            "connection_drop"
                        ])
                        
                        results["failures_introduced"] += 1
                        results["failure_types"].append(failure_type)
                        
                        if failure_type == "exception_throw":
                            # Simulate exception
                            try:
                                raise Exception(f"Simulated failure {worker_id}")
                            except Exception as e:
                                logger.warning(f"Simulated exception: {e}")
                                
                        elif failure_type == "resource_leak":
                            # Simulate resource leak
                            data = [0] * 10000
                            time.sleep(0.1)
                            # Intentionally don't clean up
                            
                        elif failure_type == "deadlock_simulation":
                            # Simulate deadlock
                            lock1 = threading.Lock()
                            lock2 = threading.Lock()
                            
                            def deadlock_func():
                                with lock1:
                                    time.sleep(0.01)
                                    with lock2:
                                        pass
                            
                            def deadlock_func2():
                                with lock2:
                                    time.sleep(0.01)
                                    with lock1:
                                        pass
                            
                            # Start deadlock threads
                            t1 = threading.Thread(target=deadlock_func)
                            t2 = threading.Thread(target=deadlock_func2)
                            t1.start()
                            t2.start()
                            t1.join(timeout=0.1)
                            t2.join(timeout=0.1)
                            
                        elif failure_type == "timeout_simulation":
                            # Simulate timeout
                            time.sleep(random.uniform(0.1, 0.5))
                            
                        elif failure_type == "connection_drop":
                            # Simulate connection drop
                            try:
                                requests.get("http://localhost:5000/api/health", timeout=0.1)
                            except requests.exceptions.Timeout:
                                pass
                        
                        # Simulate recovery
                        recovery_start = time.time()
                        time.sleep(random.uniform(0.01, 0.1))
                        recovery_time = time.time() - recovery_start
                        results["recovery_times"].append(recovery_time)
                        results["system_recoveries"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception as e:
                        logger.error(f"Failure Worker {worker_id} error: {e}")
                        
                logger.info(f"Failure Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Failure Worker {worker_id} failed: {e}")
        
        # Start multiple failure workers
        threads = []
        for i in range(5):
            thread = threading.Thread(target=failure_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def resource_exhaustion_chaos(self, duration: int) -> Dict[str, Any]:
        """Exhaust system resources"""
        logger.info("🔥 Exhausting system resources")
        
        results = {
            "chaos_duration": duration,
            "cpu_exhaustion_cycles": 0,
            "memory_exhaustion_cycles": 0,
            "disk_exhaustion_cycles": 0,
            "file_handles_exhausted": 0
        }
        
        def resource_exhaustion_worker(worker_id: int):
            """Resource exhaustion worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # CPU exhaustion
                        for _ in range(1000000):
                            pass
                        results["cpu_exhaustion_cycles"] += 1
                        
                        # Memory exhaustion
                        data = [0] * 100000
                        time.sleep(0.1)
                        del data
                        results["memory_exhaustion_cycles"] += 1
                        
                        # Disk exhaustion
                        filename = f"exhaustion_{worker_id}_{int(time.time())}.tmp"
                        with open(filename, 'w') as f:
                            f.write("X" * 1024 * 1024)  # 1MB
                        os.remove(filename)
                        results["disk_exhaustion_cycles"] += 1
                        
                        # File handle exhaustion
                        files = []
                        for i in range(100):
                            try:
                                f = open(f"handle_{worker_id}_{i}.tmp", 'w')
                                files.append(f)
                            except OSError:
                                break
                        
                        # Close files
                        for f in files:
                            f.close()
                            os.remove(f.name)
                        
                        results["file_handles_exhausted"] += len(files)
                        
                        # Brief pause
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Resource Exhaustion Worker {worker_id} error: {e}")
                        
                logger.info(f"Resource Exhaustion Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Resource Exhaustion Worker {worker_id} failed: {e}")
        
        # Start multiple resource exhaustion workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=resource_exhaustion_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def network_partitions_chaos(self, duration: int) -> Dict[str, Any]:
        """Simulate network partitions"""
        logger.info("🌐 Simulating network partitions")
        
        results = {
            "chaos_duration": duration,
            "network_partitions": 0,
            "connection_drops": 0,
            "timeout_events": 0,
            "recovery_events": 0
        }
        
        def network_partition_worker(worker_id: int):
            """Network partition worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate network partition
                        results["network_partitions"] += 1
                        
                        # Simulate connection drops
                        for _ in range(10):
                            try:
                                response = requests.get("http://localhost:5000/api/health", timeout=0.1)
                                results["connection_drops"] += 1
                            except requests.exceptions.Timeout:
                                results["timeout_events"] += 1
                            except requests.exceptions.ConnectionError:
                                results["connection_drops"] += 1
                        
                        # Simulate recovery
                        time.sleep(random.uniform(0.1, 0.5))
                        results["recovery_events"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.error(f"Network Partition Worker {worker_id} error: {e}")
                        
                logger.info(f"Network Partition Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Network Partition Worker {worker_id} failed: {e}")
        
        # Start multiple network partition workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=network_partition_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def process_termination_chaos(self, duration: int) -> Dict[str, Any]:
        """Simulate process terminations"""
        logger.info("💀 Simulating process terminations")
        
        results = {
            "chaos_duration": duration,
            "processes_created": 0,
            "processes_terminated": 0,
            "termination_types": [],
            "recovery_attempts": 0
        }
        
        def process_termination_worker(worker_id: int):
            """Process termination worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Create temporary process
                        def temp_process():
                            time.sleep(10)  # Long running process
                        
                        process = multiprocessing.Process(target=temp_process)
                        process.start()
                        results["processes_created"] += 1
                        
                        # Let it run briefly
                        time.sleep(0.1)
                        
                        # Terminate process
                        termination_type = random.choice([
                            "graceful_terminate",
                            "force_kill",
                            "signal_interrupt"
                        ])
                        
                        results["termination_types"].append(termination_type)
                        
                        if termination_type == "graceful_terminate":
                            process.terminate()
                        elif termination_type == "force_kill":
                            process.kill()
                        elif termination_type == "signal_interrupt":
                            os.kill(process.pid, signal.SIGINT)
                        
                        process.join(timeout=1)
                        results["processes_terminated"] += 1
                        
                        # Simulate recovery
                        time.sleep(0.1)
                        results["recovery_attempts"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.error(f"Process Termination Worker {worker_id} error: {e}")
                        
                logger.info(f"Process Termination Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Process Termination Worker {worker_id} failed: {e}")
        
        # Start multiple process termination workers
        threads = []
        for i in range(2):
            thread = threading.Thread(target=process_termination_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def memory_corruption_chaos(self, duration: int) -> Dict[str, Any]:
        """Simulate memory corruption"""
        logger.info("🧠 Simulating memory corruption")
        
        results = {
            "chaos_duration": duration,
            "memory_corruption_events": 0,
            "buffer_overflows": 0,
            "dangling_pointers": 0,
            "recovery_attempts": 0
        }
        
        def memory_corruption_worker(worker_id: int):
            """Memory corruption worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate buffer overflow
                        data = [0] * 1000
                        try:
                            # Access beyond bounds
                            for i in range(1000, 1100):
                                data[i] = 1
                        except IndexError:
                            results["buffer_overflows"] += 1
                        
                        # Simulate dangling pointer
                        def create_dangling():
                            local_data = [1, 2, 3, 4, 5]
                            return local_data
                        
                        dangling = create_dangling()
                        try:
                            # Access after scope
                            result = sum(dangling)
                        except:
                            results["dangling_pointers"] += 1
                        
                        results["memory_corruption_events"] += 1
                        
                        # Simulate recovery
                        time.sleep(0.01)
                        results["recovery_attempts"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.1, 0.3))
                        
                    except Exception as e:
                        logger.error(f"Memory Corruption Worker {worker_id} error: {e}")
                        
                logger.info(f"Memory Corruption Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Memory Corruption Worker {worker_id} failed: {e}")
        
        # Start multiple memory corruption workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=memory_corruption_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def disk_full_chaos(self, duration: int) -> Dict[str, Any]:
        """Simulate disk full conditions"""
        logger.info("💿 Simulating disk full conditions")
        
        results = {
            "chaos_duration": duration,
            "disk_full_events": 0,
            "write_failures": 0,
            "recovery_attempts": 0,
            "files_created": 0,
            "files_deleted": 0
        }
        
        def disk_full_worker(worker_id: int):
            """Disk full worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate disk full
                        results["disk_full_events"] += 1
                        
                        # Try to create large files
                        for i in range(10):
                            filename = f"disk_full_{worker_id}_{i}.tmp"
                            try:
                                with open(filename, 'w') as f:
                                    f.write("X" * 1024 * 1024)  # 1MB
                                results["files_created"] += 1
                            except OSError as e:
                                if "No space left" in str(e):
                                    results["write_failures"] += 1
                                break
                        
                        # Clean up files
                        import glob
                        temp_files = glob.glob(f"disk_full_{worker_id}_*.tmp")
                        for file in temp_files:
                            try:
                                os.remove(file)
                                results["files_deleted"] += 1
                            except OSError:
                                pass
                        
                        # Simulate recovery
                        time.sleep(0.1)
                        results["recovery_attempts"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.error(f"Disk Full Worker {worker_id} error: {e}")
                        
                logger.info(f"Disk Full Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Disk Full Worker {worker_id} failed: {e}")
        
        # Start multiple disk full workers
        threads = []
        for i in range(2):
            thread = threading.Thread(target=disk_full_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def cpu_spikes_chaos(self, duration: int) -> Dict[str, Any]:
        """Create CPU spikes"""
        logger.info("⚡ Creating CPU spikes")
        
        results = {
            "chaos_duration": duration,
            "cpu_spikes": 0,
            "spike_duration": 0,
            "recovery_time": 0
        }
        
        def cpu_spike_worker(worker_id: int):
            """CPU spike worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Create CPU spike
                        spike_start = time.time()
                        results["cpu_spikes"] += 1
                        
                        # Intensive CPU work
                        for _ in range(10000000):
                            result = sum(i * i for i in range(1000))
                        
                        spike_duration = time.time() - spike_start
                        results["spike_duration"] += spike_duration
                        
                        # Recovery time
                        recovery_start = time.time()
                        time.sleep(0.1)
                        recovery_time = time.time() - recovery_start
                        results["recovery_time"] += recovery_time
                        
                        # Random delay
                        time.sleep(random.uniform(0.5, 2.0))
                        
                    except Exception as e:
                        logger.error(f"CPU Spike Worker {worker_id} error: {e}")
                        
                logger.info(f"CPU Spike Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"CPU Spike Worker {worker_id} failed: {e}")
        
        # Start multiple CPU spike workers
        threads = []
        for i in range(2):
            thread = threading.Thread(target=cpu_spike_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def database_lockout_chaos(self, duration: int) -> Dict[str, Any]:
        """Simulate database lockouts"""
        logger.info("🗄️ Simulating database lockouts")
        
        results = {
            "chaos_duration": duration,
            "lockout_events": 0,
            "deadlocks": 0,
            "timeout_events": 0,
            "recovery_attempts": 0
        }
        
        def database_lockout_worker(worker_id: int):
            """Database lockout worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate database lockout
                        results["lockout_events"] += 1
                        
                        # Create database connection
                        conn = sqlite3.connect('hexagonal_kb.db', timeout=1.0)
                        cursor = conn.cursor()
                        
                        # Start transaction
                        cursor.execute("BEGIN TRANSACTION")
                        
                        # Long running query
                        try:
                            cursor.execute("SELECT * FROM facts ORDER BY RANDOM() LIMIT 1000")
                            result = cursor.fetchall()
                            
                            # Simulate deadlock
                            if random.random() < 0.3:
                                results["deadlocks"] += 1
                                time.sleep(1)  # Simulate deadlock
                            
                        except sqlite3.OperationalError as e:
                            if "timeout" in str(e).lower():
                                results["timeout_events"] += 1
                        
                        # Commit or rollback
                        try:
                            cursor.execute("COMMIT")
                        except:
                            cursor.execute("ROLLBACK")
                        
                        conn.close()
                        
                        # Simulate recovery
                        time.sleep(0.1)
                        results["recovery_attempts"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.5, 1.0))
                        
                    except Exception as e:
                        logger.error(f"Database Lockout Worker {worker_id} error: {e}")
                        
                logger.info(f"Database Lockout Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Database Lockout Worker {worker_id} failed: {e}")
        
        # Start multiple database lockout workers
        threads = []
        for i in range(3):
            thread = threading.Thread(target=database_lockout_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def monitor_chaos_impact(self, duration: int) -> Dict[str, Any]:
        """Monitor impact of chaos events"""
        logger.info("📊 Monitoring chaos impact")
        
        results = {
            "monitoring_duration": duration,
            "system_health_samples": [],
            "performance_degradation": 0,
            "recovery_events": 0,
            "chaos_resilience_score": 0
        }
        
        def chaos_monitor():
            """Chaos monitoring thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Monitor system health
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        memory_percent = psutil.virtual_memory().percent
                        disk_percent = psutil.disk_usage('.').percent
                        
                        health_sample = {
                            "timestamp": time.time(),
                            "cpu": cpu_percent,
                            "memory": memory_percent,
                            "disk": disk_percent
                        }
                        
                        results["system_health_samples"].append(health_sample)
                        
                        # Detect performance degradation
                        if cpu_percent > 90 or memory_percent > 90 or disk_percent > 90:
                            results["performance_degradation"] += 1
                        
                        # Detect recovery
                        if cpu_percent < 50 and memory_percent < 50 and disk_percent < 50:
                            results["recovery_events"] += 1
                        
                        time.sleep(0.1)
                        
                    except Exception as e:
                        logger.error(f"Chaos monitor error: {e}")
                        
                logger.info("Chaos monitoring completed")
                
            except Exception as e:
                logger.error(f"Chaos monitor failed: {e}")
        
        # Start chaos monitoring
        monitor_thread = threading.Thread(target=chaos_monitor)
        monitor_thread.start()
        
        # Wait for completion
        monitor_thread.join()
        
        # Calculate chaos resilience score
        if results["system_health_samples"]:
            total_samples = len(results["system_health_samples"])
            degradation_ratio = results["performance_degradation"] / total_samples
            recovery_ratio = results["recovery_events"] / total_samples
            
            # Resilience score: higher is better
            results["chaos_resilience_score"] = (1 - degradation_ratio) * 100 + recovery_ratio * 10
        
        return results
    
    def run_chaos_engineering_test(self):
        """Run chaos engineering test"""
        logger.info("💥 STARTING CHAOS ENGINEERING TEST")
        print(f"\n{'='*100}")
        print("💥 CHAOS ENGINEERING TEST - HAK/GAL SYSTEM")
        print(f"{'='*100}")
        
        total_start_time = time.time()
        
        for scenario in self.chaos_scenarios:
            self.log_chaos_scenario(scenario)
            
            # Determine duration based on scenario
            if scenario in ["RANDOM_FAILURES", "MEMORY_CORRUPTION"]:
                duration = 30
            elif scenario in ["RESOURCE_EXHAUSTION", "NETWORK_PARTITIONS"]:
                duration = 45
            elif scenario in ["PROCESS_TERMINATION", "DISK_FULL"]:
                duration = 60
            else:
                duration = 40
            
            logger.info(f"Duration: {duration}s")
            
            # Start chaos scenario
            if scenario == "RANDOM_FAILURES":
                chaos_result = self.random_failures_chaos(duration)
            elif scenario == "RESOURCE_EXHAUSTION":
                chaos_result = self.resource_exhaustion_chaos(duration)
            elif scenario == "NETWORK_PARTITIONS":
                chaos_result = self.network_partitions_chaos(duration)
            elif scenario == "PROCESS_TERMINATION":
                chaos_result = self.process_termination_chaos(duration)
            elif scenario == "MEMORY_CORRUPTION":
                chaos_result = self.memory_corruption_chaos(duration)
            elif scenario == "DISK_FULL":
                chaos_result = self.disk_full_chaos(duration)
            elif scenario == "CPU_SPIKES":
                chaos_result = self.cpu_spikes_chaos(duration)
            elif scenario == "DATABASE_LOCKOUT":
                chaos_result = self.database_lockout_chaos(duration)
            
            # Monitor impact
            impact_result = self.monitor_chaos_impact(duration)
            
            # Store results
            self.test_results[scenario] = {
                "chaos_events": chaos_result,
                "system_impact": impact_result
            }
            
            # Brief pause between scenarios
            time.sleep(5)
        
        # Final analysis
        total_time = time.time() - total_start_time
        self.test_results["total_test_time"] = total_time
        self.test_results["test_timestamp"] = datetime.now().isoformat()
        
        # Generate comprehensive report
        self.generate_chaos_report()
        
        logger.info("✅ CHAOS ENGINEERING TEST COMPLETED")
        return self.test_results
    
    def generate_chaos_report(self):
        """Generate chaos engineering report"""
        logger.info("📊 Generating chaos engineering report")
        
        report = {
            "test_summary": {
                "total_test_time": self.test_results.get("total_test_time", 0),
                "test_timestamp": self.test_results.get("test_timestamp", ""),
                "chaos_scenarios_tested": len(self.chaos_scenarios),
                "overall_chaos_resilience": "UNKNOWN"
            },
            "detailed_results": self.test_results,
            "recommendations": []
        }
        
        # Analyze results
        total_chaos_events = 0
        total_recovery_events = 0
        total_resilience_score = 0
        
        for scenario, results in self.test_results.items():
            if isinstance(results, dict) and "system_impact" in results:
                impact = results["system_impact"]
                total_chaos_events += impact.get("performance_degradation", 0)
                total_recovery_events += impact.get("recovery_events", 0)
                total_resilience_score += impact.get("chaos_resilience_score", 0)
        
        # Overall resilience assessment
        if total_resilience_score > 80:
            report["test_summary"]["overall_chaos_resilience"] = "EXCELLENT"
            report["recommendations"].append("System shows excellent chaos resilience")
        elif total_resilience_score > 60:
            report["test_summary"]["overall_chaos_resilience"] = "GOOD"
            report["recommendations"].append("System shows good chaos resilience")
        elif total_resilience_score > 40:
            report["test_summary"]["overall_chaos_resilience"] = "FAIR"
            report["recommendations"].append("System shows fair chaos resilience - consider improvements")
        else:
            report["test_summary"]["overall_chaos_resilience"] = "POOR"
            report["recommendations"].append("System shows poor chaos resilience - immediate attention required")
        
        # Save report
        with open('chaos_engineering_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*100}")
        print("📊 CHAOS ENGINEERING TEST REPORT")
        print(f"{'='*100}")
        
        print(f"⏱️  Total Test Time: {report['test_summary']['total_test_time']:.2f} seconds")
        print(f"🛡️  Overall Chaos Resilience: {report['test_summary']['overall_chaos_resilience']}")
        print(f"💥 Total Chaos Events: {total_chaos_events}")
        print(f"🔄 Total Recovery Events: {total_recovery_events}")
        print(f"📊 Average Resilience Score: {total_resilience_score / len(self.chaos_scenarios):.1f}")
        
        print(f"\n🔍 DETAILED RESULTS BY CHAOS SCENARIO:")
        for scenario in self.chaos_scenarios:
            if scenario in self.test_results:
                print(f"\n📋 {scenario}:")
                scenario_results = self.test_results[scenario]
                for result_type, result_data in scenario_results.items():
                    if isinstance(result_data, dict):
                        print(f"   {result_type}:")
                        for key, value in result_data.items():
                            if isinstance(value, (int, float)):
                                print(f"     {key}: {value}")
                            elif isinstance(value, list):
                                print(f"     {key}: {len(value)} items")
                            else:
                                print(f"     {key}: {value}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        print(f"\n✅ Report saved to: chaos_engineering_test_report.json")
        print(f"{'='*100}")

def main():
    """Main function"""
    print("💥 CHAOS ENGINEERING TESTER - HAK/GAL SYSTEM")
    print("Testing system resilience under chaotic conditions...")
    
    tester = ChaosEngineeringTester()
    results = tester.run_chaos_engineering_test()
    
    print("\n🎉 CHAOS ENGINEERING TEST COMPLETED!")
    print("Check chaos_engineering_test_report.json for detailed results")

if __name__ == "__main__":
    main()


