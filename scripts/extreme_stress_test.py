#!/usr/bin/env python3
"""
EXTREME STRESS TEST - HAK/GAL SYSTEM
Testet das System unter extremen Bedingungen
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
import multiprocessing
from datetime import datetime
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('extreme_stress_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ExtremeStressTester:
    """Extreme Stress Tester für HAK/GAL System"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = time.time()
        self.stress_levels = [
            "LOW_STRESS",
            "MEDIUM_STRESS", 
            "HIGH_STRESS",
            "EXTREME_STRESS",
            "MAXIMUM_STRESS"
        ]
        
    def log_stress_level(self, level: str):
        """Log stress level"""
        logger.info(f"🔥 STRESS LEVEL: {level}")
        print(f"\n{'='*80}")
        print(f"🔥 STRESS LEVEL: {level}")
        print(f"{'='*80}")
        
    def create_cpu_storm(self, duration: int, intensity: int = 100) -> Dict[str, Any]:
        """Create CPU storm"""
        logger.info(f"⚡ Creating CPU storm - Intensity: {intensity}%")
        
        results = {
            "cpu_storm_duration": duration,
            "intensity": intensity,
            "processes_created": 0,
            "total_cpu_time": 0
        }
        
        def cpu_worker(worker_id: int, intensity: int):
            """CPU worker process"""
            try:
                start_time = time.time()
                cpu_time = 0
                
                while time.time() - start_time < duration:
                    # Create CPU load based on intensity
                    load_factor = intensity / 100.0
                    
                    # CPU intensive operations
                    for _ in range(int(1000000 * load_factor)):
                        # Mathematical operations
                        result = sum(i * i for i in range(1000))
                        cpu_time += 1
                    
                    # Brief pause to prevent system lockup
                    time.sleep(0.001)
                
                results["total_cpu_time"] += cpu_time
                logger.info(f"CPU Worker {worker_id} completed - CPU time: {cpu_time}")
                
            except Exception as e:
                logger.error(f"CPU Worker {worker_id} failed: {e}")
        
        # Create multiple CPU workers
        processes = []
        num_processes = min(intensity // 10, multiprocessing.cpu_count() * 2)
        
        for i in range(num_processes):
            process = multiprocessing.Process(target=cpu_worker, args=(i, intensity))
            process.start()
            processes.append(process)
            results["processes_created"] += 1
        
        # Wait for completion
        for process in processes:
            process.join()
        
        return results
    
    def create_memory_storm(self, duration: int, intensity: int = 100) -> Dict[str, Any]:
        """Create memory storm"""
        logger.info(f"💾 Creating memory storm - Intensity: {intensity}%")
        
        results = {
            "memory_storm_duration": duration,
            "intensity": intensity,
            "memory_allocated": 0,
            "allocation_cycles": 0
        }
        
        def memory_worker(worker_id: int, intensity: int):
            """Memory worker thread"""
            try:
                start_time = time.time()
                memory_data = []
                allocation_size = int(1024 * 1024 * intensity / 100)  # MB based on intensity
                
                while time.time() - start_time < duration:
                    try:
                        # Allocate memory
                        data = [0] * allocation_size
                        memory_data.append(data)
                        results["memory_allocated"] += allocation_size
                        results["allocation_cycles"] += 1
                        
                        # Brief pause
                        time.sleep(0.1)
                        
                        # Deallocate some memory to prevent OOM
                        if len(memory_data) > 10:
                            memory_data.pop(0)
                            
                    except MemoryError:
                        logger.warning(f"Memory Worker {worker_id} hit memory limit")
                        # Clear some memory
                        memory_data.clear()
                        time.sleep(0.5)
                        
                logger.info(f"Memory Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Memory Worker {worker_id} failed: {e}")
        
        # Create multiple memory workers
        threads = []
        num_threads = min(intensity // 20, 10)
        
        for i in range(num_threads):
            thread = threading.Thread(target=memory_worker, args=(i, intensity))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def create_disk_storm(self, duration: int, intensity: int = 100) -> Dict[str, Any]:
        """Create disk I/O storm"""
        logger.info(f"💿 Creating disk storm - Intensity: {intensity}%")
        
        results = {
            "disk_storm_duration": duration,
            "intensity": intensity,
            "files_created": 0,
            "files_deleted": 0,
            "total_bytes_written": 0
        }
        
        def disk_worker(worker_id: int, intensity: int):
            """Disk worker thread"""
            try:
                start_time = time.time()
                file_size = int(1024 * intensity / 100)  # KB based on intensity
                
                while time.time() - start_time < duration:
                    try:
                        # Create temporary file
                        filename = f"stress_test_{worker_id}_{int(time.time())}.tmp"
                        
                        # Write data
                        with open(filename, 'w') as f:
                            data = "X" * file_size
                            f.write(data)
                            results["total_bytes_written"] += file_size
                        
                        results["files_created"] += 1
                        
                        # Read data
                        with open(filename, 'r') as f:
                            content = f.read()
                        
                        # Delete file
                        os.remove(filename)
                        results["files_deleted"] += 1
                        
                        # Brief pause
                        time.sleep(0.01)
                        
                    except Exception as e:
                        logger.error(f"Disk Worker {worker_id} error: {e}")
                        
                logger.info(f"Disk Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Disk Worker {worker_id} failed: {e}")
        
        # Create multiple disk workers
        threads = []
        num_threads = min(intensity // 25, 8)
        
        for i in range(num_threads):
            thread = threading.Thread(target=disk_worker, args=(i, intensity))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def create_network_storm(self, duration: int, intensity: int = 100) -> Dict[str, Any]:
        """Create network storm"""
        logger.info(f"🌐 Creating network storm - Intensity: {intensity}%")
        
        results = {
            "network_storm_duration": duration,
            "intensity": intensity,
            "requests_sent": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_bytes_transferred": 0
        }
        
        def network_worker(worker_id: int, intensity: int):
            """Network worker thread"""
            try:
                start_time = time.time()
                request_interval = max(0.001, 0.1 - (intensity / 1000))  # Faster requests with higher intensity
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate network requests
                        urls = [
                            "http://localhost:5000/api/health",
                            "http://localhost:5000/api/metrics",
                            "http://localhost:8000/metrics"
                        ]
                        
                        url = random.choice(urls)
                        
                        try:
                            response = requests.get(url, timeout=2)
                            results["requests_sent"] += 1
                            
                            if response.status_code == 200:
                                results["successful_requests"] += 1
                                results["total_bytes_transferred"] += len(response.content)
                            else:
                                results["failed_requests"] += 1
                                
                        except requests.exceptions.RequestException:
                            results["requests_sent"] += 1
                            results["failed_requests"] += 1
                        
                        # Brief pause
                        time.sleep(request_interval)
                        
                    except Exception as e:
                        logger.error(f"Network Worker {worker_id} error: {e}")
                        
                logger.info(f"Network Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Network Worker {worker_id} failed: {e}")
        
        # Create multiple network workers
        threads = []
        num_threads = min(intensity // 20, 5)
        
        for i in range(num_threads):
            thread = threading.Thread(target=network_worker, args=(i, intensity))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def create_database_storm(self, duration: int, intensity: int = 100) -> Dict[str, Any]:
        """Create database storm"""
        logger.info(f"🗄️ Creating database storm - Intensity: {intensity}%")
        
        results = {
            "database_storm_duration": duration,
            "intensity": intensity,
            "queries_executed": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "concurrent_connections": 0
        }
        
        def database_worker(worker_id: int, intensity: int):
            """Database worker thread"""
            try:
                conn = sqlite3.connect('hexagonal_kb.db', timeout=30.0)
                cursor = conn.cursor()
                
                start_time = time.time()
                query_interval = max(0.001, 0.01 - (intensity / 10000))  # Faster queries with higher intensity
                
                while time.time() - start_time < duration:
                    try:
                        # Random database queries
                        queries = [
                            "SELECT COUNT(*) FROM facts",
                            "SELECT * FROM facts LIMIT 100",
                            "SELECT * FROM facts WHERE statement LIKE '%test%'",
                            "SELECT COUNT(*) FROM audit_log",
                            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50",
                            "SELECT COUNT(*) FROM facts WHERE statement LIKE '%stress%'",
                            "SELECT * FROM facts ORDER BY RANDOM() LIMIT 10"
                        ]
                        
                        query = random.choice(queries)
                        cursor.execute(query)
                        result = cursor.fetchall()
                        
                        results["queries_executed"] += 1
                        results["successful_queries"] += 1
                        
                        # Brief pause
                        time.sleep(query_interval)
                        
                    except Exception as e:
                        results["queries_executed"] += 1
                        results["failed_queries"] += 1
                        logger.error(f"Database Worker {worker_id} query error: {e}")
                        
                conn.close()
                logger.info(f"Database Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Database Worker {worker_id} failed: {e}")
                results["failed_queries"] += 1
        
        # Create multiple database workers
        threads = []
        num_threads = min(intensity // 15, 20)
        
        for i in range(num_threads):
            thread = threading.Thread(target=database_worker, args=(i, intensity))
            thread.start()
            threads.append(thread)
            results["concurrent_connections"] += 1
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def monitor_system_health(self, duration: int) -> Dict[str, Any]:
        """Monitor system health during stress test"""
        logger.info("🏥 Monitoring system health during stress test")
        
        results = {
            "monitoring_duration": duration,
            "cpu_samples": [],
            "memory_samples": [],
            "disk_samples": [],
            "max_cpu": 0,
            "max_memory": 0,
            "max_disk": 0,
            "avg_cpu": 0,
            "avg_memory": 0,
            "avg_disk": 0,
            "system_stability": "UNKNOWN"
        }
        
        def health_monitor():
            """Health monitoring thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # CPU usage
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        results["cpu_samples"].append(cpu_percent)
                        
                        # Memory usage
                        memory = psutil.virtual_memory()
                        memory_percent = memory.percent
                        results["memory_samples"].append(memory_percent)
                        
                        # Disk usage
                        disk = psutil.disk_usage('.')
                        disk_percent = (disk.used / disk.total) * 100
                        results["disk_samples"].append(disk_percent)
                        
                        time.sleep(0.1)  # Sample every 100ms
                        
                    except Exception as e:
                        logger.error(f"Health monitor error: {e}")
                        
                logger.info("Health monitoring completed")
                
            except Exception as e:
                logger.error(f"Health monitor failed: {e}")
        
        # Start health monitoring
        monitor_thread = threading.Thread(target=health_monitor)
        monitor_thread.start()
        
        # Wait for completion
        monitor_thread.join()
        
        # Calculate statistics
        if results["cpu_samples"]:
            results["max_cpu"] = max(results["cpu_samples"])
            results["avg_cpu"] = sum(results["cpu_samples"]) / len(results["cpu_samples"])
        
        if results["memory_samples"]:
            results["max_memory"] = max(results["memory_samples"])
            results["avg_memory"] = sum(results["memory_samples"]) / len(results["memory_samples"])
        
        if results["disk_samples"]:
            results["max_disk"] = max(results["disk_samples"])
            results["avg_disk"] = sum(results["disk_samples"]) / len(results["disk_samples"])
        
        # Assess system stability
        if results["max_cpu"] > 95 or results["max_memory"] > 95 or results["max_disk"] > 95:
            results["system_stability"] = "CRITICAL"
        elif results["max_cpu"] > 80 or results["max_memory"] > 80 or results["max_disk"] > 80:
            results["system_stability"] = "HIGH_STRESS"
        elif results["max_cpu"] > 60 or results["max_memory"] > 60 or results["max_disk"] > 60:
            results["system_stability"] = "MODERATE_STRESS"
        else:
            results["system_stability"] = "STABLE"
        
        return results
    
    def run_extreme_stress_test(self):
        """Run extreme stress test"""
        logger.info("🔥 STARTING EXTREME STRESS TEST")
        print(f"\n{'='*100}")
        print("🔥 EXTREME STRESS TEST - HAK/GAL SYSTEM")
        print(f"{'='*100}")
        
        total_start_time = time.time()
        
        for level in self.stress_levels:
            self.log_stress_level(level)
            
            # Determine intensity based on stress level
            if level == "LOW_STRESS":
                intensity = 20
                duration = 30
            elif level == "MEDIUM_STRESS":
                intensity = 40
                duration = 45
            elif level == "HIGH_STRESS":
                intensity = 60
                duration = 60
            elif level == "EXTREME_STRESS":
                intensity = 80
                duration = 90
            elif level == "MAXIMUM_STRESS":
                intensity = 100
                duration = 120
            
            logger.info(f"Intensity: {intensity}%, Duration: {duration}s")
            
            # Start all stress tests concurrently
            with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                # Submit all stress tests
                cpu_future = executor.submit(self.create_cpu_storm, duration, intensity)
                memory_future = executor.submit(self.create_memory_storm, duration, intensity)
                disk_future = executor.submit(self.create_disk_storm, duration, intensity)
                network_future = executor.submit(self.create_network_storm, duration, intensity)
                database_future = executor.submit(self.create_database_storm, duration, intensity)
                health_future = executor.submit(self.monitor_system_health, duration)
                
                # Collect results
                self.test_results[level] = {
                    "cpu_storm": cpu_future.result(),
                    "memory_storm": memory_future.result(),
                    "disk_storm": disk_future.result(),
                    "network_storm": network_future.result(),
                    "database_storm": database_future.result(),
                    "system_health": health_future.result()
                }
            
            # Brief pause between stress levels
            time.sleep(5)
        
        # Final analysis
        total_time = time.time() - total_start_time
        self.test_results["total_test_time"] = total_time
        self.test_results["test_timestamp"] = datetime.now().isoformat()
        
        # Generate comprehensive report
        self.generate_stress_report()
        
        logger.info("✅ EXTREME STRESS TEST COMPLETED")
        return self.test_results
    
    def generate_stress_report(self):
        """Generate stress test report"""
        logger.info("📊 Generating stress test report")
        
        report = {
            "test_summary": {
                "total_test_time": self.test_results.get("total_test_time", 0),
                "test_timestamp": self.test_results.get("test_timestamp", ""),
                "stress_levels_tested": len(self.stress_levels),
                "overall_system_stability": "UNKNOWN"
            },
            "detailed_results": self.test_results,
            "recommendations": []
        }
        
        # Analyze results
        max_cpu = 0
        max_memory = 0
        max_disk = 0
        
        for level, results in self.test_results.items():
            if isinstance(results, dict) and "system_health" in results:
                health = results["system_health"]
                max_cpu = max(max_cpu, health.get("max_cpu", 0))
                max_memory = max(max_memory, health.get("max_memory", 0))
                max_disk = max(max_disk, health.get("max_disk", 0))
        
        # Overall stability assessment
        if max_cpu > 95 or max_memory > 95 or max_disk > 95:
            report["test_summary"]["overall_system_stability"] = "CRITICAL"
            report["recommendations"].append("System reached critical limits - immediate attention required")
        elif max_cpu > 80 or max_memory > 80 or max_disk > 80:
            report["test_summary"]["overall_system_stability"] = "HIGH_STRESS"
            report["recommendations"].append("System under high stress - consider optimization")
        elif max_cpu > 60 or max_memory > 60 or max_disk > 60:
            report["test_summary"]["overall_system_stability"] = "MODERATE_STRESS"
            report["recommendations"].append("System under moderate stress - monitor closely")
        else:
            report["test_summary"]["overall_system_stability"] = "STABLE"
            report["recommendations"].append("System handled stress well - good performance")
        
        # Save report
        with open('extreme_stress_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*100}")
        print("📊 EXTREME STRESS TEST REPORT")
        print(f"{'='*100}")
        
        print(f"⏱️  Total Test Time: {report['test_summary']['total_test_time']:.2f} seconds")
        print(f"🏥 Overall System Stability: {report['test_summary']['overall_system_stability']}")
        print(f"🔥 Max CPU Usage: {max_cpu:.1f}%")
        print(f"💾 Max Memory Usage: {max_memory:.1f}%")
        print(f"💿 Max Disk Usage: {max_disk:.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS BY STRESS LEVEL:")
        for level in self.stress_levels:
            if level in self.test_results:
                print(f"\n📋 {level}:")
                level_results = self.test_results[level]
                for test_type, test_result in level_results.items():
                    if isinstance(test_result, dict):
                        print(f"   {test_type}:")
                        for key, value in test_result.items():
                            if isinstance(value, (int, float)):
                                print(f"     {key}: {value}")
                            elif isinstance(value, list):
                                print(f"     {key}: {len(value)} samples")
                            else:
                                print(f"     {key}: {value}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        print(f"\n✅ Report saved to: extreme_stress_test_report.json")
        print(f"{'='*100}")

def main():
    """Main function"""
    print("🔥 EXTREME STRESS TESTER - HAK/GAL SYSTEM")
    print("Testing system under extreme stress conditions...")
    
    tester = ExtremeStressTester()
    results = tester.run_extreme_stress_test()
    
    print("\n🎉 EXTREME STRESS TEST COMPLETED!")
    print("Check extreme_stress_test_report.json for detailed results")

if __name__ == "__main__":
    main()


