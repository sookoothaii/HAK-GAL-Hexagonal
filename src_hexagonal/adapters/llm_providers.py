"""
LLM Providers for Deep Explanations - FIXED FOR GEMINI-1.5-FLASH
=================================================================
Using gemini-1.5-flash directly (not flash-latest which is rate limited)
"""

import os
import sys
import requests
import subprocess
import json
from typing import Optional, List
from abc import ABC, abstractmethod
from pathlib import Path # HINZUGEFÜGT: Fehlender Import

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> tuple[str, str]:
        pass

class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider - Uses a subprocess proxy to avoid eventlet conflicts."""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.proxy_script_path = Path(__file__).parent / "deepseek_proxy.py"
    
    def is_available(self) -> bool:
        # Debugging-Ausgaben hinzugefügt
        api_key_present = bool(self.api_key)
        proxy_exists = self.proxy_script_path.exists()
        print(f"[DeepSeek.is_available] API Key Present: {api_key_present}, Proxy Exists: {proxy_exists}, Path: {self.proxy_script_path}")
        return api_key_present and proxy_exists
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "DeepSeek"
        if not self.is_available():
            if not self.api_key:
                return "DeepSeek API key not configured", provider_name
            else:
                return f"DeepSeek proxy script not found at {self.proxy_script_path}", provider_name
        
        try:
            print(f"[{provider_name}] Calling proxy script for request...")
            result = subprocess.run(
                [sys.executable, str(self.proxy_script_path), prompt],
                capture_output=True, text=True, timeout=120, encoding='utf-8'
            )

            if result.returncode != 0:
                error_message = f"DeepSeek proxy script failed. Stderr: {result.stderr}"
                return error_message, provider_name

            response_json = json.loads(result.stdout)
            if "error" in response_json:
                return f"Error from proxy: {response_json['error']}", provider_name

            print(f"[{provider_name}] Success via proxy!")
            return response_json['choices'][0]['message']['content'], provider_name

        except subprocess.TimeoutExpired:
            return f"DeepSeek proxy timeout after 120 seconds", provider_name
        except json.JSONDecodeError:
            return f"Failed to decode JSON from proxy. Raw: {result.stdout[:200]}", provider_name
        except Exception as e:
            return f"DeepSeek proxy error: {str(e)}", provider_name

class ClaudeProvider(LLMProvider):
    """Anthropic Claude API provider - Claude 3.5 Sonnet"""
    
    def __init__(self):
        self.api_key = os.environ.get('ANTHROPIC_API_KEY', '')
        self.base_url = "https://api.anthropic.com/v1/messages"
        self.models = ["claude-3-5-sonnet-20241022", "claude-3-5-sonnet-latest", "claude-3-sonnet-20240229"]
        self.timeout = 30
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Claude"
        if not self.is_available():
            return "Claude API key not configured (needs ANTHROPIC_API_KEY)", provider_name
        
        errors = []
        for model in self.models:
            try:
                print(f"[{provider_name}] Trying model {model} (timeout={self.timeout}s)...")
                headers = {
                    "Content-Type": "application/json",
                    "x-api-key": self.api_key,
                    "anthropic-version": "2023-06-01",
                }
                data = {
                    "model": model,
                    "messages": [{"role": "user", "content": prompt}],
                    "max_tokens": 4096,
                    "temperature": 0.7
                }
                response = requests.post(
                    self.base_url, 
                    headers=headers, 
                    json=data, 
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'content' in result and len(result['content']) > 0:
                        text = result['content'][0].get('text', '')
                        if text and len(text) > 100:
                            print(f"[{provider_name}] Success with {model}!")
                            return text, provider_name
                    errors.append(f"{model}: Invalid response structure")
                else:
                    errors.append(f"{model}: HTTP {response.status_code}")
            except Exception as e:
                errors.append(f"{model}: {str(e)[:50]}")
        
        return f"Claude error - tried all models: {', '.join(errors)}", provider_name

class MistralProvider(LLMProvider):
    """Mistral API provider - Currently disabled due to invalid API key"""
    
    def __init__(self):
        self.api_key = os.environ.get('MISTRAL_API_KEY', '')
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-small-latest"
        self.timeout = 30
    
    def is_available(self) -> bool:
        return False
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Mistral"
        return "Mistral API key invalid (401 Unauthorized)", provider_name

class GeminiProvider(LLMProvider):
    """Google Gemini API provider - Tuned model list"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        self.models = ["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash-exp", "gemini-1.5-flash"]
        self.timeout = 30
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Gemini"
        if not self.is_available():
            return "Gemini API key not configured", provider_name
        
        errors = []
        for model in self.models:
            try:
                print(f"[{provider_name}] Trying model {model} (timeout={self.timeout}s)...")
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                data = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 4096, "topK": 40, "topP": 0.95}
                }
                response = requests.post(url, headers={"Content-Type": "application/json"}, json=data, timeout=self.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0].get('text', '')
                        if text and len(text) > 100:
                            print(f"[{provider_name}] Success with {model}!")
                            return text, provider_name
                    errors.append(f"{model}: Invalid response structure")
                else:
                    errors.append(f"{model}: HTTP {response.status_code}")
            except Exception as e:
                errors.append(f"{model}: {str(e)[:50]}")
        
        return f"Gemini error - tried all models: {', '.join(errors)}", provider_name

