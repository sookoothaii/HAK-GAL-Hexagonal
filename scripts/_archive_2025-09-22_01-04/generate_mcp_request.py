#!/usr/bin/env python3
"""
Generate correct MCP API request for GPT-5
"""

import json

def generate_mcp_request():
    """Generate the correct JSON structure for MCP API request"""
    
    request_data = {
        "model": "gpt-5-chat-latest",
        "messages": [
            {
                "role": "system",
                "content": "Du bist GPT-5 und führst eine kritische, evidenzbasierte Analyse durch."
            },
            {
                "role": "user",
                "content": "Was ist HAK/GAL basierend auf den empirischen Daten (4,242 Fakten, 66 Tools, 2.85 MB Datenbank)? Kurze, kritische Antwort bitte."
            }
        ],
        "max_completion_tokens": 300,
        "temperature": 1.0
    }
    
    headers = {
        "Authorization": "Bearer YOUR_OPENAI_API_KEY_HERE",
        "Content-Type": "application/json"
    }
    
    print("=== MCP API REQUEST STRUCTURE ===")
    print("URL: https://api.openai.com/v1/chat/completions")
    print("METHOD: POST")
    print("\nHEADERS:")
    print(json.dumps(headers, indent=2))
    print("\nDATA:")
    print(json.dumps(request_data, indent=2))
    
    return request_data, headers

if __name__ == "__main__":
    generate_mcp_request()




