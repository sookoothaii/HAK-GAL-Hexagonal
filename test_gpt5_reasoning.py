#!/usr/bin/env python3
import requests
import json

def test_gpt5_reasoning():
    api_key = 'YOUR_OPENAI_API_KEY_HERE'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test with GPT-4o first, then try GPT-5 if available
    models_to_try = ['gpt-4o', 'gpt-4o-mini', 'gpt-4-turbo', 'gpt-3.5-turbo']
    
    for model in models_to_try:
        print(f"\n=== Testing {model} ===")
        
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system', 
                    'content': 'Du bist ein führender KI-Forscher und System-Architekt. Analysiere die HAK/GAL-Architektur aus wissenschaftlicher Sicht.'
                },
                {
                    'role': 'user', 
                    'content': 'HAK/GAL zeigt 0.00-0.02ms Query-Zeiten und 100x Performance-Verbesserung durch hexagonale Architektur. Was ist deine wissenschaftliche Einschätzung dieser "Emergent Cognitive Architecture"?'
                }
            ],
            'max_tokens': 500
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
    model, result = test_gpt5_reasoning()
    if model:
        print(f"\n🎉 Best working model: {model}")
    else:
        print("\n❌ No working models found")

