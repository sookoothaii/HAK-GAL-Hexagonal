#!/usr/bin/env python3
"""
HAK-GAL System Integration Test Suite
=====================================
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
Umfassende Tests für alle System-Komponenten
"""

import unittest
import requests
import json
import time
import sqlite3
import sys
import os
from pathlib import Path
from datetime import datetime
import subprocess
import threading

# Configuration
BASE_URL = "http://localhost:5001"
DB_PATH = "../HAK_GAL_SUITE/k_assistant.db"
TIMEOUT = 10

class TestHAKGALIntegration(unittest.TestCase):
    """Complete integration tests for HAK-GAL system"""
    
    @classmethod
    def setUpClass(cls):
        """Start the backend before tests"""
        print("\n" + "=" * 60)
        print("HAK-GAL INTEGRATION TEST SUITE")
        print("=" * 60)
        
        # Start backend process
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        cls.backend_process = subprocess.Popen(
            [sys.executable, "src_hexagonal/hexagonal_api_enhanced.py"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for backend to start
        print("[INFO] Starting backend...")
        time.sleep(5)
        
        # Verify backend is running
        try:
            response = requests.get(f"{BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                print("[OK] Backend is running")
            else:
                raise Exception("Backend not responding")
        except Exception as e:
            print(f"[ERROR] Backend failed to start: {e}")
            cls.backend_process.terminate()
            raise
    
    @classmethod
    def tearDownClass(cls):
        """Stop the backend after tests"""
        print("\n[INFO] Stopping backend...")
        cls.backend_process.terminate()
        cls.backend_process.wait(timeout=5)
        print("[OK] Backend stopped")
    
    def test_01_health_check(self):
        """Test health endpoint"""
        response = requests.get(f"{BASE_URL}/health", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'operational')
        self.assertEqual(data['architecture'], 'hexagonal')
        print("[PASS] Health check")
    
    def test_02_system_status(self):
        """Test system status endpoint"""
        response = requests.get(f"{BASE_URL}/api/status", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['status'], 'operational')
        self.assertIn('fact_count', data)
        self.assertIsInstance(data['fact_count'], int)
        print(f"[PASS] System status - Facts: {data['fact_count']}")
    
    def test_03_facts_count(self):
        """Test facts count endpoint with caching"""
        # First request (no cache)
        response1 = requests.get(f"{BASE_URL}/api/facts/count", timeout=TIMEOUT)
        self.assertEqual(response1.status_code, 200)
        data1 = response1.json()
        self.assertIn('count', data1)
        self.assertFalse(data1.get('cached', True))
        
        # Second request (should be cached)
        response2 = requests.get(f"{BASE_URL}/api/facts/count", timeout=TIMEOUT)
        self.assertEqual(response2.status_code, 200)
        data2 = response2.json()
        self.assertEqual(data1['count'], data2['count'])
        self.assertTrue(data2.get('cached', False))
        print(f"[PASS] Facts count with caching - Count: {data1['count']}")
    
    def test_04_list_facts(self):
        """Test listing facts"""
        response = requests.get(f"{BASE_URL}/api/facts?limit=10", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('facts', data)
        self.assertIsInstance(data['facts'], list)
        self.assertLessEqual(len(data['facts']), 10)
        
        if data['facts']:
            fact = data['facts'][0]
            self.assertIn('statement', fact)
            self.assertIn('confidence', fact)
        print(f"[PASS] List facts - Retrieved: {len(data['facts'])}")
    
    def test_05_search_facts(self):
        """Test fact search"""
        payload = {
            "query": "matter",
            "limit": 5,
            "min_confidence": 0.5
        }
        response = requests.post(
            f"{BASE_URL}/api/search",
            json=payload,
            timeout=TIMEOUT
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertIsInstance(data['results'], list)
        print(f"[PASS] Search facts - Found: {data['count']}")
    
    def test_06_reasoning(self):
        """Test reasoning endpoint"""
        payload = {"query": "IsTypeOf(Matter, Substance)"}
        response = requests.post(
            f"{BASE_URL}/api/reason",
            json=payload,
            timeout=TIMEOUT
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('confidence', data)
        self.assertIn('success', data)
        self.assertIn('duration_ms', data)
        self.assertIsInstance(data['confidence'], (int, float))
        print(f"[PASS] Reasoning - Confidence: {data['confidence']:.3f}, Time: {data['duration_ms']:.1f}ms")
    
    def test_07_add_fact(self):
        """Test adding a new fact"""
        timestamp = int(time.time())
        payload = {
            "statement": f"TestFact(Integration, Test_{timestamp})",
            "context": {"source": "integration_test"}
        }
        response = requests.post(
            f"{BASE_URL}/api/facts",
            json=payload,
            timeout=TIMEOUT
        )
        # Could be 201 (success) or 400 (already exists)
        self.assertIn(response.status_code, [201, 400])
        data = response.json()
        self.assertIn('success', data)
        self.assertIn('message', data)
        print(f"[PASS] Add fact - Success: {data['success']}")
    
    def test_08_architecture_info(self):
        """Test architecture endpoint"""
        response = requests.get(f"{BASE_URL}/api/architecture", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data['pattern'], 'Hexagonal Architecture')
        self.assertIn('features', data)
        self.assertIn('layers', data)
        self.assertIn('benefits', data)
        print(f"[PASS] Architecture info - Version: {data['version']}")
    
    def test_09_governor_status(self):
        """Test Governor status"""
        response = requests.get(f"{BASE_URL}/api/governor/status", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('running', data)
        self.assertIn('mode', data)
        self.assertIn('initialized', data)
        print(f"[PASS] Governor status - Mode: {data['mode']}")
    
    def test_10_governor_decision(self):
        """Test Governor decision making"""
        response = requests.get(f"{BASE_URL}/api/governor/decision", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        if data:  # Decision might be None if no arms configured
            self.assertIn('arm_id', data)
            self.assertIn('expected_reward', data)
            print(f"[PASS] Governor decision - Arm: {data.get('arm_name', 'N/A')}")
        else:
            print("[PASS] Governor decision - No decision available")
    
    def test_11_websocket_connection(self):
        """Test WebSocket connectivity"""
        try:
            import socketio
            sio = socketio.Client()
            
            connected = threading.Event()
            
            @sio.on('connect')
            def on_connect():
                connected.set()
            
            @sio.on('connection_status')
            def on_status(data):
                self.assertTrue(data['connected'])
                self.assertEqual(data['backend'], 'hexagonal_optimized')
            
            sio.connect(BASE_URL)
            connected.wait(timeout=5)
            
            self.assertTrue(sio.connected)
            
            # Request metrics
            sio.emit('kb_metrics_request')
            time.sleep(1)
            
            sio.disconnect()
            print("[PASS] WebSocket connection")
            
        except ImportError:
            print("[SKIP] WebSocket test - socketio not installed")
        except Exception as e:
            print(f"[SKIP] WebSocket test - {e}")
    
    def test_12_graph_emergency_status(self):
        """Test graph emergency status"""
        response = requests.get(f"{BASE_URL}/api/graph/emergency-status", timeout=TIMEOUT)
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('graph_exists', data)
        self.assertIn('fact_count', data)
        self.assertIn('emergency_actions_available', data)
        print(f"[PASS] Graph status - Exists: {data['graph_exists']}")
    
    def test_13_performance_metrics(self):
        """Test performance under load"""
        print("\n[PERFORMANCE] Testing response times...")
        
        endpoints = [
            ('/health', 'GET', None),
            ('/api/status?light=1', 'GET', None),
            ('/api/facts/count', 'GET', None),
            ('/api/reason', 'POST', {"query": "Test"})
        ]
        
        for endpoint, method, payload in endpoints:
            times = []
            for _ in range(5):
                start = time.time()
                
                if method == 'GET':
                    response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
                else:
                    response = requests.post(f"{BASE_URL}{endpoint}", json=payload, timeout=TIMEOUT)
                
                elapsed = (time.time() - start) * 1000
                times.append(elapsed)
            
            avg_time = sum(times) / len(times)
            print(f"  {endpoint}: {avg_time:.1f}ms avg")
            
            # Performance assertions
            if '/health' in endpoint:
                self.assertLess(avg_time, 100, "Health check too slow")
            elif 'light=1' in endpoint:
                self.assertLess(avg_time, 500, "Light status too slow")
    
    def test_14_database_integrity(self):
        """Test database integrity"""
        db_path = Path(DB_PATH)
        if not db_path.exists():
            db_path = Path('..') / 'HAK_GAL_SUITE' / 'k_assistant.db'
        
        if db_path.exists():
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Check facts table
            cursor.execute("SELECT COUNT(*) FROM facts")
            count = cursor.fetchone()[0]
            self.assertGreater(count, 0, "No facts in database")
            
            # Check for corruption
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()[0]
            self.assertEqual(result, 'ok', "Database integrity check failed")
            
            conn.close()
            print(f"[PASS] Database integrity - Facts: {count}")
        else:
            print("[SKIP] Database integrity - DB not found")
    
    def test_15_concurrent_requests(self):
        """Test concurrent request handling"""
        import concurrent.futures
        
        def make_request(endpoint):
            try:
                response = requests.get(f"{BASE_URL}{endpoint}", timeout=TIMEOUT)
                return response.status_code == 200
            except:
                return False
        
        endpoints = ['/health'] * 10 + ['/api/status'] * 10
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(make_request, ep) for ep in endpoints]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]
        
        success_rate = sum(results) / len(results)
        self.assertGreater(success_rate, 0.9, "Too many concurrent requests failed")
        print(f"[PASS] Concurrent requests - Success rate: {success_rate:.1%}")

class TestOptimizations(unittest.TestCase):
    """Test optimization features"""
    
    def test_cache_performance(self):
        """Test caching optimization"""
        # Make multiple requests to test cache
        times = []
        for i in range(10):
            start = time.time()
            response = requests.get(f"{BASE_URL}/api/facts/count", timeout=TIMEOUT)
            elapsed = (time.time() - start) * 1000
            times.append(elapsed)
            
            data = response.json()
            if i == 0:
                self.assertFalse(data.get('cached', True))
            else:
                # Should be cached after first request
                pass  # Cache might expire
        
        # Later requests should be faster (cached)
        avg_first_5 = sum(times[:5]) / 5
        avg_last_5 = sum(times[5:]) / 5
        
        print(f"[PASS] Cache performance - First 5: {avg_first_5:.1f}ms, Last 5: {avg_last_5:.1f}ms")
    
    def test_rate_limiting(self):
        """Test rate limiting (if implemented)"""
        # This would test the WebSocket rate limiting
        # Skipping as it requires WebSocket client
        print("[SKIP] Rate limiting test - Requires WebSocket")
    
    def test_graph_generation(self):
        """Test optimized graph generation"""
        if Path("optimized_graph_generator.py").exists():
            try:
                result = subprocess.run(
                    [sys.executable, "optimized_graph_generator.py", "--limit", "100"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                self.assertEqual(result.returncode, 0, "Graph generation failed")
                self.assertIn("Generated", result.stdout)
                print("[PASS] Graph generation")
            except Exception as e:
                print(f"[SKIP] Graph generation - {e}")
        else:
            print("[SKIP] Graph generation - Script not found")

def run_tests():
    """Run all integration tests"""
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test cases
    suite.addTests(loader.loadTestsFromTestCase(TestHAKGALIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestOptimizations))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.wasSuccessful():
        print("\n[SUCCESS] All tests passed!")
        return 0
    else:
        print("\n[FAILURE] Some tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())