#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
DeepSeek API Proxy - Minimales Skript für saubere Netzwerkaufrufe.
Nimmt einen Prompt als Kommandozeilen-Argument entgegen und gibt die JSON-Antwort der API auf stdout aus.
"""

import os
import sys
import json
import requests
from pathlib import Path
from dotenv import load_dotenv

def main():
    # Lade Umgebungsvariablen, um den API-Schlüssel zu erhalten
    project_root = Path(__file__).parent.parent.parent
    env_path = project_root / '.env'
    if env_path.exists():
        load_dotenv(dotenv_path=env_path)
    
    api_key = os.environ.get('DEEPSEEK_API_KEY', '')
    if not api_key:
        print(json.dumps({"error": "DEEPSEEK_API_KEY not found"}))
        sys.exit(1)

    # Lese den Prompt vom Kommandozeilen-Argument
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No prompt provided"}))
        sys.exit(1)
    
    prompt = sys.argv[1]

    # Führe den API-Aufruf durch
    try:
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        data = {
            "model": "deepseek-chat",
            "messages": [
                {"role": "system", "content": "You are a helpful AI assistant that provides detailed explanations."},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.7,
            "max_tokens": 1500
        }
        
        response = requests.post(
            "https://api.deepseek.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=90  # Das Timeout hier ist entscheidend
        )
        
        response.raise_for_status() # Löst einen Fehler aus für 4xx/5xx Statuscodes
        
        # Gebe die erfolgreiche JSON-Antwort auf stdout aus
        print(response.text)

    except requests.exceptions.RequestException as e:
        print(json.dumps({"error": f"Request failed: {str(e)}"}))
        sys.exit(1)

if __name__ == "__main__":
    main()
