#!/usr/bin/env python3
"""
Test API Endpoints
"""

import requests
import json

def test_health():
    """Test health endpoint"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        print(f"Health Check Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Health Check Error: {e}")
        return False

def test_metrics():
    """Test metrics endpoint"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/metrics', timeout=5)
        print(f"Metrics Status: {response.status_code}")
        data = response.json()
        
        print("\n=== LIVE METRICS ===")
        print(f"Facts Count: {data['facts_count']}")
        print(f"Avg Query Time: {data['avg_query_time']:.3f}s")
        print(f"Cache Hit Rate: {data['cache_hits']/(data['cache_hits']+data['cache_misses'])*100:.1f}%")
        print(f"CPU Usage: {data['system_cpu_percent']:.1f}%")
        print(f"Memory Usage: {data['system_memory_percent']:.1f}%")
        print(f"Database Connections: {data['database_connections']}")
        print(f"WAL Size: {data['wal_size_bytes']} bytes")
        
        return response.status_code == 200
    except Exception as e:
        print(f"Metrics Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing HAK/GAL API Endpoints")
    print("=" * 40)
    
    health_ok = test_health()
    print()
    metrics_ok = test_metrics()
    
    print("\n" + "=" * 40)
    print("📊 TEST RESULTS:")
    print(f"Health Endpoint: {'✅ PASS' if health_ok else '❌ FAIL'}")
    print(f"Metrics Endpoint: {'✅ PASS' if metrics_ok else '❌ FAIL'}")
    
    if health_ok and metrics_ok:
        print("\n🎉 ALL API ENDPOINTS WORKING!")
    else:
        print("\n⚠️ Some endpoints failed")

if __name__ == "__main__":
    main()