class OllamaProvider(LLMProvider):
    """Ollama Local LLM Provider - QWEN 2.5 Model"""
    
    def __init__(self):
        self.base_url = "http://localhost:11434"
        self.model = "qwen2.5:14b-instruct-q4_K_M"
        self.timeout = 300
    
    def is_available(self) -> bool:
        try:
            return requests.get(f"{self.base_url}/api/tags", timeout=2).status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Ollama"
        if not self.is_available():
            return "Ollama server not running", provider_name
        
        try:
            print(f"[{provider_name}] Trying model {self.model} (timeout={self.timeout}s)...")
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.7, "top_p": 0.95, "max_tokens": 2048}},
                timeout=self.timeout
            )
            if response.status_code == 200:
                text = response.json().get('response', '')
                if text:
                    print(f"[{provider_name}] Success with {self.model}!")
                    return text, provider_name
                else:
                    return "Ollama returned empty response", provider_name
            else:
                return f"Ollama API error: {response.status_code}", provider_name
        except Exception as e:
            return f"Ollama error: {str(e)}", provider_name

class MultiLLMProvider(LLMProvider):
    """Fallback provider - tries multiple LLMs in priority order."""
    
    def __init__(self, providers: Optional[List[LLMProvider]] = None, offline_mode: bool = False):
        if providers is None:
            if offline_mode:
                providers = [OllamaProvider()]
                print("[MultiLLM] Offline mode: Using only local Ollama provider")
            else:
                providers = [DeepSeekProvider(), ClaudeProvider(), GeminiProvider(), OllamaProvider()]
                print("[MultiLLM] Online mode: Optimized chain (DeepSeek -> Claude -> Gemini)")
        self.providers = providers
    
    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers)
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        final_error = "No LLM provider available."
        
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__.replace('Provider', '')
            if provider.is_available():
                print(f"[MultiLLM] Trying {provider_name} ({i+1}/{len(self.providers)})...")
                try:
                    response_text, _ = provider.generate_response(prompt)
                    error_indicators = ['timeout', 'failed', 'unauthorized', 'not found', 'invalid', 'api error', 'api key']
                    if response_text and len(response_text) > 100 and not any(err in response_text.lower()[:200] for err in error_indicators):
                        return response_text, provider_name
                    else:
                        final_error = f"{provider_name}: {response_text[:100]}"
                        print(f"[MultiLLM] {provider_name} returned error, trying next...")
                except Exception as e:
                    final_error = f"{provider_name}: {str(e)[:100]}"
                    print(f"[MultiLLM] {provider_name} exception, trying next...")
        
        return f"All LLM providers failed. Last error: {final_error}", "None"

def get_llm_provider() -> LLMProvider:
    """Factory function - returns working LLM provider with extended timeouts"""
    # Check if we're in offline mode (no internet or API keys)
    offline_mode = False
    
    # Check for offline indicators
    try:
        # Check for manual offline mode override
        force_offline = os.environ.get('HAK_GAL_OFFLINE_MODE', '').lower() in ['true', '1', 'yes']
        if force_offline:
            print("[MultiLLM] Manual offline mode enabled via HAK_GAL_OFFLINE_MODE")
            offline_mode = True
        else:
            # Try to detect if we're offline by checking if Gemini API key is missing
            gemini_key = os.environ.get('GEMINI_API_KEY', '')
            deepseek_key = os.environ.get('DEEPSEEK_API_KEY', '')
            
            if not gemini_key and not deepseek_key:
                print("[MultiLLM] No API keys found, enabling offline mode")
                offline_mode = True
            else:
                # Test internet connectivity with a quick request
                import requests
                try:
                    requests.get("https://www.google.com", timeout=2)
                    print("[MultiLLM] Internet connection detected, using online mode")
                except:
                    print("[MultiLLM] No internet connection, enabling offline mode")
                    offline_mode = True
                
    except Exception as e:
        print(f"[MultiLLM] Error detecting connectivity: {e}, defaulting to online mode")
        offline_mode = False
    
    return MultiLLMProvider(offline_mode=offline_mode)
