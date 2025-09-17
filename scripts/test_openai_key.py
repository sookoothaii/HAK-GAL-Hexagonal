#!/usr/bin/env python3
import requests
import json

def test_openai_key():
    api_key = 'YOUR_OPENAI_API_KEY_HERE'
    
    headers = {
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }
    
    data = {
        'model': 'gpt-3.5-turbo',
        'messages': [{'role': 'user', 'content': 'Test - antworte mit: API Key funktioniert!'}],
        'max_tokens': 50
    }
    
    try:
        print("Testing OpenAI API Key...")
        response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
        
        print(f'Status Code: {response.status_code}')
        print(f'Response Headers: {dict(response.headers)}')
        
        if response.status_code == 200:
            result = response.json()
            print("✅ SUCCESS: API Key funktioniert!")
            print(f"Response: {result}")
        else:
            print("❌ ERROR: API Key funktioniert nicht!")
            print(f"Error Response: {response.text}")
            
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

if __name__ == "__main__":
    test_openai_key()
