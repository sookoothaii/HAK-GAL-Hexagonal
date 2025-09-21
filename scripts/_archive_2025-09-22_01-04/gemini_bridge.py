#!/usr/bin/env python3
"""
GEMINI DIRECT BRIDGE - Bypass für defektes gemini.exe
======================================================
Dieses Script ersetzt gemini.exe komplett
"""

import os
import sys
import json
import subprocess
import tempfile
import logging
from pathlib import Path
from typing import Dict, Any, Optional

from context_loader import get_combined_context

class GeminiBridge:
    """Direkte Python-Bridge zu Gemini API ohne gemini.exe"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY')
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        self.model = "models/gemini-2.0-flash-exp"
        
        # Logging Setup
        logging.basicConfig(
            level=logging.INFO, # Weniger verbose als DEBUG
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('gemini_bridge.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('GeminiBridge')
        
    def test_connection(self) -> bool:
        """Teste ob API erreichbar ist"""
        try:
            import requests
            
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            payload = {
                "contents": [{"parts": [{"text": "Say 'Connection successful'"}]}]
            }
            
            response = requests.post(url, json=payload)
            self.logger.info(f"Connection test: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                self.logger.info(f"Gemini responded: {text}")
                return True
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
            
    def send_message(self, message: str, context: Optional[Dict] = None) -> str:
        """Sende Nachricht an Gemini"""
        try:
            # Lade und kombiniere den statischen Kontext
            static_context = get_combined_context('gemini', base_path='D:\\MCP Mods\\HAK_GAL_HEXAGONAL')
            full_message = static_context + message

            import requests
            
            url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
            
            # Baue Request
            contents = []
            
            # Füge Chat-Historie hinzu wenn vorhanden
            if context and 'history' in context:
                contents.extend(context['history'])
            
            # Füge aktuelle Nachricht hinzu
            contents.append({
                "role": "user",
                "parts": [{"text": full_message}]
            })
            
            payload = {
                "contents": contents,
                "generationConfig": {
                    "temperature": 0.7,
                    "topK": 40,
                    "topP": 0.95,
                    "maxOutputTokens": 2048,
                }
            }
            
            # Sende Request
            response = requests.post(url, json=payload, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                text = result['candidates'][0]['content']['parts'][0]['text']
                self.logger.info(f"Gemini response received: {len(text)} chars")
                return text
            else:
                error = f"API Error: {response.status_code} - {response.text}"
                self.logger.error(error)
                return error
                
        except Exception as e:
            self.logger.error(f"send_message failed: {e}")
            return f"Error: {str(e)}"
    
    # ... (Rest des Codes bleibt unverändert)
    def execute_code(self, code: str, language: str = "python") -> Dict[str, Any]:
        """Führe Code aus (Gemini generiert, lokal ausgeführt)"""
        
        self.logger.info(f"Executing {language} code: {len(code)} chars")
        
        # Erstelle temporäre Datei
        suffix = {
            "python": ".py",
            "javascript": ".js",
            "bash": ".sh",
            "powershell": ".ps1"
        }.get(language, ".txt")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix=suffix, delete=False, encoding='utf-8') as f:
            f.write(code)
            temp_file = f.name
        
        try:
            # Bestimme Executor
            if language == "python":
                cmd = [sys.executable, temp_file]
            elif language == "javascript":
                cmd = ["node", temp_file]
            elif language == "bash":
                cmd = ["bash", temp_file]
            elif language == "powershell":
                cmd = ["powershell", "-File", temp_file]
            else:
                return {"error": f"Unsupported language: {language}"}
            
            # Führe aus
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                encoding='utf-8'
            )
            
            self.logger.info(f"Execution completed: exit code {result.returncode}")
            
            return {
                "stdout": result.stdout,
                "stderr": result.stderr,
                "returncode": result.returncode,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Execution timeout"}
        except Exception as e:
            return {"error": str(e)}
        finally:
            # Aufräumen
            os.unlink(temp_file)
    
    def interactive_mode(self):
        """Interaktiver Modus - ersetzt gemini.exe komplett"""
        
        print("GEMINI BRIDGE - Interactive Mode")
        print("Type 'exit' to quit, 'test' to test connection")
        print("-" * 40)
        
        history = []
        
        while True:
            try:
                user_input = input("\nYou: ").strip()
                
                if user_input.lower() == 'exit':
                    break
                elif user_input.lower() == 'test':
                    if self.test_connection():
                        print("Connection successful!")
                    else:
                        print("Connection failed!")
                    continue
                elif user_input.startswith('/execute '):
                    # Code execution mode
                    code = user_input[9:]
                    result = self.execute_code(code)
                    print(f"Execution result: {result}")
                    continue
                
                # Normale Nachricht
                response = self.send_message(user_input, {"history": history})
                print(f"\nGemini: {response}")
                
                # Update history
                history.append({"role": "user", "parts": [{"text": user_input}]})
                history.append({"role": "model", "parts": [{"text": response}]})
                
                # Behalte nur letzte 10 Nachrichten
                if len(history) > 20:
                    history = history[-20:]
                    
            except KeyboardInterrupt:
                print("\n\nInterrupted. Type 'exit' to quit.")
            except Exception as e:
                print(f"Error: {e}")

# USAGE EXAMPLE
if __name__ == "__main__":
    
    # Check API Key
    if not os.environ.get('GEMINI_API_KEY'):
        print("ERROR: GEMINI_API_KEY not set!")
        print("Set it with: export GEMINI_API_KEY='your-key-here'")
        sys.exit(1)
    
    bridge = GeminiBridge()
    
    # Test mode
    if '--test' in sys.argv:
        print("Running connection test...")
        if bridge.test_connection():
                print("Gemini Bridge is working!")
        else:
            print("Connection failed!")
            
    # Execute mode
    elif '--execute' in sys.argv:
        code = sys.argv[sys.argv.index('--execute') + 1]
        result = bridge.execute_code(code)
        print(json.dumps(result, indent=2))
        
    # Send message mode
    elif '--message' in sys.argv:
        message = sys.argv[sys.argv.index('--message') + 1]
        response = bridge.send_message(message)
        print(response)
        
    # Interactive mode (default)
    else:
        bridge.interactive_mode()