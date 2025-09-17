#!/usr/bin/env python3
"""
Full System Test - Flask + Prometheus
"""

import requests
import time

def test_flask():
    """Test Flask Dashboard"""
    try:
        response = requests.get('http://127.0.0.1:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Flask Health: {data['status']} (Uptime: {data['uptime']:.1f}s)")
            return True
    except Exception as e:
        print(f"❌ Flask Error: {e}")
    return False

def test_prometheus():
    """Test Prometheus Metrics"""
    try:
        response = requests.get('http://127.0.0.1:8000/metrics', timeout=5)
        if response.status_code == 200:
            metrics = response.text
            lines = metrics.count('\n')
            print(f"✅ Prometheus: {lines} metric lines")
            return True
    except Exception as e:
        print(f"❌ Prometheus Error: {e}")
    return False

def test_metrics_integration():
    """Test metrics integration between Flask and Prometheus"""
    try:
        # Get Flask metrics
        flask_response = requests.get('http://127.0.0.1:5000/api/metrics', timeout=5)
        flask_data = flask_response.json()
        
        # Get Prometheus metrics
        prom_response = requests.get('http://127.0.0.1:8000/metrics', timeout=5)
        prom_text = prom_response.text
        
        # Check if Prometheus contains Flask data
        facts_in_prom = f'hakgal_facts_total {flask_data["facts_count"]}' in prom_text
        cpu_in_prom = f'hakgal_system_cpu_percent {flask_data["system_cpu_percent"]}' in prom_text
        
        if facts_in_prom and cpu_in_prom:
            print("✅ Metrics Integration: Flask → Prometheus working")
            return True
        else:
            print("⚠️ Metrics Integration: Partial sync")
            return False
    except Exception as e:
        print(f"❌ Integration Error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 FULL SYSTEM TEST - Flask + Prometheus")
    print("=" * 50)
    
    flask_ok = test_flask()
    prometheus_ok = test_prometheus()
    integration_ok = test_metrics_integration()
    
    print("\n" + "=" * 50)
    print("📊 SYSTEM STATUS:")
    print(f"Flask Dashboard: {'✅ RUNNING' if flask_ok else '❌ DOWN'}")
    print(f"Prometheus: {'✅ RUNNING' if prometheus_ok else '❌ DOWN'}")
    print(f"Integration: {'✅ SYNCED' if integration_ok else '⚠️ PARTIAL'}")
    
    if flask_ok and prometheus_ok:
        print("\n🎉 FULL SYSTEM OPERATIONAL!")
        print("🌐 Flask: http://localhost:5000")
        print("📊 Prometheus: http://localhost:8000/metrics")
    else:
        print("\n⚠️ System partially operational")

if __name__ == "__main__":
    main()


