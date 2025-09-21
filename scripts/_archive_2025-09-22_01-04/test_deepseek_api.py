#!/usr/bin/env python3
"""
DEEPSEEK API TEST
=================
Testet die Verbindung und Funktionalität der DeepSeek API
"""

import os
import requests
import json
import time

def test_deepseek_api():
    """Teste DeepSeek API mit minimalem Request"""
    
    print("="*60)
    print("DEEPSEEK API VERBINDUNGSTEST")
    print("="*60)
    
    # API Key prüfen
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        print("❌ FEHLER: DEEPSEEK_API_KEY nicht gesetzt!")
        print("\nSetzen Sie den Key mit:")
        print('  $env:DEEPSEEK_API_KEY = "sk-..."')
        return False
    
    print(f"✅ API Key gefunden: {api_key[:15]}...")
    
    # Test 1: Einfacher Ping
    print("\n📡 Test 1: Einfache Anfrage...")
    print("-"*40)
    
    try:
        start_time = time.time()
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'user', 'content': 'Say "API works" if you receive this.'}
                ],
                'temperature': 0.1,
                'max_tokens': 10
            },
            timeout=10
        )
        
        elapsed = time.time() - start_time
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Time: {elapsed:.2f}s")
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Antwort erhalten: {content}")
        else:
            print(f"❌ Fehler: {response.status_code}")
            print(f"Response: {response.text[:500]}")
            return False
            
    except requests.exceptions.Timeout:
        print("❌ Timeout nach 10 Sekunden")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Verbindungsfehler: {e}")
        return False
    except Exception as e:
        print(f"❌ Unerwarteter Fehler: {e}")
        return False
    
    # Test 2: Größere Anfrage
    print("\n📡 Test 2: Faktvalidierung (5 Fakten)...")
    print("-"*40)
    
    test_facts = [
        "HasProperty(water, liquid).",
        "ConsistsOf(H2O, hydrogen, oxygen).",
        "ConsistsOf(NH3, oxygen).",  # Falsch
        "Uses(TCP, handshake).",
        "IsTypeOf(electron, particle)."
    ]
    
    prompt = f"""Validate these 5 facts. Reply with JSON array:
{chr(10).join(f'{i+1}. {f}' for i, f in enumerate(test_facts))}

Format: [{{"id": 1, "valid": true/false, "reason": "..."}}]"""
    
    try:
        start_time = time.time()
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [
                    {'role': 'system', 'content': 'You are a fact validator. Reply only with JSON.'},
                    {'role': 'user', 'content': prompt}
                ],
                'temperature': 0.1,
                'max_tokens': 500
            },
            timeout=20
        )
        
        elapsed = time.time() - start_time
        
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print(f"✅ Validierung in {elapsed:.2f}s erhalten")
            
            # Versuche JSON zu parsen
            try:
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    validations = json.loads(json_match.group())
                    print(f"✅ {len(validations)} Validierungen geparst")
                    
                    # Zeige Ergebnisse
                    for v in validations[:3]:
                        valid = "✓" if v.get('valid') else "✗"
                        print(f"   {valid} Fakt {v.get('id', '?')}: {v.get('reason', '')[:50]}...")
                else:
                    print("⚠️ Keine JSON-Array gefunden in Antwort")
            except:
                print("⚠️ JSON-Parsing fehlgeschlagen")
                print(f"Rohe Antwort: {content[:200]}...")
        else:
            print(f"❌ API Fehler: {response.status_code}")
            print(f"Details: {response.text[:500]}")
            return False
            
    except Exception as e:
        print(f"❌ Test 2 fehlgeschlagen: {e}")
        return False
    
    # Test 3: Rate Limits prüfen
    print("\n📡 Test 3: Rate Limits & Headers...")
    print("-"*40)
    
    try:
        response = requests.post(
            'https://api.deepseek.com/v1/chat/completions',
            headers={
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            },
            json={
                'model': 'deepseek-chat',
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 5
            },
            timeout=10
        )
        
        # Zeige relevante Headers
        headers = response.headers
        print("Response Headers:")
        for key in ['x-ratelimit-limit', 'x-ratelimit-remaining', 'x-ratelimit-reset', 'date']:
            if key in headers:
                print(f"  {key}: {headers[key]}")
        
        # Usage Info wenn vorhanden
        if response.status_code == 200:
            result = response.json()
            if 'usage' in result:
                usage = result['usage']
                print(f"\nToken Usage:")
                print(f"  Prompt: {usage.get('prompt_tokens', 0)}")
                print(f"  Completion: {usage.get('completion_tokens', 0)}")
                print(f"  Total: {usage.get('total_tokens', 0)}")
    except:
        pass
    
    print("\n" + "="*60)
    print("TEST ABGESCHLOSSEN")
    print("="*60)
    
    return True

# Hauptfunktion
if __name__ == "__main__":
    import sys
    
    # Prüfe ob Key als Argument übergeben wurde
    if len(sys.argv) > 1:
        os.environ['DEEPSEEK_API_KEY'] = sys.argv[1]
        print(f"Verwende übergebenen API Key")
    
    success = test_deepseek_api()
    
    if success:
        print("\n✅ DeepSeek API funktioniert!")
        print("\nSie können das Validierungsskript nutzen:")
        print("  python validate_facts_with_llm.py --batch-size 50")
    else:
        print("\n❌ DeepSeek API Test fehlgeschlagen!")
        print("\nAlternativen:")
        print("1. Prüfen Sie Ihren API Key auf https://platform.deepseek.com/")
        print("2. Nutzen Sie Gemini stattdessen (kostenlos):")
        print('   $env:GEMINI_API_KEY = "AIza..."')
        print("3. Oder lokales Ollama:")
        print("   ollama serve")
