"""
LLM Providers for Deep Explanations - WITH 50% MORE TIMEOUT
============================================================
DeepSeek: 90s, Gemini: 70s, Mistral: 70s timeout
"""

import os
import requests
from typing import Optional, List
from abc import ABC, abstractmethod

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> str:
        pass

class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider - CONFIRMED WORKING WITH EXTENDED TIMEOUT"""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
        self.timeout = 90  # Increased from 60 to 90 seconds (+50%)
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            return "DeepSeek API key not configured"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant that provides detailed explanations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500  # Also increased for longer responses
            }
            
            print(f"[DeepSeek] Sending request (timeout={self.timeout}s)...")
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                print("[DeepSeek] Success!")
                return result['choices'][0]['message']['content']
            else:
                error_msg = f"DeepSeek API error: {response.status_code}"
                print(f"[DeepSeek] {error_msg}")
                if response.text:
                    error_msg += f" - {response.text[:200]}"
                return error_msg
                
        except requests.exceptions.Timeout:
            error_msg = f"DeepSeek timeout after {self.timeout} seconds"
            print(f"[DeepSeek] {error_msg}")
            return error_msg
        except requests.exceptions.ConnectionError as e:
            error_msg = f"DeepSeek connection error: {str(e)[:100]}"
            print(f"[DeepSeek] {error_msg}")
            return error_msg
        except Exception as e:
            error_msg = f"DeepSeek error: {str(e)}"
            print(f"[DeepSeek] {error_msg}")
            return error_msg

class MistralProvider(LLMProvider):
    """Mistral API provider - Currently disabled due to invalid API key"""
    
    def __init__(self):
        self.api_key = os.environ.get('MISTRAL_API_KEY', '')
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-small-latest"
        self.timeout = 70  # Increased from 45 to 70 seconds (+50%)
    
    def is_available(self) -> bool:
        # Disabled due to invalid API key (401 error)
        return False
    
    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            return "Mistral API key invalid (401 Unauthorized)"
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": "You are a helpful AI assistant that provides detailed explanations."},
                    {"role": "user", "content": prompt}
                ],
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Mistral API error: {response.status_code}"
                
        except Exception as e:
            return f"Mistral error: {str(e)}"

class GeminiProvider(LLMProvider):
    """Google Gemini API provider - WITH LATEST MODELS AND EXTENDED TIMEOUT"""
    
    def __init__(self):
        self.api_key = os.environ.get('GEMINI_API_KEY', '')
        # Updated model list with latest versions - flash-latest first for speed
        self.models = [
            "gemini-1.5-flash-latest",  # Newest, fastest model - PRIMARY
            "gemini-1.5-flash",          # Stable flash version
            "gemini-1.5-pro-latest",     # Latest pro model
            "gemini-1.5-pro",            # Stable pro version
            "gemini-1.0-pro",            # Legacy fallback
        ]
        self.timeout = 70  # Increased from 45 to 70 seconds (+50%)
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            return "Gemini API key not configured"
        
        errors = []
        
        for model in self.models:
            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={self.api_key}"
                
                data = {
                    "contents": [{
                        "parts": [{
                            "text": prompt
                        }]
                    }],
                    "generationConfig": {
                        "temperature": 0.7,
                        "maxOutputTokens": 1500,  # Increased for longer responses
                        "topK": 40,
                        "topP": 0.95
                    }
                }
                
                print(f"[Gemini] Trying model {model} (timeout={self.timeout}s)...")
                response = requests.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json=data,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"[Gemini] Success with {model}!")
                    
                    # Extract text from response
                    if 'candidates' in result and len(result['candidates']) > 0:
                        candidate = result['candidates'][0]
                        if 'content' in candidate and 'parts' in candidate['content']:
                            text = candidate['content']['parts'][0].get('text', '')
                            if text:
                                return text
                    
                    # Fallback if structure is different
                    errors.append(f"{model}: Unexpected response structure")
                    continue
                    
                elif response.status_code == 404:
                    errors.append(f"{model}: Not found")
                    print(f"[Gemini] {model} not available (404)")
                    continue  # Try next model
                else:
                    errors.append(f"{model}: HTTP {response.status_code}")
                    print(f"[Gemini] {model} error: {response.status_code}")
                    continue
                    
            except requests.exceptions.Timeout:
                errors.append(f"{model}: Timeout after {self.timeout}s")
                print(f"[Gemini] {model} timeout after {self.timeout}s")
                continue
            except Exception as e:
                errors.append(f"{model}: {str(e)[:50]}")
                print(f"[Gemini] {model} exception: {str(e)[:100]}")
                continue
        
        # All models failed
        return f"Gemini error - tried all models: {', '.join(errors)}"

class MultiLLMProvider(LLMProvider):
    """Fallback provider - tries multiple LLMs in priority order with extended timeouts"""
    
    def __init__(self, providers: Optional[List[LLMProvider]] = None):
        if providers is None:
            providers = [
                GeminiProvider(),     # Gemini first - fast with flash-latest
                DeepSeekProvider(),   # DeepSeek second - confirmed working but slower
                # MistralProvider() removed due to invalid API key
            ]
        self.providers = providers
    
    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers)
    
    def generate_response(self, prompt: str) -> str:
        errors = []
        
        for i, provider in enumerate(self.providers):
            provider_name = provider.__class__.__name__.replace('Provider', '')
            
            if provider.is_available():
                print(f"[MultiLLM] Trying {provider_name} ({i+1}/{len(self.providers)})...")
                try:
                    response = provider.generate_response(prompt)
                    
                    # Check if it's a real response (not an error)
                    error_indicators = ['error', 'timeout', 'failed', 'unauthorized', 'not found', 'invalid']
                    if response and not any(err in response.lower() for err in error_indicators):
                        print(f"[MultiLLM] Success with {provider_name}")
                        return response
                    else:
                        errors.append(f"{provider_name}: {response[:100]}")
                        print(f"[MultiLLM] {provider_name} returned error, trying next...")
                        
                except Exception as e:
                    errors.append(f"{provider_name}: {str(e)[:100]}")
                    print(f"[MultiLLM] {provider_name} exception, trying next...")
        
        # All providers failed
        if errors:
            return f"All LLM providers failed:\n" + "\n".join(errors)
        else:
            return "No LLM provider available. Please check API keys in .env file."

def get_llm_provider() -> LLMProvider:
    """Factory function - returns working LLM provider with extended timeouts"""
    return MultiLLMProvider()
