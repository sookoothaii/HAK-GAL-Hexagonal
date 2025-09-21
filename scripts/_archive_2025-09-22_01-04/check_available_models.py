#!/usr/bin/env python3
"""
Check available OpenAI models
"""

import requests
import json

def check_available_models(api_key: str):
    """Check which models are available in the account"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get('https://api.openai.com/v1/models', headers=headers)
        
        if response.status_code == 200:
            models = response.json()
            print("✅ Available models:")
            print("="*50)
            
            for model in models['data']:
                model_id = model['id']
                if 'gpt' in model_id.lower():
                    print(f"📋 {model_id}")
            
            print("="*50)
            return models['data']
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return None

def test_gpt5_variants(api_key: str):
    """Test different GPT-5 model name variants"""
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    # Test different possible GPT-5 model names
    gpt5_variants = [
        'gpt-5',
        'gpt-5-max',
        'gpt-5-turbo',
        'gpt-5-reasoning',
        'gpt-5-thinking',
        'gpt-5o',
        'gpt-5o-max',
        'gpt-5o-reasoning'
    ]
    
    print("🔍 Testing GPT-5 variants...")
    print("="*50)
    
    for model in gpt5_variants:
        data = {
            'model': model,
            'messages': [{'role': 'user', 'content': 'Test'}],
            'max_tokens': 10
        }
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
            
            if response.status_code == 200:
                print(f"✅ {model} - WORKS!")
                return model
            elif response.status_code == 404:
                print(f"❌ {model} - Not found")
            elif response.status_code == 400:
                print(f"⚠️  {model} - Parameter issue: {response.text}")
            else:
                print(f"❌ {model} - Error {response.status_code}")
                
        except Exception as e:
            print(f"❌ {model} - Exception: {e}")
    
    print("="*50)
    return None

def main():
    api_key = "YOUR_OPENAI_API_KEY_HERE"
    
    print("🔍 CHECKING AVAILABLE OPENAI MODELS")
    print("="*60)
    
    # Check available models
    models = check_available_models(api_key)
    
    if models:
        print(f"\n📊 Total models available: {len(models)}")
    
    print("\n" + "="*60)
    
    # Test GPT-5 variants
    working_model = test_gpt5_variants(api_key)
    
    if working_model:
        print(f"\n🎉 Found working GPT-5 model: {working_model}")
    else:
        print("\n❌ No GPT-5 models found or accessible")

if __name__ == "__main__":
    main()




