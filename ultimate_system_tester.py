#!/usr/bin/env python3
"""
ULTIMATE SYSTEM TESTER - HAK/GAL SYSTEM
Kombiniert alle Tests für maximale Komplexität
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

# Import our test modules
from maximum_complexity_tester import MaximumComplexityTester
from extreme_stress_test import ExtremeStressTester
from chaos_engineering_test import ChaosEngineeringTester

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ultimate_system_test.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UltimateSystemTester:
    """Ultimate System Tester - Kombiniert alle Tests"""
    
    def __init__(self):
        self.test_results = {}
        self.performance_metrics = {}
        self.start_time = time.time()
        self.test_suites = [
            "MAXIMUM_COMPLEXITY",
            "EXTREME_STRESS", 
            "CHAOS_ENGINEERING",
            "COMBINED_STRESS",
            "FINAL_VALIDATION"
        ]
        
        # Initialize testers
        self.complexity_tester = MaximumComplexityTester()
        self.stress_tester = ExtremeStressTester()
        self.chaos_tester = ChaosEngineeringTester()
        
    def log_test_suite(self, suite: str):
        """Log test suite"""
        logger.info(f"🚀 TEST SUITE: {suite}")
        print(f"\n{'='*100}")
        print(f"🚀 TEST SUITE: {suite}")
        print(f"{'='*100}")
        
    def run_maximum_complexity_suite(self) -> Dict[str, Any]:
        """Run maximum complexity test suite"""
        logger.info("🔧 Running Maximum Complexity Test Suite")
        
        try:
            results = self.complexity_tester.run_maximum_complexity_test()
            logger.info("✅ Maximum Complexity Test Suite completed")
            return results
        except Exception as e:
            logger.error(f"❌ Maximum Complexity Test Suite failed: {e}")
            return {"error": str(e)}
    
    def run_extreme_stress_suite(self) -> Dict[str, Any]:
        """Run extreme stress test suite"""
        logger.info("🔥 Running Extreme Stress Test Suite")
        
        try:
            results = self.stress_tester.run_extreme_stress_test()
            logger.info("✅ Extreme Stress Test Suite completed")
            return results
        except Exception as e:
            logger.error(f"❌ Extreme Stress Test Suite failed: {e}")
            return {"error": str(e)}
    
    def run_chaos_engineering_suite(self) -> Dict[str, Any]:
        """Run chaos engineering test suite"""
        logger.info("💥 Running Chaos Engineering Test Suite")
        
        try:
            results = self.chaos_tester.run_chaos_engineering_test()
            logger.info("✅ Chaos Engineering Test Suite completed")
            return results
        except Exception as e:
            logger.error(f"❌ Chaos Engineering Test Suite failed: {e}")
            return {"error": str(e)}
    
    def run_combined_stress_test(self) -> Dict[str, Any]:
        """Run combined stress test - all systems under load simultaneously"""
        logger.info("⚡ Running Combined Stress Test")
        
        results = {
            "combined_stress_duration": 300,  # 5 minutes
            "concurrent_systems": 0,
            "total_operations": 0,
            "system_failures": 0,
            "recovery_events": 0,
            "performance_metrics": {}
        }
        
        def combined_worker(worker_id: int):
            """Combined stress worker"""
            try:
                start_time = time.time()
                operations = 0
                
                while time.time() - start_time < 300:  # 5 minutes
                    try:
                        # Random system operations
                        operation_type = random.choice([
                            "database_operation",
                            "file_operation",
                            "network_operation",
                            "memory_operation",
                            "cpu_operation"
                        ])
                        
                        if operation_type == "database_operation":
                            # Database stress
                            conn = sqlite3.connect('hexagonal_kb.db', timeout=10.0)
                            cursor = conn.cursor()
                            cursor.execute("SELECT COUNT(*) FROM facts")
                            result = cursor.fetchall()
                            conn.close()
                            
                        elif operation_type == "file_operation":
                            # File stress
                            filename = f"combined_stress_{worker_id}_{int(time.time())}.tmp"
                            with open(filename, 'w') as f:
                                f.write("Combined stress test data" * 1000)
                            os.remove(filename)
                            
                        elif operation_type == "network_operation":
                            # Network stress
                            try:
                                response = requests.get("http://localhost:5000/api/health", timeout=2)
                            except:
                                pass
                            
                        elif operation_type == "memory_operation":
                            # Memory stress
                            data = [0] * 10000
                            time.sleep(0.001)
                            del data
                            
                        elif operation_type == "cpu_operation":
                            # CPU stress
                            for _ in range(100000):
                                result = sum(i * i for i in range(100))
                        
                        operations += 1
                        results["total_operations"] += 1
                        
                        # Random delay
                        time.sleep(random.uniform(0.001, 0.01))
                        
                    except Exception as e:
                        results["system_failures"] += 1
                        logger.error(f"Combined Worker {worker_id} error: {e}")
                        
                logger.info(f"Combined Worker {worker_id} completed {operations} operations")
                
            except Exception as e:
                logger.error(f"Combined Worker {worker_id} failed: {e}")
                results["system_failures"] += 1
        
        # Start multiple combined workers
        threads = []
        for i in range(20):  # 20 concurrent workers
            thread = threading.Thread(target=combined_worker, args=(i,))
            thread.start()
            threads.append(thread)
            results["concurrent_systems"] += 1
        
        # Monitor system health during combined stress
        def health_monitor():
            """Health monitoring during combined stress"""
            try:
                start_time = time.time()
                health_samples = []
                
                while time.time() - start_time < 300:
                    try:
                        cpu_percent = psutil.cpu_percent(interval=0.1)
                        memory_percent = psutil.virtual_memory().percent
                        disk_percent = psutil.disk_usage('.').percent
                        
                        health_sample = {
                            "timestamp": time.time(),
                            "cpu": cpu_percent,
                            "memory": memory_percent,
                            "disk": disk_percent
                        }
                        
                        health_samples.append(health_sample)
                        
                        # Detect recovery
                        if cpu_percent < 50 and memory_percent < 50 and disk_percent < 50:
                            results["recovery_events"] += 1
                        
                        time.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Health monitor error: {e}")
                        
                results["performance_metrics"]["health_samples"] = health_samples
                logger.info("Health monitoring completed")
                
            except Exception as e:
                logger.error(f"Health monitor failed: {e}")
        
        # Start health monitoring
        monitor_thread = threading.Thread(target=health_monitor)
        monitor_thread.start()
        
        # Wait for all workers to complete
        for thread in threads:
            thread.join()
        
        monitor_thread.join()
        
        return results
    
    def run_final_validation(self) -> Dict[str, Any]:
        """Run final system validation"""
        logger.info("🔍 Running Final System Validation")
        
        results = {
            "validation_timestamp": datetime.now().isoformat(),
            "system_health": {},
            "performance_metrics": {},
            "stability_assessment": "UNKNOWN",
            "recommendations": []
        }
        
        # System health check
        try:
            # CPU health
            cpu_percent = psutil.cpu_percent(interval=1)
            results["system_health"]["cpu_usage"] = cpu_percent
            
            # Memory health
            memory = psutil.virtual_memory()
            results["system_health"]["memory_usage"] = memory.percent
            results["system_health"]["memory_available"] = memory.available
            
            # Disk health
            disk = psutil.disk_usage('.')
            results["system_health"]["disk_usage"] = (disk.used / disk.total) * 100
            results["system_health"]["disk_free"] = disk.free
            
            # Database health
            try:
                conn = sqlite3.connect('hexagonal_kb.db', timeout=10.0)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM facts")
                fact_count = cursor.fetchone()[0]
                conn.close()
                results["system_health"]["database_facts"] = fact_count
            except Exception as e:
                results["system_health"]["database_error"] = str(e)
            
            # Network health
            try:
                response = requests.get("http://localhost:5000/api/health", timeout=5)
                results["system_health"]["network_status"] = response.status_code
            except Exception as e:
                results["system_health"]["network_error"] = str(e)
            
        except Exception as e:
            logger.error(f"System health check failed: {e}")
            results["system_health"]["error"] = str(e)
        
        # Performance metrics
        try:
            # Calculate performance score
            cpu_score = max(0, 100 - cpu_percent)
            memory_score = max(0, 100 - memory.percent)
            disk_score = max(0, 100 - (disk.used / disk.total) * 100)
            
            overall_score = (cpu_score + memory_score + disk_score) / 3
            results["performance_metrics"]["overall_score"] = overall_score
            results["performance_metrics"]["cpu_score"] = cpu_score
            results["performance_metrics"]["memory_score"] = memory_score
            results["performance_metrics"]["disk_score"] = disk_score
            
        except Exception as e:
            logger.error(f"Performance metrics calculation failed: {e}")
            results["performance_metrics"]["error"] = str(e)
        
        # Stability assessment
        try:
            if overall_score >= 90:
                results["stability_assessment"] = "EXCELLENT"
                results["recommendations"].append("System is performing excellently")
            elif overall_score >= 75:
                results["stability_assessment"] = "GOOD"
                results["recommendations"].append("System is performing well")
            elif overall_score >= 60:
                results["stability_assessment"] = "FAIR"
                results["recommendations"].append("System performance is fair - consider optimization")
            else:
                results["stability_assessment"] = "POOR"
                results["recommendations"].append("System performance is poor - immediate attention required")
                
        except Exception as e:
            logger.error(f"Stability assessment failed: {e}")
            results["stability_assessment"] = "ERROR"
        
        return results
    
    def run_ultimate_system_test(self):
        """Run ultimate system test"""
        logger.info("🚀 STARTING ULTIMATE SYSTEM TEST")
        print(f"\n{'='*120}")
        print("🚀 ULTIMATE SYSTEM TEST - HAK/GAL SYSTEM")
        print("Kombiniert alle Tests für maximale Komplexität")
        print(f"{'='*120}")
        
        total_start_time = time.time()
        
        for suite in self.test_suites:
            self.log_test_suite(suite)
            
            if suite == "MAXIMUM_COMPLEXITY":
                # Run maximum complexity test suite
                results = self.run_maximum_complexity_suite()
                self.test_results["maximum_complexity"] = results
                
            elif suite == "EXTREME_STRESS":
                # Run extreme stress test suite
                results = self.run_extreme_stress_suite()
                self.test_results["extreme_stress"] = results
                
            elif suite == "CHAOS_ENGINEERING":
                # Run chaos engineering test suite
                results = self.run_chaos_engineering_suite()
                self.test_results["chaos_engineering"] = results
                
            elif suite == "COMBINED_STRESS":
                # Run combined stress test
                results = self.run_combined_stress_test()
                self.test_results["combined_stress"] = results
                
            elif suite == "FINAL_VALIDATION":
                # Run final validation
                results = self.run_final_validation()
                self.test_results["final_validation"] = results
        
        # Final analysis
        total_time = time.time() - total_start_time
        self.test_results["total_test_time"] = total_time
        self.test_results["test_timestamp"] = datetime.now().isoformat()
        
        # Generate ultimate report
        self.generate_ultimate_report()
        
        logger.info("✅ ULTIMATE SYSTEM TEST COMPLETED")
        return self.test_results
    
    def generate_ultimate_report(self):
        """Generate ultimate test report"""
        logger.info("📊 Generating Ultimate Test Report")
        
        report = {
            "test_summary": {
                "total_test_time": self.test_results.get("total_test_time", 0),
                "test_timestamp": self.test_results.get("test_timestamp", ""),
                "test_suites_completed": len(self.test_suites),
                "overall_system_status": "UNKNOWN"
            },
            "detailed_results": self.test_results,
            "recommendations": [],
            "performance_summary": {}
        }
        
        # Analyze all test results
        total_operations = 0
        total_errors = 0
        total_chaos_events = 0
        total_recovery_events = 0
        
        for suite_name, suite_results in self.test_results.items():
            if isinstance(suite_results, dict):
                # Count operations
                if "total_operations" in suite_results:
                    total_operations += suite_results["total_operations"]
                if "operations_performed" in suite_results:
                    total_operations += suite_results["operations_performed"]
                if "operations_completed" in suite_results:
                    total_operations += suite_results["operations_completed"]
                
                # Count errors
                if "errors" in suite_results:
                    total_errors += suite_results["errors"]
                if "failed_calls" in suite_results:
                    total_errors += suite_results["failed_calls"]
                if "failed_operations" in suite_results:
                    total_errors += suite_results["failed_operations"]
                if "system_failures" in suite_results:
                    total_errors += suite_results["system_failures"]
                
                # Count chaos events
                if "chaos_events" in suite_results:
                    total_chaos_events += suite_results["chaos_events"]
                if "performance_degradation" in suite_results:
                    total_chaos_events += suite_results["performance_degradation"]
                
                # Count recovery events
                if "recovery_events" in suite_results:
                    total_recovery_events += suite_results["recovery_events"]
                if "system_recoveries" in suite_results:
                    total_recovery_events += suite_results["system_recoveries"]
        
        # Performance summary
        report["performance_summary"] = {
            "total_operations": total_operations,
            "total_errors": total_errors,
            "total_chaos_events": total_chaos_events,
            "total_recovery_events": total_recovery_events,
            "error_rate": (total_errors / total_operations * 100) if total_operations > 0 else 0,
            "recovery_rate": (total_recovery_events / total_chaos_events * 100) if total_chaos_events > 0 else 0
        }
        
        # Overall system status
        if total_operations > 0:
            error_rate = total_errors / total_operations
            if error_rate < 0.01:  # Less than 1% error rate
                report["test_summary"]["overall_system_status"] = "EXCELLENT"
                report["recommendations"].append("System shows excellent performance and reliability")
            elif error_rate < 0.05:  # Less than 5% error rate
                report["test_summary"]["overall_system_status"] = "GOOD"
                report["recommendations"].append("System shows good performance with minor issues")
            elif error_rate < 0.1:  # Less than 10% error rate
                report["test_summary"]["overall_system_status"] = "FAIR"
                report["recommendations"].append("System shows fair performance - consider optimization")
            else:
                report["test_summary"]["overall_system_status"] = "POOR"
                report["recommendations"].append("System shows poor performance - immediate attention required")
        
        # Add specific recommendations based on test results
        if "final_validation" in self.test_results:
            final_validation = self.test_results["final_validation"]
            if "recommendations" in final_validation:
                report["recommendations"].extend(final_validation["recommendations"])
        
        # Save report
        with open('ultimate_system_test_report.json', 'w') as f:
            json.dump(report, f, indent=2)
        
        # Print summary
        print(f"\n{'='*120}")
        print("📊 ULTIMATE SYSTEM TEST REPORT")
        print(f"{'='*120}")
        
        print(f"⏱️  Total Test Time: {report['test_summary']['total_test_time']:.2f} seconds")
        print(f"🏥 Overall System Status: {report['test_summary']['overall_system_status']}")
        print(f"📈 Total Operations: {total_operations:,}")
        print(f"❌ Total Errors: {total_errors:,}")
        print(f"💥 Total Chaos Events: {total_chaos_events:,}")
        print(f"🔄 Total Recovery Events: {total_recovery_events:,}")
        print(f"📊 Error Rate: {report['performance_summary']['error_rate']:.2f}%")
        print(f"🛡️  Recovery Rate: {report['performance_summary']['recovery_rate']:.2f}%")
        
        print(f"\n🔍 DETAILED RESULTS BY TEST SUITE:")
        for suite in self.test_suites:
            if suite.lower().replace("_", " ") in self.test_results:
                suite_key = suite.lower().replace("_", " ")
                print(f"\n📋 {suite}:")
                suite_results = self.test_results[suite_key]
                if isinstance(suite_results, dict):
                    for key, value in suite_results.items():
                        if isinstance(value, (int, float)):
                            print(f"   {key}: {value:,}")
                        elif isinstance(value, list):
                            print(f"   {key}: {len(value)} items")
                        elif isinstance(value, dict):
                            print(f"   {key}: {len(value)} sub-items")
                        else:
                            print(f"   {key}: {value}")
        
        print(f"\n💡 RECOMMENDATIONS:")
        for recommendation in report['recommendations']:
            print(f"   • {recommendation}")
        
        print(f"\n✅ Report saved to: ultimate_system_test_report.json")
        print(f"{'='*120}")

def main():
    """Main function"""
    print("🚀 ULTIMATE SYSTEM TESTER - HAK/GAL SYSTEM")
    print("Kombiniert alle Tests für maximale Komplexität...")
    
    tester = UltimateSystemTester()
    results = tester.run_ultimate_system_test()
    
    print("\n🎉 ULTIMATE SYSTEM TEST COMPLETED!")
    print("Check ultimate_system_test_report.json for detailed results")

if __name__ == "__main__":
    main()
