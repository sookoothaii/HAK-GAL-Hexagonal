#!/usr/bin/env python3
"""
Test Gemini Models - Focus on 1.5 Flash Latest
===============================================
Tests which Gemini models work with extended timeout
"""

import os
import sys
import time
import requests
from pathlib import Path

# Load environment
env_path = Path(__file__).parent / '.env'
if env_path.exists():
    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        if '=' in line:
            key, val = line.split('=', 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            if key and key not in os.environ:
                os.environ[key] = val

api_key = os.environ.get('GEMINI_API_KEY', '')
if not api_key:
    print("❌ No GEMINI_API_KEY found in .env")
    sys.exit(1)

print(f"Testing Gemini models with key: {api_key[:10]}...")
print("=" * 60)

# Priority list - flash-latest first
models_to_test = [
    # Latest versions (highest priority)
    "gemini-1.5-flash-latest",
    "gemini-1.5-pro-latest",
    
    # Stable 1.5 versions
    "gemini-1.5-flash",
    "gemini-1.5-flash-001",
    "gemini-1.5-flash-002",
    "gemini-1.5-pro",
    "gemini-1.5-pro-001",
    "gemini-1.5-pro-002",
    
    # 2.0 versions (experimental)
    "gemini-2.0-flash",
    "gemini-2.0-flash-latest",
    
    # 1.0 versions (legacy)
    "gemini-1.0-pro",
    "gemini-1.0-pro-latest",
]

working_models = []
model_timings = {}

for model in models_to_test:
    print(f"\nTesting {model}...", end=" ")
    
    try:
        start_time = time.time()
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{
                        "text": "Say 'test ok' and nothing else"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 10,
                    "topK": 1
                }
            },
            timeout=15  # Extended timeout
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            
            # Try to extract response text
            text = "No text found"
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate and 'parts' in candidate['content']:
                    text = candidate['content']['parts'][0].get('text', 'No text')[:50]
            
            print(f"✅ WORKS! Response: {text} (Time: {elapsed:.2f}s)")
            working_models.append(model)
            model_timings[model] = elapsed
            
        elif response.status_code == 404:
            print(f"❌ Not found (404)")
        elif response.status_code == 400:
            print(f"❌ Bad request (400) - Model may be deprecated")
        elif response.status_code == 403:
            print(f"❌ Forbidden (403) - Check API key permissions")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except requests.exceptions.Timeout:
        print(f"❌ Timeout (>15s)")
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("-" * 40)

if working_models:
    print(f"✅ {len(working_models)} working models found:")
    for model in working_models:
        timing = model_timings.get(model, 0)
        print(f"   • {model} ({timing:.2f}s)")
    
    # Find fastest model
    if model_timings:
        fastest = min(model_timings.items(), key=lambda x: x[1])
        print(f"\n⚡ FASTEST: {fastest[0]} ({fastest[1]:.2f}s)")
        print(f"💡 RECOMMENDED: {working_models[0]} (first working)")
else:
    print("❌ No working Gemini models found")
    print("Possible issues:")
    print("• API key may be invalid or expired")
    print("• Regional restrictions may apply")
    print("• Models may be temporarily unavailable")

print("=" * 60)
