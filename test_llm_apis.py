#!/usr/bin/env python3
"""
Direct LLM API Test - Verifiziert API-Keys und Connectivity
============================================================
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

def test_deepseek():
    """Test DeepSeek API directly"""
    api_key = os.environ.get('DEEPSEEK_API_KEY', '')
    if not api_key:
        print("❌ DeepSeek: No API key configured")
        return False
    
    print(f"Testing DeepSeek API (Key: {api_key[:10]}...)")
    
    try:
        start = time.time()
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': 'Say "test ok" if you receive this'}
                ],
                'max_tokens': 10,
                'temperature': 0.1
            },
            timeout=60  # Increased timeout
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ DeepSeek: Success in {elapsed:.1f}s - Response: {content}")
            return True
        else:
            print(f"❌ DeepSeek: HTTP {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ DeepSeek: Timeout after 60 seconds")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ DeepSeek: Connection failed - {str(e)[:100]}")
        return False
    except Exception as e:
        print(f"❌ DeepSeek: Error - {str(e)[:100]}")
        return False

def test_mistral():
    """Test Mistral API directly"""
    api_key = os.environ.get('MISTRAL_API_KEY', '')
    if not api_key:
        print("❌ Mistral: No API key configured")
        return False
    
    print(f"Testing Mistral API (Key: {api_key[:10]}...)")
    
    try:
        start = time.time()
        response = requests.post(
            'https://api.mistral.ai/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'mistral-small-latest',  # Changed from mistral-medium
                'messages': [
                    {'role': 'user', 'content': 'Say "test ok" if you receive this'}
                ],
                'max_tokens': 10,
                'temperature': 0.1
            },
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Mistral: Success in {elapsed:.1f}s - Response: {content}")
            return True
        else:
            print(f"❌ Mistral: HTTP {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Mistral: Timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Mistral: Error - {str(e)[:100]}")
        return False

def test_gemini():
    """Test Gemini API directly"""
    api_key = os.environ.get('GEMINI_API_KEY', '')
    if not api_key:
        print("❌ Gemini: No API key configured")
        return False
    
    print(f"Testing Gemini API (Key: {api_key[:10]}...)")
    
    try:
        start = time.time()
        response = requests.post(
            f'https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={api_key}',
            headers={'Content-Type': 'application/json'},
            json={
                'contents': [{
                    'parts': [{
                        'text': 'Say "test ok" if you receive this'
                    }]
                }]
            },
            timeout=30
        )
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            result = response.json()
            content = result['candidates'][0]['content']['parts'][0]['text']
            print(f"✅ Gemini: Success in {elapsed:.1f}s - Response: {content[:50]}")
            return True
        else:
            print(f"❌ Gemini: HTTP {response.status_code} - {response.text[:200]}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"❌ Gemini: Timeout after 30 seconds")
        return False
    except Exception as e:
        print(f"❌ Gemini: Error - {str(e)[:100]}")
        return False

def test_network_connectivity():
    """Test basic network connectivity"""
    print("\n1. Testing Network Connectivity...")
    
    # Test DNS and HTTPS
    test_sites = [
        ('Google DNS', 'https://dns.google.com'),
        ('CloudFlare', 'https://1.1.1.1'),
        ('OpenAI', 'https://api.openai.com'),
    ]
    
    for name, url in test_sites:
        try:
            r = requests.get(url, timeout=5)
            print(f"  ✅ {name}: Reachable")
        except Exception as e:
            print(f"  ❌ {name}: {str(e)[:50]}")

if __name__ == '__main__':
    print("=" * 60)
    print("LLM API CONNECTIVITY TEST")
    print("=" * 60)
    
    test_network_connectivity()
    
    print("\n2. Testing LLM APIs...")
    print("-" * 40)
    
    deepseek_ok = test_deepseek()
    print()
    mistral_ok = test_mistral()
    print()
    gemini_ok = test_gemini()
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print("-" * 40)
    
    if deepseek_ok or mistral_ok or gemini_ok:
        print("✅ At least one LLM API is working")
        if not deepseek_ok:
            print("⚠️  DeepSeek needs investigation")
        if not mistral_ok:
            print("⚠️  Mistral needs investigation")
        if not gemini_ok:
            print("⚠️  Gemini needs investigation")
    else:
        print("❌ NO LLM APIs working - check network/firewall/API keys")
    
    print("=" * 60)
