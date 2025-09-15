#!/usr/bin/env python3
"""
Test GPT-5 with correct parameters
"""

import requests
import json

def test_gpt5_correct():
    api_key = "YOUR_OPENAI_API_KEY_HERE"
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test GPT-5 with correct parameters
    gpt5_models = ['gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-chat-latest']
    
    for model in gpt5_models:
        print(f"\n🚀 Testing {model} with correct parameters...")
        
        # Use max_completion_tokens instead of max_tokens
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'Du bist GPT-5 und führst eine kritische, evidenzbasierte Analyse durch.'
                },
                {
                    'role': 'user',
                    'content': '''Analysiere HAK/GAL kritisch:

HAK/GAL ist ein Wissensmanagement-System mit:
- 4,242 Fakten in SQLite-Datenbank (2.85 MB)
- 66 Tools verfügbar
- Governance V3 mit 95-100% Success Rate
- MCP Cache mit 33% Hit Rate
- 100% Konsistenz (keine Widersprüche)

KRITISCHE ERKENNTNISSE:
- LLM-Fabulierereien über "0.00-0.02ms Query-Zeiten" entlarvt
- Keine "Emergent Cognitive Architecture" - nur funktionierendes System
- Evidence-Gating zeigt realistische Performance

Gib eine kurze, kritische Einschätzung (max 200 Wörter).'''
                }
            ],
            'max_completion_tokens': 500,  # Correct parameter for GPT-5
            'temperature': 0.0
        }
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS with {model}!")
                print(f"Response: {result['choices'][0]['message']['content']}")
                return model, result
            else:
                print(f"❌ ERROR with {model}: {response.status_code}")
                print(f"Error: {response.text}")
                
        except Exception as e:
            print(f"❌ EXCEPTION with {model}: {e}")
    
    return None, None

if __name__ == "__main__":
    model, result = test_gpt5_correct()
    if model:
        print(f"\n🎉 GPT-5 {model} funktioniert mit korrekten Parametern!")
    else:
        print("\n❌ Kein GPT-5 Modell funktioniert")

