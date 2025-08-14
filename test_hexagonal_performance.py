#!/usr/bin/env python3
"""
HAK-GAL Hexagonal API Performance Test
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import requests
import time
import json
import sys
from datetime import datetime
from typing import Dict, List, Tuple

# Configuration
API_URL = "http://127.0.0.1:5001"
ORIGINAL_API_URL = "http://127.0.0.1:5000"

class HexagonalAPITester:
    """Comprehensive API Performance Tester"""
    
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.results = []
        self.start_time = time.time()
        
    def log(self, message: str, status: str = "INFO"):
        """Log with timestamp"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        status_emoji = {
            "INFO": "ℹ️",
            "SUCCESS": "✅",
            "WARNING": "⚠️",
            "ERROR": "❌",
            "TEST": "🧪"
        }.get(status, "📝")
        
        print(f"[{timestamp}] {status_emoji} {message}")
        
    def measure_request(self, method: str, endpoint: str, data: Dict = None) -> Tuple[bool, float, Dict]:
        """Measure single request performance"""
        url = f"{self.base_url}{endpoint}"
        
        try:
            start = time.time()
            
            if method == "GET":
                response = requests.get(url)
            elif method == "POST":
                response = requests.post(url, json=data)
            else:
                raise ValueError(f"Unsupported method: {method}")
                
            duration_ms = (time.time() - start) * 1000
            
            success = response.status_code in [200, 201]
            result = response.json() if response.content else {}
            
            return success, duration_ms, result
            
        except Exception as e:
            self.log(f"Request failed: {e}", "ERROR")
            return False, 0, {"error": str(e)}
    
    def test_health_check(self):
        """Test /health endpoint"""
        self.log("Testing Health Check...", "TEST")
        
        success, duration, result = self.measure_request("GET", "/health")
        
        if success:
            self.log(f"Health Check: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Architecture: {result.get('architecture')}")
            self.log(f"  WebSocket: {result.get('websocket')}")
            self.log(f"  Governor: {result.get('governor')}")
        else:
            self.log("Health Check failed", "ERROR")
            
        self.results.append({
            "endpoint": "/health",
            "duration_ms": duration,
            "success": success
        })
        
        return success
    
    def test_system_status(self):
        """Test /api/status endpoint"""
        self.log("Testing System Status...", "TEST")
        
        success, duration, result = self.measure_request("GET", "/api/status")
        
        if success:
            self.log(f"System Status: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Facts: {result.get('fact_count', 0)}")
            self.log(f"  Device: {result.get('device', 'unknown')}")
            if 'governor' in result:
                self.log(f"  Governor Running: {result['governor'].get('running')}")
        else:
            self.log("System Status failed", "ERROR")
            
        self.results.append({
            "endpoint": "/api/status",
            "duration_ms": duration,
            "success": success,
            "fact_count": result.get('fact_count', 0)
        })
        
        return success
    
    def test_facts_list(self, limit: int = 10):
        """Test /api/facts GET endpoint"""
        self.log(f"Testing Facts List (limit={limit})...", "TEST")
        
        success, duration, result = self.measure_request("GET", f"/api/facts?limit={limit}")
        
        if success:
            self.log(f"Facts List: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Retrieved: {result.get('count', 0)} facts")
            self.log(f"  Total in DB: {result.get('total', 0)}")
            
            # Show sample fact
            if result.get('facts'):
                sample = result['facts'][0]
                self.log(f"  Sample: {sample.get('statement', 'N/A')[:50]}...")
        else:
            self.log("Facts List failed", "ERROR")
            
        self.results.append({
            "endpoint": "/api/facts",
            "duration_ms": duration,
            "success": success,
            "facts_retrieved": result.get('count', 0)
        })
        
        return success
    
    def test_reasoning(self, query: str = "IsTypeOf(Water, Substance)"):
        """Test /api/reason POST endpoint"""
        self.log(f"Testing Reasoning: {query}", "TEST")
        
        success, duration, result = self.measure_request("POST", "/api/reason", {"query": query})
        
        if success:
            self.log(f"Reasoning: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Confidence: {result.get('confidence', 0):.4f}")
            self.log(f"  High Confidence: {result.get('high_confidence', False)}")
            self.log(f"  Device: {result.get('device', 'unknown')}")
            self.log(f"  Internal Duration: {result.get('duration_ms', 0):.2f}ms")
        else:
            self.log("Reasoning failed", "ERROR")
            
        self.results.append({
            "endpoint": "/api/reason",
            "duration_ms": duration,
            "success": success,
            "confidence": result.get('confidence', 0)
        })
        
        return success
    
    def test_search(self, query: str = "Water"):
        """Test /api/search POST endpoint"""
        self.log(f"Testing Search: {query}", "TEST")
        
        data = {
            "query": query,
            "limit": 5,
            "min_confidence": 0.5
        }
        
        success, duration, result = self.measure_request("POST", "/api/search", data)
        
        if success:
            self.log(f"Search: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Results: {result.get('count', 0)}")
            
            # Show first result
            if result.get('results'):
                first = result['results'][0]
                self.log(f"  First: {first.get('statement', 'N/A')[:50]}...")
        else:
            self.log("Search failed", "ERROR")
            
        self.results.append({
            "endpoint": "/api/search",
            "duration_ms": duration,
            "success": success,
            "results": result.get('count', 0)
        })
        
        return success
    
    def test_add_fact(self):
        """Test /api/facts POST endpoint"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        test_fact = f"TestFact(PerformanceTest_{timestamp}, Hexagonal)."
        
        self.log(f"Testing Add Fact: {test_fact}", "TEST")
        
        data = {
            "statement": test_fact,
            "context": {"source": "performance_test"}
        }
        
        success, duration, result = self.measure_request("POST", "/api/facts", data)
        
        if success:
            self.log(f"Add Fact: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Success: {result.get('success', False)}")
            self.log(f"  Message: {result.get('message', 'N/A')}")
        else:
            self.log("Add Fact failed", "ERROR")
            
        self.results.append({
            "endpoint": "/api/facts (POST)",
            "duration_ms": duration,
            "success": success
        })
        
        return success
    
    def test_governor_endpoints(self):
        """Test Governor-specific endpoints"""
        self.log("Testing Governor Endpoints...", "TEST")
        
        # Test Governor Status
        success, duration, result = self.measure_request("GET", "/api/governor/status")
        
        if success:
            self.log(f"Governor Status: {duration:.2f}ms", "SUCCESS")
            self.log(f"  Running: {result.get('running', False)}")
            self.log(f"  Mode: {result.get('mode', 'unknown')}")
            self.log(f"  Decisions Made: {result.get('decisions_made', 0)}")
            
            self.results.append({
                "endpoint": "/api/governor/status",
                "duration_ms": duration,
                "success": success
            })
            
            # Test Governor Metrics
            success, duration, result = self.measure_request("GET", "/api/governor/metrics")
            
            if success:
                self.log(f"Governor Metrics: {duration:.2f}ms", "SUCCESS")
                ts = result.get('thompson_sampling', {})
                self.log(f"  Alpha: {ts.get('alpha', 0):.2f}")
                self.log(f"  Beta: {ts.get('beta', 0):.2f}")
                
                self.results.append({
                    "endpoint": "/api/governor/metrics",
                    "duration_ms": duration,
                    "success": success
                })
        else:
            self.log("Governor endpoints not available", "WARNING")
    
    def run_stress_test(self, endpoint: str = "/api/reason", requests_count: int = 10):
        """Run stress test on specific endpoint"""
        self.log(f"Running Stress Test: {requests_count} requests to {endpoint}", "TEST")
        
        durations = []
        successes = 0
        
        test_data = {"query": "IsTypeOf(Water, Substance)"} if "reason" in endpoint else None
        
        for i in range(requests_count):
            success, duration, _ = self.measure_request(
                "POST" if test_data else "GET", 
                endpoint, 
                test_data
            )
            
            if success:
                successes += 1
                durations.append(duration)
            
            # Small delay to avoid overwhelming
            time.sleep(0.01)
        
        if durations:
            avg_duration = sum(durations) / len(durations)
            min_duration = min(durations)
            max_duration = max(durations)
            
            self.log(f"Stress Test Complete:", "SUCCESS")
            self.log(f"  Success Rate: {successes}/{requests_count} ({successes*100/requests_count:.1f}%)")
            self.log(f"  Avg Duration: {avg_duration:.2f}ms")
            self.log(f"  Min Duration: {min_duration:.2f}ms")
            self.log(f"  Max Duration: {max_duration:.2f}ms")
        else:
            self.log("Stress Test failed - no successful requests", "ERROR")
    
    def generate_report(self):
        """Generate performance report"""
        print("\n" + "="*60)
        print("📊 PERFORMANCE TEST REPORT")
        print("="*60)
        
        total_tests = len(self.results)
        successful_tests = sum(1 for r in self.results if r['success'])
        
        print(f"✅ Success Rate: {successful_tests}/{total_tests} ({successful_tests*100/total_tests:.1f}%)")
        
        # Calculate average durations by endpoint
        endpoint_stats = {}
        for result in self.results:
            endpoint = result['endpoint']
            if endpoint not in endpoint_stats:
                endpoint_stats[endpoint] = []
            endpoint_stats[endpoint].append(result['duration_ms'])
        
        print("\n📈 Performance by Endpoint:")
        for endpoint, durations in endpoint_stats.items():
            avg = sum(durations) / len(durations)
            print(f"  {endpoint}: {avg:.2f}ms avg")
        
        # Overall stats
        all_durations = [r['duration_ms'] for r in self.results if r['success']]
        if all_durations:
            print(f"\n⚡ Overall Performance:")
            print(f"  Average: {sum(all_durations)/len(all_durations):.2f}ms")
            print(f"  Min: {min(all_durations):.2f}ms")
            print(f"  Max: {max(all_durations):.2f}ms")
        
        total_time = time.time() - self.start_time
        print(f"\n⏱️ Total Test Time: {total_time:.2f}s")
        print("="*60)

def main():
    """Main test execution"""
    print("="*60)
    print("🧪 HAK-GAL HEXAGONAL API PERFORMANCE TEST")
    print("="*60)
    print(f"Target: {API_URL}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)
    
    tester = HexagonalAPITester()
    
    # Basic functionality tests
    if not tester.test_health_check():
        print("\n❌ API not responding. Is the server running?")
        sys.exit(1)
    
    tester.test_system_status()
    tester.test_facts_list()
    tester.test_reasoning()
    tester.test_search()
    tester.test_add_fact()
    tester.test_governor_endpoints()
    
    # Stress test on reasoning endpoint
    print("\n" + "="*60)
    tester.run_stress_test("/api/reason", 20)
    
    # Generate report
    tester.generate_report()
    
    # Compare with Original if available
    print("\n📊 COMPARISON TEST (Optional)")
    print("="*60)
    
    try:
        original_tester = HexagonalAPITester(ORIGINAL_API_URL)
        original_success, original_duration, _ = original_tester.measure_request("GET", "/health")
        hex_success, hex_duration, _ = tester.measure_request("GET", "/health")
        
        if original_success and hex_success:
            print(f"✅ Original API: {original_duration:.2f}ms")
            print(f"✅ Hexagonal API: {hex_duration:.2f}ms")
            
            if hex_duration < original_duration:
                improvement = ((original_duration - hex_duration) / original_duration) * 100
                print(f"🚀 Hexagonal is {improvement:.1f}% faster!")
            else:
                slower = ((hex_duration - original_duration) / original_duration) * 100
                print(f"⚠️ Hexagonal is {slower:.1f}% slower")
    except:
        print("ℹ️ Original API not available for comparison")

if __name__ == "__main__":
    main()
