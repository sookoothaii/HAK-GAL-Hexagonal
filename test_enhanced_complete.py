#!/usr/bin/env python3
"""
Complete Test Suite for Enhanced Hexagonal Architecture
========================================================
Nach HAK/GAL Verfassung Artikel 6: Empirische Validierung
"""

import requests
import json
import time
from typing import Dict, Any

# Configuration
BASE_URL = "http://127.0.0.1:5001"
ORIGINAL_URL = "http://127.0.0.1:5000"

class Colors:
    """ANSI color codes for terminal output"""
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(title: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{title}{Colors.END}")
    print(f"{Colors.BOLD}{'=' * 60}{Colors.END}")

def print_test(name: str, passed: bool, message: str = ""):
    """Print test result"""
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"  {name}: {status} {message}")

def test_basic_api():
    """Test basic API functionality"""
    print_header("1. BASIC API TESTS")
    
    results = {}
    
    # Health Check
    try:
        resp = requests.get(f"{BASE_URL}/health", timeout=5)
        data = resp.json()
        passed = resp.status_code == 200 and data.get('status') == 'healthy'
        print_test("Health Check", passed)
        
        # Check features
        print(f"    WebSocket: {data.get('websocket', False)}")
        print(f"    Governor: {data.get('governor', False)}")
        print(f"    Monitoring: {data.get('monitoring', False)}")
        
        results['health'] = passed
        results['websocket'] = data.get('websocket', False)
        results['governor'] = data.get('governor', False)
        
    except Exception as e:
        print_test("Health Check", False, f"Error: {e}")
        results['health'] = False
    
    # Facts Count
    try:
        resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
        data = resp.json()
        fact_count = data.get('fact_count', 0)
        passed = fact_count == 3080
        print_test("Facts Count", passed, f"(got {fact_count})")
        results['facts_count'] = passed
    except Exception as e:
        print_test("Facts Count", False, f"Error: {e}")
        results['facts_count'] = False
    
    # HRM Reasoning
    try:
        resp = requests.post(
            f"{BASE_URL}/api/reason",
            json={"query": "HasTrait(Mammalia,ProducesMilk)"},
            timeout=10
        )
        data = resp.json()
        confidence = data.get('confidence', 0)
        device = data.get('device', 'unknown')
        duration = data.get('duration_ms', 0)
        
        passed = confidence > 0.9 and 'cuda' in device.lower()
        print_test("HRM Reasoning", passed, 
                  f"(conf={confidence:.4f}, device={device}, {duration:.1f}ms)")
        results['reasoning'] = passed
    except Exception as e:
        print_test("HRM Reasoning", False, f"Error: {e}")
        results['reasoning'] = False
    
    return results

