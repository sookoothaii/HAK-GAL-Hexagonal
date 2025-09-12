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
import time
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
        self.timeout = 3  # Reduziert von 10s auf 3s für schnelleres Failover
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
        self.timeout = (3, 10)  # Reduziert: (3s connect, 10s read) von (10s, 60s)
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
        # FEST auf qwen2.5:7b gesetzt - keine automatische Auswahl mehr
        self.model = "qwen2.5:7b"
        self.timeout = 30  # Reduziert auf 30s
        self._is_available = None  # Cache für is_available
    
    def is_available(self) -> bool:
        if self._is_available is not None:
            return self._is_available
            
        try:
            # Schneller Check ob Ollama läuft
            response = requests.get(f"{self.base_url}/api/tags", timeout=1)
            if response.status_code == 200:
                print(f"[Ollama] Server running, using fixed model: {self.model}")
                self._is_available = True
                return True
            self._is_available = False
            return False
        except:
            print(f"[Ollama] Server not reachable")
            self._is_available = False
            return False
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Ollama"
        if not self.is_available():
            return "Ollama server not running or model not available", provider_name
        
        try:
            print(f"[{provider_name}] Generating with model {self.model}")
            print(f"[{provider_name}] Prompt length: {len(prompt)} chars")
            
            # Vereinfachte API-Anfrage
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "num_predict": 1000  # statt max_tokens
                }
            }
            
            start_time = time.time()
            response = requests.post(
                f"{self.base_url}/api/generate",
                json=data,
                timeout=self.timeout
            )
            
            elapsed = time.time() - start_time
            print(f"[{provider_name}] API call took {elapsed:.1f}s")
            
            if response.status_code == 200:
                result = response.json()
                text = result.get('response', '')
                
                # Debug-Info
                if 'total_duration' in result:
                    total_ms = result['total_duration'] / 1_000_000
                    print(f"[{provider_name}] Ollama reported duration: {total_ms:.0f}ms")
                
                if text:
                    print(f"[{provider_name}] Success! Generated {len(text)} chars")
                    return text, provider_name
                else:
                    print(f"[{provider_name}] Empty response from model")
                    return "Ollama returned empty response", provider_name
            else:
                error_msg = f"Ollama API error: {response.status_code}"
                if response.text:
                    error_detail = response.text[:200]
                    print(f"[{provider_name}] Error details: {error_detail}")
                    error_msg += f" - {error_detail}"
                return error_msg, provider_name
                
        except requests.exceptions.Timeout:
            print(f"[{provider_name}] Timeout after {self.timeout}s - model might be loading")
            return f"Ollama timeout after {self.timeout}s - try again or use smaller model", provider_name
        except Exception as e:
            print(f"[{provider_name}] Exception: {type(e).__name__}: {str(e)}")
            return f"Ollama error: {str(e)[:200]}", provider_name

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
        connection_failures = 0  # Zähle Verbindungsfehler
        
        for i, provider in enumerate(providers_to_use):
            provider_name = provider.__class__.__name__.replace('Provider', '')
            
            # OPTIMIERUNG: Nach 2 Verbindungsfehlern nur noch Ollama probieren
            if connection_failures >= 2 and provider_name != 'Ollama':
                print(f"[MultiLLM] Skipping {provider_name} due to multiple connection failures")
                continue
                
            if provider.is_available():
                print(f"[MultiLLM] Trying {provider_name} ({i+1}/{len(self.providers)})...")
                try:
                    response_text, _ = provider.generate_response(prompt)
                    
                    # ROBUSTE Fehlerprüfung - Prüfe ZUERST ob es ein Fehler ist
                    response_lower = response_text.lower()
                    
                    # Erweiterte Liste von Fehlerindikatoren
                    error_indicators = [
                        'timeout', 'failed', 'unauthorized', 'not found', 'invalid', 
                        'api error', 'api key', 'not configured', 
                        'error:', 'error ', 'connectionerror', 'max retries exceeded', 
                        'ssl', 'nameres', 'httpsconnectionpool', 'couldn\'t connect',
                        'connection refused', 'no such host', 'getaddrinfo failed',
                        'server not running', 'model not available'
                    ]
                    
                    # Spezielle Verbindungsfehler-Indikatoren
                    connection_error_indicators = [
                        'max retries exceeded', 'httpsconnectionpool', 'connectionerror',
                        'connection refused', 'no such host', 'getaddrinfo failed',
                        'name or service not known', 'temporary failure in name resolution'
                    ]
                    
                    # Prüfe ob es definitiv ein Fehler ist
                    is_definitely_error = False
                    is_connection_error = False
                    
                    for err in error_indicators:
                        if err in response_lower:
                            is_definitely_error = True
                            print(f"[MultiLLM] Detected error indicator: '{err}'")
                            # Prüfe ob es ein Verbindungsfehler ist
                            if any(conn_err in response_lower for conn_err in connection_error_indicators):
                                is_connection_error = True
                                connection_failures += 1
                                print(f"[MultiLLM] Detected CONNECTION error (total: {connection_failures})")
                            break
                    
                    # Zusätzliche Prüfung: Wenn Provider-Name + "error" im Text ist
                    if f"{provider_name.lower()} error" in response_lower or \
                       f"{provider_name.lower()}:" in response_lower and "error" in response_lower:
                        is_definitely_error = True
                        print(f"[MultiLLM] Detected provider-specific error")
                    
                    # Mindestlänge für sinnvolle Antwort
                    MIN_GOOD_RESPONSE = 20  # Reduziert für Ollama-Kompatibilität
                    is_valid_length = len(response_text) > MIN_GOOD_RESPONSE
                    
                    # Entscheidungslogik
                    if is_definitely_error:
                        print(f"[MultiLLM] {provider_name} returned error: {response_text[:150]}...")
                        final_error = f"{provider_name}: {response_text[:200]}"
                        continue  # Nächster Provider
                    elif not is_valid_length:
                        print(f"[MultiLLM] {provider_name} response too short ({len(response_text)} chars)")
                        final_error = f"{provider_name}: Response too short"
                        continue  # Nächster Provider
                    else:
                        # Erfolg!
                        print(f"[MultiLLM] Success with {provider_name}! (Length: {len(response_text)})")
                        return response_text, provider_name
                        
                except Exception as e:
                    final_error = f"{provider_name}: Exception - {str(e)[:100]}"
                    print(f"[MultiLLM] {provider_name} exception: {str(e)[:100]}")
                    # Exceptions oft bei Verbindungsproblemen
                    if any(indicator in str(e).lower() for indicator in ['connection', 'timeout', 'refused']):
                        connection_failures += 1
                        print(f"[MultiLLM] Connection exception (total failures: {connection_failures})")
            else:
                print(f"[MultiLLM] {provider_name} not available")
        
        # FALLBACK: Wenn alle Provider fehlgeschlagen sind
        print(f"[MultiLLM] All providers failed. Final error: {final_error}")
        return final_error, "None"

