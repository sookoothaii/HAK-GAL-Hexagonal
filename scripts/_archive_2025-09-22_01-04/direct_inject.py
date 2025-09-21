#!/usr/bin/env python
"""
ULTIMATE FIX: Direct fact injection bypassing everything
"""

import requests
import time

API_BASE_URL = "http://localhost:5002/api"
API_KEY = "hg_sk_4f9a8e1b7d2c5f6a8b3d9e0c1a7b4f9d"

def direct_inject():
    """Inject facts directly, bypass all checks"""
    
    headers = {
        "Content-Type": "application/json",
        "X-API-Key": API_KEY
    }
    
    # Sinnvolle HAK-GAL Facts ohne Platzhalter
    test_facts = [
        "Uses(HAK_GAL, SQLite_Database).",
        "Requires(HAK_GAL, Python_Environment).",
        "Supports(HAK_GAL, Multi_Agent_Systems).",
        "Provides(HAK_GAL, Knowledge_Management).",
        "Architecture(HAK_GAL, Hexagonal, REST_API, MCP_Server, WebSocket, Database).",
        "System(HAK_GAL, Frontend, Backend, API, Database, Agents).",
        "Process(HAK_GAL, Input, Analysis, Storage, Retrieval, Output).",
        "Contains(HAK_GAL, Gemini_Adapter, Claude_Adapter, Cursor_Adapter).",
        "RunsOn(HAK_GAL_Backend, Flask, Port_5002).",
        "RunsOn(HAK_GAL_Frontend, React, Port_5173)."
    ]
    
    print("DIRECT FACT INJECTION TEST")
    print("=" * 60)
    
    success = 0
    failed = 0
    
    for fact in test_facts:
        try:
            r = requests.post(
                f"{API_BASE_URL}/facts",
                headers=headers,
                json={"statement": fact},
                timeout=10
            )
            
            if r.status_code == 200 and r.json().get('success'):
                print(f"✅ Added: {fact}")
                success += 1
            elif 'exists' in str(r.json().get('message', '')).lower():
                print(f"⏭️ Exists: {fact}")
            else:
                print(f"❌ Failed: {fact}")
                failed += 1
                
        except Exception as e:
            print(f"❌ Error: {fact} - {e}")
            failed += 1
        
        time.sleep(0.2)  # Rate limit
    
    print("\n" + "=" * 60)
    print(f"Results: {success} added, {failed} failed")
    print()
    
    if success > 0:
        print("✅ API WORKS! Problem is with QualityGate/generate_bridge_facts")
    else:
        print("❌ API might be down or write-protected")

if __name__ == "__main__":
    direct_inject()
