"""
LLM Providers for Deep Explanations - WITH SSL VERIFICATION
===========================================================
SSL certificate verification enabled for security
"""

import os
import sys
import requests
# SSL warnings are now shown for security awareness
import subprocess
import json
from typing import Optional, List
from abc import ABC, abstractmethod
from pathlib import Path

class LLMProvider(ABC):
    """Base class for LLM providers"""
    
    @abstractmethod
    def is_available(self) -> bool:
        pass
    
    @abstractmethod
    def generate_response(self, prompt: str) -> tuple[str, str]:
        pass

class GroqProvider(LLMProvider):
    """Groq API provider - Llama 3.1 8B Instant with LPU technology (extremely fast and free)"""
    
    def __init__(self):
        self.api_key = os.environ.get('GROQ_API_KEY', '')
        self.base_url = "https://api.groq.com/openai/v1/chat/completions"
        self.timeout = 10  # Fast timeout for LPU
        self.model = "llama-3.1-8b-instant"  # Current free tier model
    
    def is_available(self) -> bool:
        api_key_present = bool(self.api_key)
        print(f"[Groq.is_available] API Key Present: {api_key_present}")
        return api_key_present
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Groq"
        if not self.is_available():
            return "Groq API key not configured", provider_name
        
        try:
            print(f"[{provider_name}] Calling Llama 3.1 8B Instant via Groq API...")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7,
                "stream": False
            }
            
            response = requests.post(
                self.base_url, 
                headers=headers, 
                json=data, 
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if content:
                    return content, provider_name
                else:
                    return "Empty response from Groq", provider_name
            else:
                return f"Groq API error: {response.status_code} - {response.text[:200]}", provider_name
                
        except requests.exceptions.Timeout:
            return f"Groq API timeout after {self.timeout}s", provider_name
        except Exception as e:
            return f"Groq API error: {str(e)[:200]}", provider_name

class TogetherAIProvider(LLMProvider):
    """Together AI provider - Mixtral 8x7B with $25 free credits"""
    
    def __init__(self):
        self.api_key = os.environ.get('TOGETHER_API_KEY', '')
        self.base_url = "https://api.together.xyz/v1/chat/completions"
        self.timeout = 15
        self.model = "mistralai/Mixtral-8x7B-Instruct-v0.1"
    
    def is_available(self) -> bool:
        api_key_present = bool(self.api_key)
        print(f"[TogetherAI.is_available] API Key Present: {api_key_present}")
        return api_key_present
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "TogetherAI"
        if not self.is_available():
            return "Together AI API key not configured", provider_name
        
        try:
            print(f"[{provider_name}] Calling Mixtral 8x7B via Together AI...")
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": self.model,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
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
                content = result.get('choices', [{}])[0].get('message', {}).get('content', '')
                if content:
                    return content, provider_name
                else:
                    return "Empty response from Together AI", provider_name
            else:
                return f"Together AI API error: {response.status_code} - {response.text[:200]}", provider_name
                
        except requests.exceptions.Timeout:
            return f"Together AI API timeout after {self.timeout}s", provider_name
        except Exception as e:
            return f"Together AI API error: {str(e)[:200]}", provider_name

class DeepSeekProvider(LLMProvider):
    """DeepSeek API provider - Fixed implementation based on successful test."""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.timeout = (5, 30)  # (connect timeout, read timeout)
        self.session = requests.Session()  # Reuse connection
    
    def is_available(self) -> bool:
        api_key_present = bool(self.api_key)
        print(f"[DeepSeek.is_available] API Key Present: {api_key_present}")
        return api_key_present
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "DeepSeek"
        if not self.is_available():
            return "DeepSeek API key not configured", provider_name
        
        try:
            print(f"[{provider_name}] Direct API call...")
            
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'User-Agent': 'HAK-GAL/1.0'
            }
            
            # EXACT configuration that worked in test
            data = {
                "model": "deepseek-chat",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.7,
                "stream": False
            }
            
            print(f"[{provider_name}] Sending request...")
            response = self.session.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                verify=True
            )
            
            print(f"[{provider_name}] Response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                if "choices" in result and len(result["choices"]) > 0:
                    content = result["choices"][0]["message"]["content"]
                    print(f"[{provider_name}] Success! Response time: {response.elapsed.total_seconds():.2f}s")
                    return content, provider_name
                else:
                    return f"DeepSeek: Invalid response format", provider_name
            else:
                error_text = response.text[:200] if response.text else "No error details"
                return f"DeepSeek API error {response.status_code}: {error_text}", provider_name
                
        except requests.exceptions.ConnectTimeout:
            return "DeepSeek: Connection timeout (couldn't connect)", provider_name
        except requests.exceptions.ReadTimeout:
            return "DeepSeek: Read timeout (connected but slow response)", provider_name
        except Exception as e:
            return f"DeepSeek error: {type(e).__name__}: {str(e)[:100]}", provider_name

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
                        if text and len(text) > 10:  # Reduced threshold
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
        self.timeout = 15
    
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
                    "generationConfig": {"temperature": 0.7, "maxOutputTokens": 1000, "topK": 40, "topP": 0.95}
                }
                response = requests.post(url, headers={"Content-Type": "application/json"}, json=data, timeout=self.timeout)
                
                if response.status_code == 200:
                    result = response.json()
                    if 'candidates' in result and len(result['candidates']) > 0:
                        text = result['candidates'][0]['content']['parts'][0].get('text', '')
                        if text and len(text) > 10:  # Reduced threshold
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
        self.model = os.environ.get("OLLAMA_MODEL", "qwen2.5:7b")
        self.timeout = 300
    
    def is_available(self) -> bool:
        try:
            # For localhost, SSL verification might fail - handle gracefully
            if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
                # Try with SSL first, fallback to without
                try:
                    return requests.get(f"{self.base_url}/api/tags", timeout=2).status_code == 200
                except requests.exceptions.SSLError:
                    return requests.get(f"{self.base_url}/api/tags", timeout=2, verify=False).status_code == 200
            else:
                return requests.get(f"{self.base_url}/api/tags", timeout=2).status_code == 200
        except:
            return False
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Ollama"
        if not self.is_available():
            return "Ollama server not running", provider_name
        
        try:
            print(f"[{provider_name}] Trying model {self.model} (timeout={self.timeout}s)...")
            # For localhost, handle SSL gracefully
            verify_ssl = True
            if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
                verify_ssl = True  # Try with SSL first
                
            try:
                response = requests.post(
                    f"{self.base_url}/api/generate",
                    json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.7, "top_p": 0.95, "max_tokens": 2048}},
                    timeout=self.timeout,
                    verify=verify_ssl
                )
            except requests.exceptions.SSLError as ssl_err:
                if "localhost" in self.base_url or "127.0.0.1" in self.base_url:
                    print(f"[{provider_name}] SSL verification failed for localhost, retrying without...")
                    response = requests.post(
                        f"{self.base_url}/api/generate",
                        json={"model": self.model, "prompt": prompt, "stream": False, "options": {"temperature": 0.7, "top_p": 0.95, "max_tokens": 2048}},
                        timeout=self.timeout,
                        verify=False
                    )
                else:
                    raise ssl_err
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
                # User-defined chain: groq-deepseek-gemini-claude-ollama
                providers = [
                    GroqProvider(),           # 1. Groq - FREE & FAST (LPU)
                    DeepSeekProvider(),       # 2. DeepSeek - Fast paid option
                    GeminiProvider(),         # 3. Gemini - Google's free tier
                    ClaudeProvider(),         # 4. Claude - Anthropic
                    OllamaProvider()          # 5. Ollama - Local fallback
                ]
                print("[MultiLLM] Online mode: Custom chain (Groq -> DeepSeek -> Gemini -> Claude -> Ollama)")
        self.providers = providers
        self._check_dynamic_config()
    
    def _check_dynamic_config(self):
        """Check for dynamic LLM configuration"""
        try:
            # Check if there's a config file or environment variable for dynamic config
            import json
            config_path = Path("llm_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    print(f"[MultiLLM] Loaded dynamic configuration from {config_path}")
                    # TODO: Apply configuration
        except Exception as e:
            print(f"[MultiLLM] No dynamic configuration found: {e}")
    
    def _get_enabled_providers(self) -> List[LLMProvider]:
        """Get list of enabled providers based on configuration"""
        # Check for runtime configuration
        try:
            # Try to load configuration from a shared location or API
            # This could be enhanced to read from Redis, DB, or shared memory
            import json
            config_path = Path("llm_config.json")
            if config_path.exists():
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    enabled_ids = config.get('enabled_providers', [])
                    provider_order = config.get('provider_order', [])
                    api_keys = config.get('api_keys', {})
                    
                    # Filter and order providers
                    provider_map = {p.__class__.__name__.replace('Provider', '').lower(): p for p in self.providers}
                    ordered_providers = []
                    
                    for provider_id in provider_order:
                        if provider_id.lower() in provider_map and provider_id in enabled_ids:
                            provider = provider_map[provider_id.lower()]
                            # Apply temporary API key if available
                            if provider_id in api_keys and hasattr(provider, 'api_key'):
                                provider.api_key = api_keys[provider_id]
                            ordered_providers.append(provider)
                    
                    if ordered_providers:
                        print(f"[MultiLLM] Using configured providers: {[p.__class__.__name__ for p in ordered_providers]}")
                        return ordered_providers
        except Exception as e:
            # Fallback to default providers
            pass
        
        # Return all providers by default
        return self.providers
    
    def is_available(self) -> bool:
        return any(p.is_available() for p in self._get_enabled_providers())
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        final_error = "No LLM provider available."
        providers_to_use = self._get_enabled_providers()
        
        for i, provider in enumerate(providers_to_use):
            provider_name = provider.__class__.__name__.replace('Provider', '')
            if provider.is_available():
                print(f"[MultiLLM] Trying {provider_name} ({i+1}/{len(self.providers)})...")
                try:
                    response_text, _ = provider.generate_response(prompt)
                    # Check if response is valid (not an error message)
                    # Only check for actual error messages, not content
                    error_indicators = ['timeout', 'failed', 'unauthorized', 'not found', 'invalid', 'api error', 'api key', 'not configured']
                    is_error = any(err in response_text.lower() for err in error_indicators)
                    is_valid_length = len(response_text) > 10  # Low threshold
                    
                    if response_text and is_valid_length and not is_error:
                        print(f"[MultiLLM] Success with {provider_name}! (Length: {len(response_text)})")
                        return response_text, provider_name
                    else:
                        final_error = f"{provider_name}: {response_text}"
                        print(f"[MultiLLM] {provider_name} returned: {response_text}")
                        print(f"[MultiLLM] (Length: {len(response_text)}, IsError: {is_error}), trying next...")
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