def test_governor():
    """Test Governor functionality"""
    print_header("2. GOVERNOR TESTS")
    
    results = {}
    
    # Governor Status
    try:
        resp = requests.get(f"{BASE_URL}/api/governor/status", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            running = data.get('running', False)
            mode = data.get('mode', 'unknown')
            
            print_test("Governor Status", True, 
                      f"(running={running}, mode={mode})")
            results['status'] = True
            
            # Governor Metrics
            resp = requests.get(f"{BASE_URL}/api/governor/metrics", timeout=5)
            if resp.status_code == 200:
                metrics = resp.json()
                alpha = metrics.get('thompson_sampling', {}).get('alpha', 0)
                beta = metrics.get('thompson_sampling', {}).get('beta', 0)
                
                print_test("Governor Metrics", True, 
                          f"(α={alpha:.2f}, β={beta:.2f})")
                results['metrics'] = True
            else:
                print_test("Governor Metrics", False)
                results['metrics'] = False
            
            # Governor Decision
            resp = requests.get(f"{BASE_URL}/api/governor/decision", timeout=5)
            if resp.status_code == 200:
                decision = resp.json()
                action = decision.get('action', 'none')
                confidence = decision.get('confidence', 0)
                
                print_test("Governor Decision", True, 
                          f"(action={action}, conf={confidence:.2f})")
                results['decision'] = True
            else:
                print_test("Governor Decision", False)
                results['decision'] = False
                
        else:
            print_test("Governor Status", False, "Not available")
            results['status'] = False
            
    except Exception as e:
        print_test("Governor", False, f"Error: {e}")
        results['status'] = False
    
    return results

def test_websocket():
    """Test WebSocket connectivity"""
    print_header("3. WEBSOCKET TESTS")
    
    results = {}
    
    try:
        import socketio
        
        # Create Socket.IO client
        sio = socketio.Client()
        connected = False
        received_events = []
        
        @sio.on('connect')
        def on_connect():
            nonlocal connected
            connected = True
            print_test("WebSocket Connection", True)
        
        @sio.on('kb_update')
        def on_kb_update(data):
            received_events.append('kb_update')
        
        @sio.on('system_status')
        def on_system_status(data):
            received_events.append('system_status')
        
        # Try to connect
        try:
            sio.connect(BASE_URL)
            time.sleep(2)  # Wait for events
            
            if connected:
                print_test("WebSocket Events", len(received_events) > 0, 
                          f"(received {len(received_events)} events)")
                results['connected'] = True
                results['events'] = len(received_events)
            else:
                print_test("WebSocket Connection", False)
                results['connected'] = False
                
            sio.disconnect()
            
        except Exception as e:
            print_test("WebSocket Connection", False, f"Error: {e}")
            results['connected'] = False
            
    except ImportError:
        print_test("WebSocket", False, "socketio not installed")
        print("    Run: pip install python-socketio[client]")
        results['connected'] = False
    
    return results

def test_architecture():
    """Test architecture endpoint"""
    print_header("4. ARCHITECTURE INFO")
    
    try:
        resp = requests.get(f"{BASE_URL}/api/architecture", timeout=5)
        if resp.status_code == 200:
            data = resp.json()
            version = data.get('version', '1.0')
            features = data.get('features', {})
            
            print(f"  Version: {version}")
            print(f"  Features:")
            for feature, enabled in features.items():
                status = "✅" if enabled else "❌"
                print(f"    {status} {feature}: {enabled}")
            
            return True
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def test_performance():
    """Test API performance"""
    print_header("5. PERFORMANCE TESTS")
    
    # Reasoning performance
    queries = [
        "HasTrait(Mammalia,ProducesMilk)",
        "IsTypeOf(NeuralNetwork,MachineLearning)",
        "PartOf(CPU,Computer)"
    ]
    
    total_time = 0
    for query in queries:
        try:
            start = time.time()
            resp = requests.post(
                f"{BASE_URL}/api/reason",
                json={"query": query},
                timeout=10
            )
            duration = (time.time() - start) * 1000
            total_time += duration
            
            if resp.status_code == 200:
                data = resp.json()
                api_duration = data.get('duration_ms', duration)
                print(f"  {query[:30]}... : {api_duration:.1f}ms")
        except:
            print(f"  {query[:30]}... : FAILED")
    
    avg_time = total_time / len(queries)
    print(f"\n  Average Response Time: {avg_time:.1f}ms")
    print_test("Performance", avg_time < 100, 
              "Target: <100ms" if avg_time < 100 else "Too slow!")
    
    return avg_time < 100

def compare_with_original():
    """Compare Hexagonal with Original API"""
    print_header("6. COMPARISON WITH ORIGINAL")
    
    try:
        # Get Original status
        orig_resp = requests.get(f"{ORIGINAL_URL}/api/knowledge-base/status", timeout=5)
        if orig_resp.status_code == 200:
            orig_data = orig_resp.json()
            orig_facts = orig_data.get('total_facts', 0)
        else:
            orig_facts = "N/A"
    except:
        orig_facts = "Not running"
    
    try:
        # Get Hexagonal status
        hex_resp = requests.get(f"{BASE_URL}/api/status", timeout=5)
        if hex_resp.status_code == 200:
            hex_data = hex_resp.json()
            hex_facts = hex_data.get('fact_count', 0)
        else:
            hex_facts = "N/A"
    except:
        hex_facts = "Not running"
    
    print(f"  Original (5000): {orig_facts} facts")
    print(f"  Hexagonal (5001): {hex_facts} facts")
    
    if hex_facts == 3080:
        print(f"  {Colors.GREEN}✅ Hexagonal working correctly!{Colors.END}")
        return True
    else:
        print(f"  {Colors.YELLOW}⚠️ Check hexagonal facts count{Colors.END}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print(f"{Colors.BOLD}{Colors.BLUE}")
    print("╔══════════════════════════════════════════════════════════╗")
    print("║   HAK-GAL HEXAGONAL ARCHITECTURE v2.0 - TEST SUITE      ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}")
    
    all_results = {}
    
    # Run tests
    all_results['basic'] = test_basic_api()
    all_results['governor'] = test_governor()
    all_results['websocket'] = test_websocket()
    all_results['architecture'] = test_architecture()
    all_results['performance'] = test_performance()
    all_results['comparison'] = compare_with_original()
    
    # Summary
    print_header("TEST SUMMARY")
    
    # Count successes
    basic_pass = sum(1 for v in all_results['basic'].values() if v)
    governor_pass = sum(1 for v in all_results.get('governor', {}).values() if v)
    websocket_pass = 1 if all_results.get('websocket', {}).get('connected') else 0
    
    total_tests = len(all_results['basic']) + len(all_results.get('governor', {})) + 3
    total_passed = basic_pass + governor_pass + websocket_pass + \
                  (1 if all_results['architecture'] else 0) + \
                  (1 if all_results['performance'] else 0) + \
                  (1 if all_results['comparison'] else 0)
    
    print(f"  Total Tests: {total_tests}")
    print(f"  Passed: {Colors.GREEN}{total_passed}{Colors.END}")
    print(f"  Failed: {Colors.RED}{total_tests - total_passed}{Colors.END}")
    
    success_rate = (total_passed / total_tests) * 100
    
    if success_rate >= 80:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ HEXAGONAL ARCHITECTURE READY! ({success_rate:.1f}%){Colors.END}")
    elif success_rate >= 60:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️ PARTIALLY READY ({success_rate:.1f}%){Colors.END}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ NEEDS WORK ({success_rate:.1f}%){Colors.END}")
    
    # Recommendations
    if not all_results.get('websocket', {}).get('connected'):
        print(f"\n{Colors.YELLOW}💡 Tip: Install python-socketio[client] for WebSocket tests{Colors.END}")
    
    if not all_results.get('governor', {}).get('status'):
        print(f"\n{Colors.YELLOW}💡 Tip: Governor may need legacy system connection{Colors.END}")

if __name__ == "__main__":
    run_all_tests()
