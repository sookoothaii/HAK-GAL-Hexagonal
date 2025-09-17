#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
AETHELRED ENGINE API FIX
========================
Korrigiert die add_facts_governed Methode für API-basierte Fact-Addition
"""

import os
import requests
import time
from typing import List

# AUTH TOKEN aus Environment
AUTH_TOKEN = os.environ.get('HAKGAL_AUTH_TOKEN', '515f57956e7bd15ddc3817573598f190')
API_BASE_URL = 'http://localhost:5002'

def add_facts_via_api(facts: List[str], max_retries: int = 3) -> int:
    """
    Fügt Facts via API hinzu statt direkt in die DB
    
    Args:
        facts: Liste von Fact-Statements
        max_retries: Maximale Anzahl von Versuchen
        
    Returns:
        Anzahl erfolgreich hinzugefügter Facts
    """
    
    if not facts:
        return 0
    
    headers = {
        'Content-Type': 'application/json',
        'X-API-Key': AUTH_TOKEN
    }
    
    added_count = 0
    
    for fact in facts:
        # Ensure fact ends with period
        if not fact.endswith('.'):
            fact = fact + '.'
        
        payload = {
            'statement': fact,
            'context': {
                'source': 'aethelred_engine',
                'engine_version': 'fixed_api',
                'generated_at': time.time()
            }
        }
        
        success = False
        for attempt in range(max_retries):
            try:
                response = requests.post(
                    f"{API_BASE_URL}/api/facts",
                    json=payload,
                    headers=headers,
                    timeout=5
                )
                
                if response.status_code in [200, 201]:
                    added_count += 1
                    print(f"[API] ✅ Added: {fact[:50]}...")
                    success = True
                    break
                elif response.status_code == 409:
                    # Duplicate - skip
                    print(f"[API] ⚠️ Duplicate: {fact[:50]}...")
                    success = True  # Consider it handled
                    break
                elif response.status_code == 403:
                    print(f"[API] ❌ Auth failed! Check token: {AUTH_TOKEN[:8]}...")
                    return added_count  # Stop if auth fails
                else:
                    print(f"[API] ❌ Failed ({response.status_code}): {fact[:50]}...")
                    
            except requests.exceptions.ConnectionError:
                print(f"[API] ❌ Connection failed (attempt {attempt+1}/{max_retries})")
                time.sleep(1)  # Wait before retry
            except requests.exceptions.Timeout:
                print(f"[API] ⏱️ Timeout (attempt {attempt+1}/{max_retries})")
                time.sleep(0.5)
            except Exception as e:
                print(f"[API] ❌ Error: {e}")
                break
        
        if not success:
            print(f"[API] ❌ Failed after {max_retries} attempts: {fact[:50]}...")
    
    return added_count


# MONKEY PATCH für Aethelred Engine
def patch_aethelred_engine():
    """
    Patcht die Aethelred Engine zur Laufzeit
    """
    import sys
    
    # Find and patch the engine module if loaded
    for module_name, module in sys.modules.items():
        if 'aethelred' in module_name.lower():
            if hasattr(module, 'AethelredEngine'):
                # Patch the class
                original_add = getattr(module.AethelredEngine, 'add_facts_governed', None)
                if original_add:
                    print(f"[PATCH] Patching {module_name}.AethelredEngine.add_facts_governed")
                    
                    def new_add_facts_governed(self, facts):
                        """Patched version using API"""
                        return add_facts_via_api(facts)
                    
                    module.AethelredEngine.add_facts_governed = new_add_facts_governed
                    print(f"[PATCH] ✅ Patched successfully!")
                    
            # Also patch any standalone functions
            if hasattr(module, 'add_facts_governed'):
                print(f"[PATCH] Patching {module_name}.add_facts_governed")
                module.add_facts_governed = add_facts_via_api


def test_api_connection():
    """
    Testet die API-Verbindung
    """
    print("\n=== API CONNECTION TEST ===")
    
    # Test health endpoint
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print(f"✅ API is running on {API_BASE_URL}")
            print(f"   Status: {response.json()}")
        else:
            print(f"❌ API returned {response.status_code}")
    except:
        print(f"❌ Cannot connect to API at {API_BASE_URL}")
        return False
    
    # Test auth
    headers = {'X-API-Key': AUTH_TOKEN}
    test_fact = f"TestFact(API_Test, Works, {time.time()})."
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/api/facts",
            json={'statement': test_fact},
            headers=headers,
            timeout=5
        )
        
        if response.status_code in [200, 201, 409]:
            print(f"✅ Authentication works!")
            return True
        elif response.status_code == 403:
            print(f"❌ Authentication failed! Check token.")
            return False
        else:
            print(f"⚠️ Unexpected response: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("AETHELRED ENGINE API FIX")
    print("=" * 60)
    
    # Test connection
    if test_api_connection():
        print("\n✅ API connection successful!")
        
        # Test adding facts
        test_facts = [
            "Energy(Kinetic, Formula, 0.5, m, v²).",
            "Physics(Newton, Laws, Three, Motion).",
            "Chemistry(Water, H2O, Molecules, Bonds)."
        ]
        
        print(f"\nTesting with {len(test_facts)} facts...")
        added = add_facts_via_api(test_facts)
        print(f"✅ Added {added} facts via API")
        
        # Apply patch
        print("\nApplying runtime patch...")
        patch_aethelred_engine()
        
    else:
        print("\n❌ Fix API connection first!")
        print("\nChecklist:")
        print("1. Is backend running on port 5002?")
        print("2. Is AUTH_TOKEN set correctly?")
        print(f"   Current: {AUTH_TOKEN[:8]}...")
        print("3. Is /api/facts endpoint available?")
