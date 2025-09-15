#!/usr/bin/env python3
"""
PERFORMANCE DEBUGGER - Findet die 1-Sekunden-Verzögerung
"""

import time
import requests
import threading
from datetime import datetime

class PerformanceDebugger:
    def __init__(self):
        self.results = []
        self.lock = threading.Lock()
    
    def test_endpoint(self, url, name, iterations=10):
        """Teste einen Endpoint mehrfach und messe die Zeit"""
        print(f"\n🔍 Testing {name}: {url}")
        print("-" * 50)
        
        times = []
        
        for i in range(iterations):
            start_time = time.time()
            
            try:
                response = requests.get(url, timeout=10)
                end_time = time.time()
                
                response_time = (end_time - start_time) * 1000
                times.append(response_time)
                
                print(f"Request {i+1:2d}: {response_time:6.2f}ms (Status: {response.status_code})")
                
                # Prüfe auf Cache-Header
                if 'X-From-Cache' in response.headers:
                    cache_status = response.headers['X-From-Cache']
                    print(f"         Cache: {cache_status}")
                
            except Exception as e:
                print(f"Request {i+1:2d}: ERROR - {e}")
                times.append(9999)  # Markiere als Fehler
        
        # Statistiken
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n📊 {name} Statistics:")
            print(f"   Average: {avg_time:6.2f}ms")
            print(f"   Minimum: {min_time:6.2f}ms")
            print(f"   Maximum: {max_time:6.2f}ms")
            
            # Prüfe auf 1-Sekunden-Delay
            if avg_time > 900:  # >900ms
                print(f"   ⚠️  WARNING: Average response time >900ms!")
            if max_time > 1000:  # >1000ms
                print(f"   ❌ CRITICAL: Maximum response time >1000ms!")
            
            with self.lock:
                self.results.append({
                    'name': name,
                    'url': url,
                    'avg_time': avg_time,
                    'min_time': min_time,
                    'max_time': max_time,
                    'times': times
                })
    
    def test_all_servers(self):
        """Teste alle verfügbaren Server"""
        print("🚀 PERFORMANCE DEBUGGER - 1-SECOND DELAY DETECTION")
        print("=" * 60)
        
        # Teste verschiedene Server
        servers = [
            {
                'name': 'Minimal Test Server',
                'urls': [
                    'http://127.0.0.1:5555/',
                    'http://127.0.0.1:5555/api/health',
                    'http://127.0.0.1:5555/api/metrics',
                    'http://127.0.0.1:5555/test'
                ]
            },
            {
                'name': 'HAK/GAL Dashboard Ultra',
                'urls': [
                    'http://127.0.0.1:5000/',
                    'http://127.0.0.1:5000/api/health',
                    'http://127.0.0.1:5000/api/metrics'
                ]
            },
            {
                'name': 'Original Dashboard',
                'urls': [
                    'http://127.0.0.1:5000/api/health',
                    'http://127.0.0.1:5000/api/metrics'
                ]
            }
        ]
        
        for server in servers:
            print(f"\n🌐 Testing {server['name']}")
            print("=" * 60)
            
            for url in server['urls']:
                try:
                    # Prüfe ob Server erreichbar ist
                    test_response = requests.get(url, timeout=2)
                    if test_response.status_code == 200:
                        self.test_endpoint(url, f"{server['name']} - {url.split('/')[-1] or 'root'}")
                    else:
                        print(f"❌ Server not responding: {url}")
                except requests.exceptions.ConnectionError:
                    print(f"❌ Server not reachable: {url}")
                except Exception as e:
                    print(f"❌ Error testing {url}: {e}")
    
    def analyze_results(self):
        """Analysiere die Testergebnisse"""
        print("\n" + "=" * 60)
        print("📊 PERFORMANCE ANALYSIS")
        print("=" * 60)
        
        if not self.results:
            print("❌ No test results available")
            return
        
        # Sortiere nach durchschnittlicher Antwortzeit
        sorted_results = sorted(self.results, key=lambda x: x['avg_time'])
        
        print(f"\n🏆 FASTEST ENDPOINTS:")
        for i, result in enumerate(sorted_results[:3]):
            print(f"   {i+1}. {result['name']}: {result['avg_time']:.2f}ms")
        
        print(f"\n🐌 SLOWEST ENDPOINTS:")
        for i, result in enumerate(sorted_results[-3:]):
            print(f"   {i+1}. {result['name']}: {result['avg_time']:.2f}ms")
        
        # Finde 1-Sekunden-Delays
        slow_endpoints = [r for r in self.results if r['avg_time'] > 900]
        if slow_endpoints:
            print(f"\n⚠️  ENDPOINTS WITH 1-SECOND DELAY:")
            for result in slow_endpoints:
                print(f"   ❌ {result['name']}: {result['avg_time']:.2f}ms")
                print(f"      URL: {result['url']}")
        else:
            print(f"\n✅ NO 1-SECOND DELAYS DETECTED!")
        
        # Cache-Analyse
        print(f"\n💾 CACHE ANALYSIS:")
        cache_hits = 0
        cache_misses = 0
        
        for result in self.results:
            if 'cache' in result['name'].lower():
                # Analysiere Cache-Performance
                fast_requests = [t for t in result['times'] if t < 100]
                slow_requests = [t for t in result['times'] if t > 100]
                
                print(f"   {result['name']}:")
                print(f"      Fast requests (<100ms): {len(fast_requests)}")
                print(f"      Slow requests (>100ms): {len(slow_requests)}")
    
    def run_full_analysis(self):
        """Führe vollständige Analyse durch"""
        self.test_all_servers()
        self.analyze_results()
        
        print(f"\n🎯 RECOMMENDATIONS:")
        print("=" * 60)
        
        if any(r['avg_time'] > 900 for r in self.results):
            print("1. ❌ 1-SECOND DELAY DETECTED!")
            print("   - Check Flask configuration")
            print("   - Check for blocking operations")
            print("   - Check database connections")
            print("   - Check external API calls")
        else:
            print("1. ✅ No 1-second delays detected")
        
        print("2. 🔧 Optimization suggestions:")
        print("   - Use caching for expensive operations")
        print("   - Minimize database queries")
        print("   - Use async operations where possible")
        print("   - Check for unnecessary sleep() calls")

def main():
    """Main function"""
    debugger = PerformanceDebugger()
    debugger.run_full_analysis()

if __name__ == "__main__":
    main()