def get_llm_provider() -> LLMProvider:
    """Factory function - returns working LLM provider with FAST offline detection"""
    import socket
    import time
    
    offline_mode = False
    
    # Check for offline indicators
    try:
        # 1. Check for manual offline mode override
        force_offline = os.environ.get('HAK_GAL_OFFLINE_MODE', '').lower() in ['true', '1', 'yes']
        if force_offline:
            print("[get_llm_provider] Manual offline mode enabled via HAK_GAL_OFFLINE_MODE")
            offline_mode = True
        else:
            # 2. SCHNELLER DNS-Check (300ms timeout) - zuverlässigste Methode
            start_time = time.time()
            try:
                # Setze sehr kurzen Timeout für DNS-Auflösung
                socket.setdefaulttimeout(0.3)
                # Versuche DNS-Auflösung einer API-Domain
                socket.gethostbyname("api.groq.com")
                socket.setdefaulttimeout(None)  # Reset to default
                dns_time = time.time() - start_time
                print(f"[get_llm_provider] DNS resolution successful in {dns_time:.3f}s - ONLINE")
            except (socket.gaierror, socket.timeout):
                socket.setdefaulttimeout(None)  # Reset to default
                dns_time = time.time() - start_time
                print(f"[get_llm_provider] DNS resolution failed after {dns_time:.3f}s - OFFLINE DETECTED")
                offline_mode = True
            
            # 3. Wenn online, prüfe noch ob API Keys vorhanden sind
            if not offline_mode:
                has_any_key = any([
                    os.environ.get('GROQ_API_KEY', ''),
                    os.environ.get('DEEPSEEK_API_KEY', ''),
                    os.environ.get('GEMINI_API_KEY', ''),
                    os.environ.get('ANTHROPIC_API_KEY', ''),
                    os.environ.get('TOGETHER_API_KEY', '')
                ])
                
                if not has_any_key:
                    print("[get_llm_provider] No API keys configured - using offline mode")
                    offline_mode = True
                else:
                    print("[get_llm_provider] Online mode: Internet available and API keys found")
                
    except Exception as e:
        print(f"[get_llm_provider] Error in offline detection: {e} - assuming OFFLINE for fast response")
        offline_mode = True  # Bei Fehler: Offline annehmen für schnellste Antwort
    
    # Erstelle Provider mit entsprechendem Modus
    if offline_mode:
        print("[get_llm_provider] FINAL: Starting in OFFLINE mode - Ollama only")
        # Im Offline-Modus: NUR Ollama laden, keine anderen Provider!
        return OllamaProvider()
    else:
        print("[get_llm_provider] FINAL: Starting in ONLINE mode - Full provider chain")
        return MultiLLMProvider(offline_mode=False)
