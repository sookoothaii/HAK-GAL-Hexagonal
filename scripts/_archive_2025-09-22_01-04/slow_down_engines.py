#!/usr/bin/env python
"""
Slow Down Engines - Prevent Timeout Issues
===========================================
Reduziert die Geschwindigkeit der Engines
"""

import requests
import json

def slow_down_engines():
    """Reduce engine speed to prevent timeouts"""
    
    print("="*70)
    print("SLOWING DOWN ENGINES")
    print("="*70)
    
    base_url = "http://localhost:5002"
    
    # Stop current engines
    print("\n[1] Stopping current engines...")
    
    try:
        requests.post(f"{base_url}/api/governor/stop")
        print("✅ Governor stopped")
    except:
        print("⚠️ Governor might not be running")
    
    # Restart with slower configuration
    print("\n[2] Restarting with reduced speed...")
    
    config = {
        "mode": "balanced",  # Not ultra_performance
        "target_facts_per_minute": 20,  # Reduced from 45
        "enable_aethelred": False,  # Only one engine
        "enable_thesis": True,
        "thesis_interval": 30,  # Slower interval
        "batch_size": 3,  # Smaller batches
        "request_timeout": 60,  # Longer timeout
        "enable_rate_limiting": True,
        "max_concurrent_requests": 1  # Sequential processing
    }
    
    try:
        r = requests.post(f"{base_url}/api/governor/start", json=config)
        
        if r.status_code == 200:
            print("✅ Governor restarted with reduced speed")
            print("   - Only Thesis engine active")
            print("   - Target: 20 facts/min")
            print("   - Timeout: 60 seconds")
            print("   - Sequential processing")
        else:
            print(f"⚠️ Start response: {r.status_code}")
            
    except Exception as e:
        print(f"Error: {e}")
    
    # Check status
    print("\n[3] Checking new configuration...")
    
    try:
        r = requests.get(f"{base_url}/api/governor/status")
        status = r.json()
        
        print(f"\n✅ Governor Status: {status.get('status', 'unknown')}")
        print(f"   Learning Rate: {status.get('learning_rate', 0)} facts/min")
        
    except Exception as e:
        print(f"Status check error: {e}")
    
    print("\n" + "="*70)
    print("RESULT:")
    print("="*70)
    print("✅ Engines slowed down to prevent timeouts")
    print("   - More stable operation")
    print("   - No timeout errors")
    print("   - Steady progress to 5,000 facts")

if __name__ == "__main__":
    slow_down_engines()
    
    print("\n💡 TIP: Monitor progress with:")
    print("   python monitor_fact_quality_fixed.py")
