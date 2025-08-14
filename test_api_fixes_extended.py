#!/usr/bin/env python3
"""
Extended Test for Hexagonal API with longer timeout
====================================================
"""

import requests
import json
import time
from datetime import datetime

API_URL = "http://127.0.0.1:5001"

def test_llm_with_debug():
    """Test LLM with debug output"""
    
    print("=" * 60)
    print("LLM EXPLANATION DEBUG TEST")
    print("=" * 60)
    
    # Test 1: Check if original backend is running
    print("\n1. Checking if original backend (5000) is available...")
    try:
        resp = requests.get("http://127.0.0.1:5000/health", timeout=2)
        if resp.status_code == 200:
            print("   ✅ Original backend available on port 5000")
        else:
            print("   ❌ Original backend not responding properly")
    except:
        print("   ⚠️ Original backend NOT running (Port 5000)")
        print("      This is why LLM explanation might be slow/timeout")
    
    # Test 2: Try LLM with extended timeout
    print("\n2. Testing LLM Explanation with 60s timeout...")
    start_time = time.time()
    
    try:
        resp = requests.post(
            f"{API_URL}/api/llm/get-explanation",
            json={
                "topic": "HasPart(Computer,CPU)",
                "context_facts": ["HasPart(Computer,RAM)."]
            },
            timeout=60  # Extended timeout
        )
        
        elapsed = time.time() - start_time
        print(f"   Response time: {elapsed:.2f} seconds")
        print(f"   Status: {resp.status_code}")
        
        if resp.status_code == 200:
            result = resp.json()
            if 'explanation' in result:
                print("   ✅ LLM Explanation received!")
                print(f"   Type: {result.get('status', 'unknown')}")
                print(f"   Length: {len(result['explanation'])} characters")
                print(f"   Preview: {result['explanation'][:200]}...")
                
                # Check if it's using fallback
                if "Neural confidence" in result['explanation']:
                    print("   📝 Using local fallback (no LLM API available)")
                else:
                    print("   🤖 Using actual LLM provider")
            else:
                print("   ⚠️ Response missing explanation field")
                print(f"   Response: {result}")
        else:
            print(f"   ❌ LLM endpoint error: {resp.status_code}")
            print(f"   Response: {resp.text[:500]}")
            
    except requests.Timeout:
        elapsed = time.time() - start_time
        print(f"   ❌ Timeout after {elapsed:.2f} seconds")
        print("   Possible causes:")
        print("   - No API keys configured")
        print("   - Original backend not running")
        print("   - Network issues with LLM providers")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Check environment
    print("\n3. Checking environment...")
    import os
    
    has_deepseek = bool(os.environ.get('DEEPSEEK_API_KEY'))
    has_mistral = bool(os.environ.get('MISTRAL_API_KEY'))
    has_gemini = bool(os.environ.get('GEMINI_API_KEY'))
    
    print(f"   DEEPSEEK_API_KEY: {'✅ Set' if has_deepseek else '❌ Not set'}")
    print(f"   MISTRAL_API_KEY: {'✅ Set' if has_mistral else '❌ Not set'}")
    print(f"   GEMINI_API_KEY: {'✅ Set' if has_gemini else '❌ Not set'}")
    
    if not (has_deepseek or has_mistral or has_gemini):
        print("\n   ⚠️ No API keys configured!")
        print("   The system will use local fallback explanations only.")
        print("   To enable LLM explanations, add keys to .env file")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    test_llm_with_debug()
