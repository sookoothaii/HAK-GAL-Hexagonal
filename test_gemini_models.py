#!/usr/bin/env python3
"""
Test Gemini Models - Find which model works
============================================
"""

import os
import sys
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

models_to_test = [
    "gemini-1.5-flash",
    "gemini-1.5-flash-latest", 
    "gemini-1.5-pro",
    "gemini-1.5-pro-latest",
    "gemini-1.0-pro",
    "gemini-1.0-pro-latest",
    "gemini-pro",
]

working_models = []

for model in models_to_test:
    print(f"\nTesting {model}...", end=" ")
    
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        response = requests.post(
            url,
            headers={"Content-Type": "application/json"},
            json={
                "contents": [{
                    "parts": [{
                        "text": "Say 'test ok' if you receive this"
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.1,
                    "maxOutputTokens": 10
                }
            },
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text'][:50]
            print(f"✅ WORKS! Response: {content}")
            working_models.append(model)
        elif response.status_code == 404:
            print(f"❌ Not found")
        else:
            print(f"❌ HTTP {response.status_code}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)[:30]}")

print("\n" + "=" * 60)
print("SUMMARY:")
print("-" * 40)

if working_models:
    print(f"✅ Working models found: {', '.join(working_models)}")
    print(f"\nRecommended to use: {working_models[0]}")
else:
    print("❌ No working Gemini models found")
    print("Check if API key is valid or if there's a regional restriction")

print("=" * 60)
