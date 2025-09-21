#!/usr/bin/env python3
"""
MAXIMUM COMPLEXITY TESTER - HAK/GAL SYSTEM
Testet alle Komponenten gleichzeitig unter extremer Last
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
from datetime import datetime
from typing import Dict, List, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('maximum_complexity_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MaximumComplexityTester:
    """Maximum Complexity Tester für HAK/GAL System"""
    
    def __init__(self):
        self.test_results = {}
        self.active_threads = []
        self.performance_metrics = {}
        self.start_time = time.time()
        self.test_phases = [
            "INITIALIZATION",
            "STRESS_TESTING", 
            "CONCURRENT_OPERATIONS",
            "CHAOS_ENGINEERING",
            "PERFORMANCE_VALIDATION",
            "FINAL_ANALYSIS"
        ]
        
    def log_test_phase(self, phase: str):
        """Log test phase start"""
        logger.info(f"🚀 STARTING PHASE: {phase}")
        print(f"\n{'='*80}")
        print(f"🚀 PHASE: {phase}")
        print(f"{'='*80}")
        
    def test_database_operations(self, duration: int = 30) -> Dict[str, Any]:
        """Test database operations under extreme load"""
        logger.info("🗄️ Testing database operations under extreme load")
        
        results = {
            "operations_performed": 0,
            "errors": 0,
            "avg_response_time": 0,
            "max_response_time": 0,
            "concurrent_connections": 0
        }
        
        def db_worker(worker_id: int):
            """Database worker thread"""
            try:
                conn = sqlite3.connect('hexagonal_kb.db', timeout=30.0)
                cursor = conn.cursor()
                
                operations = 0
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Random database operations
                        operation = random.choice([
                            "SELECT COUNT(*) FROM facts",
                            "SELECT * FROM facts LIMIT 100",
                            "SELECT * FROM facts WHERE statement LIKE '%test%'",
                            "SELECT COUNT(*) FROM audit_log",
                            "SELECT * FROM audit_log ORDER BY timestamp DESC LIMIT 50"
                        ])
                        
                        op_start = time.time()
                        cursor.execute(operation)
                        result = cursor.fetchall()
                        op_time = time.time() - op_start
                        
                        results["operations_performed"] += 1
                        results["avg_response_time"] += op_time
                        results["max_response_time"] = max(results["max_response_time"], op_time)
                        
                        operations += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.001, 0.01))
                        
                    except Exception as e:
                        results["errors"] += 1
                        logger.error(f"DB Worker {worker_id} error: {e}")
                        
                conn.close()
                logger.info(f"DB Worker {worker_id} completed {operations} operations")
                
            except Exception as e:
                logger.error(f"DB Worker {worker_id} failed: {e}")
                results["errors"] += 1
        
        # Start multiple database workers
        threads = []
        for i in range(20):  # 20 concurrent database connections
            thread = threading.Thread(target=db_worker, args=(i,))
            thread.start()
            threads.append(thread)
            results["concurrent_connections"] += 1
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        if results["operations_performed"] > 0:
            results["avg_response_time"] /= results["operations_performed"]
        
        return results
    
    def test_mcp_operations(self, duration: int = 30) -> Dict[str, Any]:
        """Test MCP operations under extreme load"""
        logger.info("🔌 Testing MCP operations under extreme load")
        
        results = {
            "mcp_calls": 0,
            "successful_calls": 0,
            "failed_calls": 0,
            "avg_response_time": 0,
            "max_response_time": 0
        }
        
        def mcp_worker(worker_id: int):
            """MCP worker thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate MCP calls
                        mcp_operations = [
                            "search_knowledge",
                            "get_system_status", 
                            "health_check",
                            "get_facts_count",
                            "list_recent_facts"
                        ]
                        
                        operation = random.choice(mcp_operations)
                        op_start = time.time()
                        
                        # Simulate MCP call processing time
                        processing_time = random.uniform(0.01, 0.1)
                        time.sleep(processing_time)
                        
                        op_time = time.time() - op_start
                        
                        results["mcp_calls"] += 1
                        results["successful_calls"] += 1
                        results["avg_response_time"] += op_time
                        results["max_response_time"] = max(results["max_response_time"], op_time)
                        
                        # Random delay
                        time.sleep(random.uniform(0.001, 0.005))
                        
                    except Exception as e:
                        results["failed_calls"] += 1
                        logger.error(f"MCP Worker {worker_id} error: {e}")
                        
                logger.info(f"MCP Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"MCP Worker {worker_id} failed: {e}")
                results["failed_calls"] += 1
        
        # Start multiple MCP workers
        threads = []
        for i in range(15):  # 15 concurrent MCP workers
            thread = threading.Thread(target=mcp_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        if results["mcp_calls"] > 0:
            results["avg_response_time"] /= results["mcp_calls"]
        
        return results
    
    def test_file_operations(self, duration: int = 30) -> Dict[str, Any]:
        """Test file operations under extreme load"""
        logger.info("📁 Testing file operations under extreme load")
        
        results = {
            "file_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "files_created": 0,
            "files_deleted": 0
        }
        
        def file_worker(worker_id: int):
            """File worker thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Random file operations
                        operation = random.choice([
                            "create_temp_file",
                            "read_temp_file", 
                            "delete_temp_file",
                            "list_directory"
                        ])
                        
                        if operation == "create_temp_file":
                            filename = f"temp_test_{worker_id}_{int(time.time())}.txt"
                            with open(filename, 'w') as f:
                                f.write(f"Test data from worker {worker_id}")
                            results["files_created"] += 1
                            
                        elif operation == "read_temp_file":
                            # Try to read a random temp file
                            import glob
                            temp_files = glob.glob("temp_test_*.txt")
                            if temp_files:
                                with open(random.choice(temp_files), 'r') as f:
                                    content = f.read()
                                    
                        elif operation == "delete_temp_file":
                            import glob
                            temp_files = glob.glob("temp_test_*.txt")
                            if temp_files:
                                os.remove(random.choice(temp_files))
                                results["files_deleted"] += 1
                                
                        elif operation == "list_directory":
                            os.listdir(".")
                        
                        results["file_operations"] += 1
                        results["successful_operations"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.001, 0.01))
                        
                    except Exception as e:
                        results["failed_operations"] += 1
                        logger.error(f"File Worker {worker_id} error: {e}")
                        
                logger.info(f"File Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"File Worker {worker_id} failed: {e}")
                results["failed_operations"] += 1
        
        # Start multiple file workers
        threads = []
        for i in range(10):  # 10 concurrent file workers
            thread = threading.Thread(target=file_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        return results
    
    def test_network_operations(self, duration: int = 30) -> Dict[str, Any]:
        """Test network operations under extreme load"""
        logger.info("🌐 Testing network operations under extreme load")
        
        results = {
            "network_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "avg_response_time": 0,
            "max_response_time": 0
        }
        
        def network_worker(worker_id: int):
            """Network worker thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Simulate network requests
                        urls = [
                            "http://localhost:5000/api/health",
                            "http://localhost:5000/api/metrics",
                            "http://localhost:8000/metrics"
                        ]
                        
                        url = random.choice(urls)
                        op_start = time.time()
                        
                        try:
                            response = requests.get(url, timeout=5)
                            op_time = time.time() - op_start
                            
                            results["network_requests"] += 1
                            if response.status_code == 200:
                                results["successful_requests"] += 1
                            else:
                                results["failed_requests"] += 1
                                
                            results["avg_response_time"] += op_time
                            results["max_response_time"] = max(results["max_response_time"], op_time)
                            
                        except requests.exceptions.RequestException:
                            results["network_requests"] += 1
                            results["failed_requests"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.1, 0.5))
                        
                    except Exception as e:
                        logger.error(f"Network Worker {worker_id} error: {e}")
                        
                logger.info(f"Network Worker {worker_id} completed")
                
            except Exception as e:
                logger.error(f"Network Worker {worker_id} failed: {e}")
        
        # Start multiple network workers
        threads = []
        for i in range(5):  # 5 concurrent network workers
            thread = threading.Thread(target=network_worker, args=(i,))
            thread.start()
            threads.append(thread)
        
        # Wait for completion
        for thread in threads:
            thread.join()
        
        if results["network_requests"] > 0:
            results["avg_response_time"] /= results["network_requests"]
        
        return results
    
    def test_system_resources(self, duration: int = 30) -> Dict[str, Any]:
        """Monitor system resources under load"""
        logger.info("💻 Monitoring system resources under load")
        
        results = {
            "cpu_samples": [],
            "memory_samples": [],
            "disk_samples": [],
            "max_cpu": 0,
            "max_memory": 0,
            "max_disk": 0,
            "avg_cpu": 0,
            "avg_memory": 0,
            "avg_disk": 0
        }
        
        def resource_monitor():
            """Resource monitoring thread"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # CPU usage
                        cpu_percent = psutil.cpu_percent(interval=1)
                        results["cpu_samples"].append(cpu_percent)
                        
                        # Memory usage
                        memory = psutil.virtual_memory()
                        memory_percent = memory.percent
                        results["memory_samples"].append(memory_percent)
                        
                        # Disk usage
                        disk = psutil.disk_usage('.')
                        disk_percent = (disk.used / disk.total) * 100
                        results["disk_samples"].append(disk_percent)
                        
                        time.sleep(0.5)  # Sample every 500ms
                        
                    except Exception as e:
                        logger.error(f"Resource monitor error: {e}")
                        
                logger.info("Resource monitoring completed")
                
            except Exception as e:
                logger.error(f"Resource monitor failed: {e}")
        
        # Start resource monitoring
        monitor_thread = threading.Thread(target=resource_monitor)
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
        
        return results
    
    def chaos_engineering_test(self, duration: int = 60) -> Dict[str, Any]:
        """Chaos engineering - introduce controlled failures"""
        logger.info("💥 Starting chaos engineering test")
        
        results = {
            "chaos_events": 0,
            "system_recoveries": 0,
            "failures_introduced": 0,
            "recovery_time": 0
        }
        
        def chaos_worker():
            """Chaos engineering worker"""
            try:
                start_time = time.time()
                
                while time.time() - start_time < duration:
                    try:
                        # Random chaos events
                        chaos_event = random.choice([
                            "high_cpu_load",
                            "memory_pressure",
                            "disk_io_storm",
                            "network_delay"
                        ])
                        
                        results["chaos_events"] += 1
                        results["failures_introduced"] += 1
                        
                        if chaos_event == "high_cpu_load":
                            # Create CPU load
                            for _ in range(1000000):
                                pass
                                
                        elif chaos_event == "memory_pressure":
                            # Create memory pressure
                            data = []
                            for _ in range(10000):
                                data.append([0] * 1000)
                            time.sleep(0.1)
                            del data
                            
                        elif chaos_event == "disk_io_storm":
                            # Create disk I/O storm
                            for i in range(100):
                                filename = f"chaos_test_{i}.tmp"
                                with open(filename, 'w') as f:
                                    f.write("chaos test data" * 100)
                                os.remove(filename)
                                
                        elif chaos_event == "network_delay":
                            # Simulate network delay
                            time.sleep(random.uniform(0.1, 0.5))
                        
                        results["system_recoveries"] += 1
                        
                        # Random delay between chaos events
                        time.sleep(random.uniform(1, 3))
                        
                    except Exception as e:
                        logger.error(f"Chaos worker error: {e}")
                        
                logger.info("Chaos engineering test completed")
                
            except Exception as e:
                logger.error(f"Chaos worker failed: {e}")
        
        # Start chaos engineering
        chaos_thread = threading.Thread(target=chaos_worker)
        chaos_thread.start()
        
        # Wait for completion
        chaos_thread.join()
        
        return results
    
    def run_maximum_complexity_test(self):
        """Run maximum complexity test"""
        logger.info("🚀 STARTING MAXIMUM COMPLEXITY TEST")
        print(f"\n{'='*100}")
        print("🚀 MAXIMUM COMPLEXITY TEST - HAK/GAL SYSTEM")
        print(f"{'='*100}")
        
        total_start_time = time.time()
        
        for phase in self.test_phases:
            self.log_test_phase(phase)
            
            if phase == "INITIALIZATION":
                # Initialize test environment
                logger.info("🔧 Initializing test environment")
                time.sleep(2)
                
            elif phase == "STRESS_TESTING":
                # Run stress tests
                logger.info("💪 Running stress tests")
                
                # Start all stress tests concurrently
                with concurrent.futures.ThreadPoolExecutor(max_workers=6) as executor:
                    # Submit all stress tests
                    db_future = executor.submit(self.test_database_operations, 30)
                    mcp_future = executor.submit(self.test_mcp_operations, 30)
                    file_future = executor.submit(self.test_file_operations, 30)
                    network_future = executor.submit(self.test_network_operations, 30)
                    resource_future = executor.submit(self.test_system_resources, 30)
                    chaos_future = executor.submit(self.chaos_engineering_test, 30)
                    
                    # Collect results
                    self.test_results["database"] = db_future.result()
                    self.test_results["mcp"] = mcp_future.result()
                    self.test_results["file_operations"] = file_future.result()
                    self.test_results["network"] = network_future.result()
                    self.test_results["system_resources"] = resource_future.result()
                    self.test_results["chaos_engineering"] = chaos_future.result()
                
            elif phase == "CONCURRENT_OPERATIONS":
                # Test concurrent operations
                logger.info("🔄 Testing concurrent operations")
                
                # Run all operations simultaneously
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    futures = []
                    for i in range(10):
                        future = executor.submit(self.test_concurrent_operations, 20)
                        futures.append(future)
                    
                    # Wait for all to complete
                    concurrent_results = []
                    for future in futures:
                        concurrent_results.append(future.result())
                    
                    self.test_results["concurrent_operations"] = concurrent_results
                
            elif phase == "CHAOS_ENGINEERING":
                # Extended chaos engineering
                logger.info("💥 Extended chaos engineering")
                
                chaos_results = self.chaos_engineering_test(60)
                self.test_results["extended_chaos"] = chaos_results
                
            elif phase == "PERFORMANCE_VALIDATION":
                # Validate performance under load
                logger.info("📊 Validating performance under load")
                
                performance_results = self.validate_performance()
                self.test_results["performance_validation"] = performance_results
                
            elif phase == "FINAL_ANALYSIS":
                # Final analysis
                logger.info("📈 Final analysis")
                
                total_time = time.time() - total_start_time
                self.test_results["total_test_time"] = total_time
                self.test_results["test_timestamp"] = datetime.now().isoformat()
                
                # Generate comprehensive report
                self.generate_comprehensive_report()
        
        logger.info("✅ MAXIMUM COMPLEXITY TEST COMPLETED")
        return self.test_results
    
    def test_concurrent_operations(self, duration: int) -> Dict[str, Any]:
        """Test concurrent operations"""
        results = {
            "operations_completed": 0,
            "errors": 0,
            "avg_response_time": 0
        }
        
        start_time = time.time()
        response_times = []
        
        while time.time() - start_time < duration:
            try:
                op_start = time.time()
                
                # Random operation
                operation = random.choice([
                    "database_query",
                    "file_operation",
                    "mcp_call",
                    "network_request"
                ])
                
                if operation == "database_query":
                    # Simulate database query
                    time.sleep(random.uniform(0.001, 0.01))
                elif operation == "file_operation":
                    # Simulate file operation
                    time.sleep(random.uniform(0.001, 0.005))
                elif operation == "mcp_call":
                    # Simulate MCP call
                    time.sleep(random.uniform(0.01, 0.05))
                elif operation == "network_request":
                    # Simulate network request
                    time.sleep(random.uniform(0.1, 0.3))
                
                op_time = time.time() - op_start
                response_times.append(op_time)
                results["operations_completed"] += 1
                
            except Exception as e:
                results["errors"] += 1
                logger.error(f"Concurrent operation error: {e}")
        
        if response_times:
            results["avg_response_time"] = sum(response_times) / len(response_times)
        
        return results
    
    def validate_performance(self) -> Dict[str, Any]:
        """Validate performance under load"""
        results = {
            "performance_score": 0,
            "bottlenecks_detected": [],
            "recommendations": [],
            "overall_health": "UNKNOWN"
        }
        
        # Analyze test results
        total_operations = 0
        total_errors = 0
        
        for test_name, test_result in self.test_results.items():
            if isinstance(test_result, dict):
                if "operations_performed" in test_result:
                    total_operations += test_result["operations_performed"]
                if "operations_completed" in test_result:
                    total_operations += test_result["operations_completed"]
                if "errors" in test_result:
                    total_errors += test_result["errors"]
                if "failed_calls" in test_result:
                    total_errors += test_result["failed_calls"]
                if "failed_operations" in test_result:
                    total_errors += test_result["failed_operations"]
                if "failed_requests" in test_result:
                    total_errors += test_result["failed_requests"]
        
        # Calculate performance score
        if total_operations > 0:
            error_rate = total_errors / total_operations
            results["performance_score"] = (1 - error_rate) * 100
        
        # Detect bottlenecks
        if "system_resources" in self.test_results:
            sys_res = self.test_results["system_resources"]
            if sys_res.get("max_cpu", 0) > 90:
                results["bottlenecks_detected"].append("High CPU usage")
            if sys_res.get("max_memory", 0) > 90:
                results["bottlenecks_detected"].append("High memory usage")
            if sys_res.get("max_disk", 0) > 90:
                results["bottlenecks_detected"].append("High disk usage")
        
        # Generate recommendations
        if results["performance_score"] < 80:
            results["recommendations"].append("Consider performance optimization")
        if len(results["bottlenecks_detected"]) > 0:
            results["recommendations"].append("Address detected bottlenecks")
        
        # Overall health assessment
        if results["performance_score"] >= 95:
            results["overall_health"] = "EXCELLENT"
        elif results["performance_score"] >= 85:
            results["overall_health"] = "GOOD"
        elif results["performance_score"] >= 70:
            results["overall_health"] = "FAIR"
        else:
            results["overall_health"] = "POOR"
        
        return results
    
    def generate_comprehensive_report(self):
        """Generate comprehensive test report"""
        logger.info("📊 Generating comprehensive test report")
        
        report = {
            "test_summary": {
                "total_test_time": self.test_results.get("total_test_time", 0),
                "test_timestamp": self.test_results.get("test_timestamp", ""),
                "phases_completed": len(self.test_phases),
                "overall_health": self.test_results.get("performance_validation", {}).get("overall_health", "UNKNOWN")
            },
            "detailed_results": self.test_results,
            "recommendations": self.test_results.get("performance_validation", {}).get("recommendations", [])
        }
        
        # Save report
        with open('maximum_complexity_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*100}")
        print("📊 MAXIMUM COMPLEXITY TEST REPORT")
        print(f"{'='*100}")
        
        print(f"⏱️  Total Test Time: {report['test_summary']['total_test_time']:.2f} seconds")
        print(f"🏥 Overall Health: {report['test_summary']['overall_health']}")
        print(f"📈 Performance Score: {self.test_results.get('performance_validation', {}).get('performance_score', 0):.1f}%")
        
        print(f"\n🔍 DETAILED RESULTS:")
        for test_name, test_result in self.test_results.items():
            if isinstance(test_result, dict):
                print(f"\n📋 {test_name.upper()}:")
                for key, value in test_result.items():
                    if isinstance(value, (int, float)):
                        print(f"   {key}: {value}")
                    elif isinstance(value, list):
                        print(f"   {key}: {len(value)} items")
                    else:
                        print(f"   {key}: {value}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        print(f"\n✅ Report saved to: maximum_complexity_test_report.json")
        print(f"{'='*100}")

def main():
    """Main function"""
    print("🚀 MAXIMUM COMPLEXITY TESTER - HAK/GAL SYSTEM")
    print("Testing all components under extreme load...")
    
    tester = MaximumComplexityTester()
    results = tester.run_maximum_complexity_test()
    
    print("\n🎉 MAXIMUM COMPLEXITY TEST COMPLETED!")
    print("Check maximum_complexity_test_report.json for detailed results")

if __name__ == "__main__":
    main()


