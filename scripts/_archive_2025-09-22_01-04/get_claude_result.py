#!/usr/bin/env python3
"""
Hole Claude's Antwort ab
"""

import requests
import json
import os
from pathlib import Path

# Load environment
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path, override=True)

BASE_URL = "http://localhost:5002"
API_KEY = os.environ.get("HAKGAL_API_KEY", "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d")
TASK_ID = "464f4f0a-6ea0-4182-b84f-cad59f8e2099"

headers = {"X-API-Key": API_KEY}

print("🤖 Claude CLI Ergebnis")
print("=" * 60)

response = requests.get(f"{BASE_URL}/api/agent-bus/tasks/{TASK_ID}", headers=headers)

if response.status_code == 200:
    data = response.json()
    print(f"📊 Status: {data.get('status')}")
    
    result = data.get('result', {})
    if isinstance(result, dict) and 'result' in result:
        claude_response = result['result']
        print(f"\n✅ Claude's Antwort:")
        print("=" * 60)
        print(claude_response)
        print("=" * 60)
        
        # Save to file
        with open("claude_response.txt", "w", encoding="utf-8") as f:
            f.write(claude_response)
        print(f"\n💾 Antwort gespeichert in: claude_response.txt")
    else:
        print(f"Result: {json.dumps(result, indent=2)}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
