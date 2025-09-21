#!/usr/bin/env python3
"""
Force start the optimized generator via API
"""
import requests
import json
import time

print("="*60)
print("FORCE START OPTIMIZED GENERATOR")
print("="*60)

# First stop the current governor
print("\n1. Stopping current governor...")
try:
    response = requests.post(
        "http://127.0.0.1:5002/api/governor/stop",
        timeout=5
    )
    print("   ✅ Governor stopped")
    time.sleep(1)
except Exception as e:
    print(f"   ⚠️ {e}")

# Now start with use_llm flag
print("\n2. Starting governor with LLM generator...")
try:
    response = requests.post(
        "http://127.0.0.1:5002/api/governor/start",
        json={"use_llm": True},  # CRITICAL: This enables the generator!
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Started!")
        print(f"   Mode: {data.get('mode', 'unknown')}")
        print(f"   Generating: {data.get('generating', False)}")
        print(f"   Message: {data.get('message', '')}")
        
        if 'optimized' in data:
            if data['optimized']:
                print("   ✅✅✅ OPTIMIZED GENERATOR ACTIVE!")
            else:
                print("   ⚠️ OLD generator (not optimized)")
    else:
        print(f"   ❌ Failed: {response.status_code}")
        print(f"   Response: {response.text}")
        
except Exception as e:
    print(f"   ❌ Error: {e}")

# Check status after 2 seconds
time.sleep(2)

print("\n3. Checking generator status...")
try:
    response = requests.get("http://127.0.0.1:5002/api/llm-governor/status", timeout=2)
    if response.status_code == 200:
        data = response.json()
        print(f"   Generating: {data.get('generating', False)}")
        print(f"   Optimized: {data.get('optimized', False)}")
        
        if 'metrics' in data:
            metrics = data['metrics']
            print(f"   Facts generated: {metrics.get('facts_generated', 0)}")
            print(f"   HasProperty %: {metrics.get('has_property_percentage', 0):.1f}%")
            
except Exception as e:
    print(f"   Error: {e}")

print("\n" + "="*60)
print("Monitor the generation with:")
print("python scripts\\monitor_generation.py")
print("="*60)
