#!/usr/bin/env python3
"""
BROWSER SIMULATION TEST - Simuliert exakt was ein Browser macht
"""

import requests
import time
import json
from urllib.parse import urljoin

class BrowserSimulator:
    def __init__(self):
        self.session = requests.Session()
        self.setup_browser_headers()
    
    def setup_browser_headers(self):
        """Setup echte Browser-Headers"""
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'de-DE,de;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Cache-Control': 'max-age=0'
        })
    
    def test_page_load(self, url):
        """Simuliert kompletten Page Load wie Browser"""
        print(f"🌐 Loading: {url}")
        
        # 1. Initial Request (wie Browser)
        start_time = time.time()
        try:
            response = self.session.get(url, timeout=30)
            end_time = time.time()
            
            load_time = (end_time - start_time) * 1000
            
            print(f"  📊 Page Load Time: {load_time:.2f}ms")
            print(f"  📊 Status Code: {response.status_code}")
            print(f"  📊 Content Length: {len(response.content)} bytes")
            print(f"  📊 Response Headers: {dict(response.headers)}")
            
            # 2. Simuliere weitere Browser-Requests
            if response.status_code == 200:
                self.simulate_browser_behavior(url, response)
            
            return load_time
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None
    
    def simulate_browser_behavior(self, base_url, response):
        """Simuliert typisches Browser-Verhalten"""
        print(f"  🔍 Simulating browser behavior...")
        
        # Simuliere AJAX-Requests (wie DevTools)
        ajax_endpoints = [
            '/api/health',
            '/api/metrics'
        ]
        
        for endpoint in ajax_endpoints:
            full_url = urljoin(base_url, endpoint)
            self.test_ajax_request(full_url)
    
    def test_ajax_request(self, url):
        """Simuliert AJAX-Request"""
        # AJAX-Headers
        ajax_headers = {
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'http://127.0.0.1:5000/'
        }
        
        start_time = time.time()
        try:
            response = self.session.get(url, headers=ajax_headers, timeout=30)
            end_time = time.time()
            
            ajax_time = (end_time - start_time) * 1000
            
            print(f"    📡 AJAX {url}: {ajax_time:.2f}ms")
            print(f"    📡 Status: {response.status_code}")
            print(f"    📡 Cache: {response.headers.get('X-From-Cache', 'Not Set')}")
            
        except Exception as e:
            print(f"    ❌ AJAX Error: {e}")
    
    def test_multiple_page_loads(self, url, count=5):
        """Test mehrere Page Loads"""
        print(f"🔄 Testing {count} page loads...")
        times = []
        
        for i in range(count):
            print(f"\n--- Page Load {i+1} ---")
            load_time = self.test_page_load(url)
            if load_time:
                times.append(load_time)
            
            # Simuliere Browser-Delay zwischen Requests
            time.sleep(0.1)
        
        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            
            print(f"\n📊 STATISTICS:")
            print(f"  Average: {avg_time:.2f}ms")
            print(f"  Minimum: {min_time:.2f}ms")
            print(f"  Maximum: {max_time:.2f}ms")
            
            # Prüfe auf 500ms+ Delays
            if max_time > 500:
                print(f"  ⚠️  WARNING: Maximum time >500ms!")
            if avg_time > 200:
                print(f"  ⚠️  WARNING: Average time >200ms!")

def main():
    """Main test function"""
    print("🚀 BROWSER SIMULATION TEST")
    print("=" * 60)
    print("Simuliert exakt was ein Browser macht")
    print("=" * 60)
    
    browser = BrowserSimulator()
    
    # Test HAK/GAL Dashboard
    print("\n🌐 Testing HAK/GAL Dashboard:")
    browser.test_multiple_page_loads('http://127.0.0.1:5000/', 3)
    
    print("\n" + "=" * 60)
    print("🎯 FAZIT:")
    print("Wenn hier 500ms+ gemessen werden, dann ist das Problem real!")
    print("Das ist was ein echter Browser erleben würde.")
    print("=" * 60)

if __name__ == "__main__":
    main()


