#!/usr/bin/env python3
"""
FIND THE PROBLEM - Why No Facts?
=================================
"""

import os
import sys
from pathlib import Path

print("\n" + "🔍"*40)
print("SYSTEM DIAGNOSTIC - FIND THE PROBLEM")
print("🔍"*40)

# 1. Check Python environment
print("\n1. PYTHON ENVIRONMENT:")
print(f"   Python: {sys.executable}")
print(f"   Version: {sys.version}")
print(f"   CWD: {os.getcwd()}")

# 2. Check if .env exists
env_file = Path(".env")
print(f"\n2. ENVIRONMENT FILE:")
print(f"   .env exists: {env_file.exists()}")

if env_file.exists():
    with open(env_file) as f:
        lines = f.readlines()
    api_keys = [l for l in lines if "API_KEY" in l and not l.startswith("#")]
    print(f"   API keys found: {len(api_keys)}")
    for key in api_keys:
        name = key.split("=")[0]
        has_value = len(key.split("=")[1].strip()) > 0
        print(f"     {name}: {'✅ Set' if has_value else '❌ Empty'}")

# 3. Check Engine Scripts
print(f"\n3. ENGINE SCRIPTS:")
engines = {
    "Aethelred": Path("src_hexagonal/infrastructure/engines/aethelred_engine.py"),
    "Thesis": Path("src_hexagonal/infrastructure/engines/thesis_engine.py")
}

for name, path in engines.items():
    print(f"   {name}: {'✅ Found' if path.exists() else '❌ Missing'} - {path}")

# 4. Check Governor
print(f"\n4. GOVERNOR:")
governor_path = Path("src_hexagonal/adapters/governor_adapter.py")
print(f"   Governor adapter: {'✅ Found' if governor_path.exists() else '❌ Missing'}")

# 5. Check which API file is used
print(f"\n5. API FILES:")
api_files = list(Path("src_hexagonal").glob("hexagonal_api*.py"))
for f in api_files:
    if f.name.endswith("backup") or f.name.endswith("backup.py"):
        continue
    size = f.stat().st_size
    print(f"   {f.name}: {size:,} bytes")

# 6. Try to import and test DeepSeek
print(f"\n6. TEST DEEPSEEK DIRECTLY:")
try:
    # Load .env
    from dotenv import load_dotenv
    load_dotenv()
    
    # Get API key
    deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
    print(f"   DEEPSEEK_API_KEY: {'✅ Set' if deepseek_key else '❌ Not set'}")
    
    if deepseek_key:
        # Test API
        import requests
        
        headers = {
            "Authorization": f"Bearer {deepseek_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say 'Hello, I work!' in 5 words or less."}
            ],
            "temperature": 0.7,
            "max_tokens": 50
        }
        
        print("   Testing API call...")
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            message = result['choices'][0]['message']['content']
            print(f"   ✅ DEEPSEEK WORKS! Response: {message}")
        else:
            print(f"   ❌ DeepSeek API error: {response.status_code}")
            print(f"      {response.text[:200]}")
    
except Exception as e:
    print(f"   ❌ Test failed: {e}")

# 7. Check database
print(f"\n7. DATABASE:")
db_path = Path("hexagonal_kb.db")
print(f"   Database exists: {db_path.exists()}")
if db_path.exists():
    print(f"   Database size: {db_path.stat().st_size:,} bytes")

# 8. Summary
print("\n" + "="*60)
print("DIAGNOSIS COMPLETE")
print("="*60)

print("\nTO FIX THE PROBLEM:")
print("1. Make sure the backend is running:")
print("   python src_hexagonal/hexagonal_api_enhanced_clean.py")
print("\n2. Test an engine manually:")
print("   python test_engine_direct.py")
print("\n3. Check the backend output for errors")
print("\n4. If DeepSeek doesn't work, check your API key")
