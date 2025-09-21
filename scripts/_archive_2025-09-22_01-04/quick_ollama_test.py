#!/usr/bin/env python3
"""
Quick Ollama Test - Testet direkt die Ollama-API
"""

import requests
import json
import time

def test_ollama():
    base_url = "http://localhost:11434"
    
    # 1. Check verfügbare Modelle
    print("Checking Ollama models...")
    try:
        resp = requests.get(f"{base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            models = resp.json().get('models', [])
            print(f"\nVerfügbare Modelle ({len(models)}):")
            for m in models:
                print(f"  - {m['name']} ({m.get('size', 'unknown')})")
        else:
            print("ERROR: Ollama not responding")
            return
    except Exception as e:
        print(f"ERROR: {e}")
        return
    
    # 2. Test generation mit qwen2.5:7b
    model = "qwen2.5:7b"
    prompt = "Say only: Hello World"
    
    print(f"\n\nTesting generation with {model}...")
    print(f"Prompt: '{prompt}'")
    
    data = {
        "model": model,
        "prompt": prompt,
        "stream": False,
        "options": {
            "temperature": 0.1,
            "num_predict": 50
        }
    }
    
    start = time.time()
    try:
        resp = requests.post(
            f"{base_url}/api/generate",
            json=data,
            timeout=30
        )
        elapsed = time.time() - start
        
        if resp.status_code == 200:
            result = resp.json()
            text = result.get('response', '')
            print(f"\nSUCCESS in {elapsed:.1f}s")
            print(f"Response: '{text}'")
            print(f"Length: {len(text)} chars")
            
            if 'total_duration' in result:
                ms = result['total_duration'] / 1_000_000
                print(f"Ollama duration: {ms:.0f}ms")
        else:
            print(f"\nERROR {resp.status_code}: {resp.text[:200]}")
    except Exception as e:
        print(f"\nEXCEPTION after {time.time()-start:.1f}s: {e}")

if __name__ == "__main__":
    test_ollama()
