"""
Ollama Adapter for Local LLM Inference
=======================================
Provides a connection to a local Ollama server, enabling the use of
locally-run models like Llama 3.1, Phi-3, etc.
"""

import os
import requests
from typing import Optional, List
from .llm_providers import LLMProvider

class OllamaProvider(LLMProvider):
    """
    Connects to a local Ollama instance for LLM inference.
    """
    
    def __init__(self, model: str = "phi3", timeout: int = 120):
        """
        Initializes the Ollama provider.

        Args:
            model (str): The name of the model to use (e.g., 'phi3', 'llama3.1:13b').
            timeout (int): The timeout in seconds for the API request.
        """
        self.model = model
        # Use 127.0.0.1 instead of localhost for better reliability when network is disabled
        self.base_url = os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434')
        self.timeout = timeout
    
    def is_available(self) -> bool:
        """
        Checks if the Ollama server is running and the model is available.
        """
        # Try both 127.0.0.1 and localhost for maximum compatibility
        urls_to_try = [
            os.environ.get('OLLAMA_BASE_URL', 'http://127.0.0.1:11434'),
            'http://127.0.0.1:11434',
            'http://localhost:11434'
        ]
        
        for url in urls_to_try:
            try:
                # Update base_url if successful
                self.base_url = url
                
                # Check if the server is reachable
                response = requests.get(url, timeout=2)
                if response.status_code != 200:
                    continue

                # Check if the specific model is downloaded
                api_url = f"{url}/api/tags"
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    model_names = [m.get("name") for m in models]
                    if any(self.model in name for name in model_names):
                        print(f"[Ollama] Model '{self.model}' is available locally at {url}.")
                        return True
                    else:
                        print(f"[Ollama] ERROR: Model '{self.model}' not found on the Ollama server.")
                        print(f"[Ollama] Please run: ollama pull {self.model}")
                        return False
                else:
                    continue
            except requests.exceptions.RequestException:
                continue
            except Exception:
                continue
        
        # If we get here, no URL worked
        print(f"[Ollama] Cannot connect to Ollama. Please ensure 'ollama serve' is running.")
        print(f"[Ollama] Tried: {', '.join(urls_to_try)}")
        return False

    def generate_response(self, prompt: str) -> str:
        """
        Generates a response from the local Ollama model.
        """
        if not self.is_available():
            return f"Ollama server or model '{self.model}' is not available."
            
        try:
            api_url = f"{self.base_url}/api/generate"
            
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,  # We want the full response at once
                "options": {
                    "temperature": 0.1,      # SEHR niedrig für Faktentreue
                    "top_p": 0.9,            # Fokussiert auf wahrscheinlichste Tokens
                    "top_k": 40,             # Begrenzt Auswahl
                    "repeat_penalty": 1.1,    # Verhindert Wiederholungen
                    "seed": 42,              # Deterministisch!
                    "num_predict": 1500,     # Max tokens
                }
            }
            
            print(f"[Ollama] Sending request to '{self.model}' (timeout={self.timeout}s)...")
            
            response = requests.post(
                api_url,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[Ollama] Success!")
                return result.get('response', 'Error: Empty response from Ollama.')
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                print(f"[Ollama] {error_msg}")
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                return error_msg

        except requests.exceptions.Timeout:
            error_msg = f"Ollama timeout after {self.timeout} seconds"
            print(f"[Ollama] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"Ollama error: {str(e)}"
            print(f"[Ollama] {error_msg}")
            return error_msg
