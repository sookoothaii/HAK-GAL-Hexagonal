"""
LLM Providers for Deep Explanations - WITH SSL VERIFICATION
===========================================================
SSL certificate verification enabled for security
"""

import os
import sys
import requests
import certifi
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
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
        # Erhöhte Timeouts: connect=5s, read=45s (konfigurierbar via ENV)
        connect_to = float(os.environ.get('HAK_GAL_LLM_CONNECT_TIMEOUT', '5'))
        read_to = float(os.environ.get('HAK_GAL_LLM_READ_TIMEOUT', '45'))
        self.timeout = (connect_to, read_to)
        # Session mit Retries (429/5xx) und Backoff
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
    
    def is_available(self) -> bool:
        api_key_present = bool(self.api_key)
        print(f"[DeepSeek.is_available] API Key Present: {api_key_present}")
        return api_key_present
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "DeepSeek"
        if not self.is_available():
            return "DeepSeek API key not configured", provider_name
        
        try:
            # Erzwinge IPv4 (Workaround für sporadische NameResolutionError unter Windows/Eventlet)
            try:
                import urllib3.util.connection as uc
                uc.HAS_IPV6 = False
            except Exception:
                pass
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
                # Reduziere Default-Ausgabegröße, kann per Prompt erhöht werden
                "max_tokens": int(os.environ.get('HAK_GAL_LLM_MAXTOKENS', '600')),
                "temperature": 0.7,
                "stream": False
            }
            
            print(f"[{provider_name}] Sending request...")
            response = self.session.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                verify=certifi.where()
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
        # Modelle: aus Konfig oder sinnvolle Defaults
        self.models = [
            "claude-3-7-sonnet-20250219",
            "claude-sonnet-4-20250514",
            "claude-3-5-sonnet-20241022",
            "claude-3-5-sonnet-latest",
            "claude-3-sonnet-20240229",
        ]
        # Optional aus Root-llm_config.json überschreiben
        try:
            from pathlib import Path as _P
            import json as _json
            cfgp = _P("llm_config.json")
            if cfgp.exists():
                with open(cfgp, 'r', encoding='utf-8') as _f:
                    _cfg = _json.load(_f)
                    cm = _cfg.get('claude', {}).get('models')
                    if isinstance(cm, list) and cm:
                        self.models = cm
        except Exception:
            pass
        # Erhöhte Read-Timeouts für Sonnet (große Antworten)
        connect_to = float(os.environ.get('HAK_GAL_LLM_CONNECT_TIMEOUT', '5'))
        read_to = float(os.environ.get('HAK_GAL_LLM_READ_TIMEOUT', '45'))
        self.timeout = (connect_to, read_to)
        self.session = requests.Session()
        retries = Retry(total=3, backoff_factor=0.5, status_forcelist=[429, 500, 502, 503, 504])
        adapter = HTTPAdapter(max_retries=retries)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        # DNS Fallback Cache (DoH)
        self._dns_cache = {}
        self._dns_ttl_seconds = 300.0
        # Optional: Vorab-IPs via ENV (HAK_GAL_CLAUDE_IPS="ip1,ip2")
        try:
            import time as _t
            ips_env = os.environ.get('HAK_GAL_CLAUDE_IPS', '').strip()
            if ips_env:
                seed_ips = [ip.strip() for ip in ips_env.split(',') if ip.strip()]
                if seed_ips:
                    self._dns_cache['api.anthropic.com'] = {"ips": seed_ips, "ts": _t.time()}
                    print(f"[Claude] Using IPs from HAK_GAL_CLAUDE_IPS: {seed_ips}")
        except Exception:
            pass
    
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
                # Erzwinge IPv4 (Workaround für sporadische DNS-Timeouts unter Windows/Eventlet)
                try:
                    import urllib3.util.connection as uc
                    uc.HAS_IPV6 = False
                except Exception:
                    pass
                # Vorab: Stelle sicher, dass DNS für api.anthropic.com auflösbar ist
                self._ensure_dns("api.anthropic.com", preflight_timeout=0.35)
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
                # Proxies ignorieren, certifi-CA nutzen
                self.session.trust_env = False
                # Führe Request in DNS-Override-Kontext aus, falls wir DoH-IPs haben
                response = None
                ips = self._get_cached_ips("api.anthropic.com")
                if ips:
                    response = self._request_with_dns_override(ips, headers, data)
                else:
                    response = self.session.post(
                        self.base_url,
                        headers=headers,
                        json=data,
                        timeout=self.timeout,
                        verify=certifi.where()
                    )
                
                if response.status_code == 200:
                    result = response.json()
                    text = ""
                    # 1) Neues Messages-API: content als Liste mit Text-Blöcken
                    if isinstance(result.get('content'), list) and len(result['content']) > 0:
                        parts = []
                        for item in result['content']:
                            if isinstance(item, dict) and item.get('type') == 'text':
                                t = item.get('text', '')
                                if t:
                                    parts.append(t)
                        text = "\n".join(parts).strip()
                    # 2) Fallback: content als einfacher String
                    if not text and isinstance(result.get('content'), str):
                        text = result['content'].strip()
                    # 3) Fallback: verschachtelt unter 'message'
                    if not text and isinstance(result.get('message'), dict):
                        msg = result['message']
                        if isinstance(msg.get('content'), list):
                            parts = []
                            for item in msg['content']:
                                if isinstance(item, dict) and item.get('type') == 'text':
                                    t = item.get('text', '')
                                    if t:
                                        parts.append(t)
                            text = "\n".join(parts).strip()
                        elif isinstance(msg.get('content'), str):
                            text = msg['content'].strip()
                    if text and len(text) >= 2:
                        print(f"[{provider_name}] Success with {model}!")
                        return text, provider_name
                    # Debug-Ausgabe zur Strukturhilfe
                    try:
                        print(f"[{provider_name}] Debug body: {response.text[:400]}")
                    except Exception:
                        pass
                    errors.append(f"{model}: Invalid response structure")
                else:
                    errors.append(f"{model}: HTTP {response.status_code}")
            except Exception as e:
                errors.append(f"{model}: {str(e)[:50]}")
        
        return f"Claude error - tried all models: {', '.join(errors)}", provider_name

    # --- DNS Robustness Helpers ---
    def _ensure_dns(self, host: str, preflight_timeout: float = 0.3):
        """Try normal DNS quickly; on failure resolve via DoH and cache IPs."""
        import socket, time
        old_to = socket.getdefaulttimeout()
        try:
            socket.setdefaulttimeout(preflight_timeout)
            try:
                socket.gethostbyname(host)
                return  # Normal DNS ok
            except Exception:
                pass
        finally:
            socket.setdefaulttimeout(old_to)
        # Fallback via DoH
        ips = self._resolve_via_doh(host)
        if ips:
            self._dns_cache[host] = {"ips": ips, "ts": time.time()}

    def _get_cached_ips(self, host: str):
        import time
        entry = self._dns_cache.get(host)
        if entry and (time.time() - entry["ts"]) < self._dns_ttl_seconds:
            return entry["ips"]
        return None

    def _resolve_via_doh(self, host: str) -> list:
        """Resolve using public DoH endpoints (Google, Cloudflare)."""
        ips = []
        # 1) Cloudflare DoH via IP (vermeidet lokale DNS) – TLS-Verify optional
        for ip_host in ("1.1.1.1", "1.0.0.1"):
            try:
                r = self.session.get(
                    f"https://{ip_host}/dns-query",
                    params={"name": host, "type": "A"},
                    headers={
                        "accept": "application/dns-json",
                        "host": "cloudflare-dns.com"
                    },
                    timeout=2,
                    verify=False  # bewusst nur für DoH-IP-Fallback
                )
                if r.status_code == 200:
                    j = r.json()
                    for ans in j.get("Answer", []):
                        data = ans.get("data", "")
                        if data and all(ch.isdigit() or ch == '.' for ch in data):
                            ips.append(data)
                    if ips:
                        break
            except Exception:
                continue
        # 2) Falls keine IPs: DoH über Domains (benötigt funktionierendes DNS)
        if not ips:
            try:
                r = self.session.get(
                    "https://dns.google/resolve",
                    params={"name": host, "type": "A"},
                    timeout=2,
                )
                if r.status_code == 200:
                    j = r.json()
                    for ans in j.get("Answer", []):
                        data = ans.get("data", "")
                        if data and all(ch.isdigit() or ch == '.' for ch in data):
                            ips.append(data)
            except Exception:
                pass
        if not ips:
            try:
                r = self.session.get(
                    "https://cloudflare-dns.com/dns-query",
                    params={"name": host, "type": "A"},
                    headers={"accept": "application/dns-json"},
                    timeout=2,
                )
                if r.status_code == 200:
                    j = r.json()
                    for ans in j.get("Answer", []):
                        data = ans.get("data", "")
                        if data and all(ch.isdigit() or ch == '.' for ch in data):
                            ips.append(data)
            except Exception:
                pass
        # 3) Letzter Ausweg: nslookup über Cloudflare-Resolver (keine DNS nötig für 1.1.1.1)
        if not ips:
            try:
                import subprocess, re
                p = subprocess.run(
                    ["nslookup", host, "1.1.1.1"],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                out = p.stdout or ""
                for line in out.splitlines():
                    m = re.search(r"Address:\s*([0-9]{1,3}(?:\.[0-9]{1,3}){3})", line)
                    if m:
                        ip = m.group(1)
                        if ip and ip != "1.1.1.1":
                            ips.append(ip)
                ips = list(dict.fromkeys(ips))
            except Exception:
                pass
        # De-dupe
        return list(dict.fromkeys(ips))

    def _request_with_dns_override(self, ips: list, headers: dict, data: dict):
        """Temporarily override getaddrinfo for api.anthropic.com to use provided IPs."""
        import socket
        original_getaddrinfo = socket.getaddrinfo
        host = "api.anthropic.com"
        def fake_getaddrinfo(node, port, family=0, type=0, proto=0, flags=0):
            if node == host:
                results = []
                for ip in ips:
                    results.append((socket.AF_INET, socket.SOCK_STREAM, socket.IPPROTO_TCP, '', (ip, port)))
                return results or original_getaddrinfo(node, port, family, type, proto, flags)
            return original_getaddrinfo(node, port, family, type, proto, flags)
        socket.getaddrinfo = fake_getaddrinfo
        try:
            return self.session.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=self.timeout,
                verify=certifi.where()
            )
        finally:
            socket.getaddrinfo = original_getaddrinfo

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
        # Eingeschränkt auf stabiles Modell
        self.models = ["gemini-2.0-flash-exp"]
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
        # IPv6/localhost-Probleme vermeiden → IPv4 Loopback explizit
        self.base_url = "http://127.0.0.1:11434"
        # Bevorzugte Reihenfolge: 14b, dann 7b (automatische Auswahl)
        self.preferred_models = ["qwen2.5:14b", "qwen2.5:7b"]
        self.model = None  # wird bei is_available() gesetzt
        self.timeout = 30  # Reduziert auf 30s
        self._is_available = None  # Cache für is_available
    
    def _select_model_from_tags(self, tags_json: dict) -> None:
        try:
            models = tags_json.get("models", [])
            available = {m.get("name") for m in models if isinstance(m, dict)}
            for candidate in self.preferred_models:
                if candidate in available:
                    self.model = candidate
                    print(f"[Ollama] Selected model: {self.model}")
                    return
        except Exception:
            pass
        # Fallback
        if not self.model:
            self.model = "qwen2.5:7b"
    
    def is_available(self) -> bool:
        # Nur positiven Zustand cachen; negatives Ergebnis nicht cachen
        if self._is_available is True:
            return True
            
        try:
            # Schneller Check ob Ollama läuft (mit einmaligem Retry)
            timeouts = [1.0, 2.0]
            response = None
            for to in timeouts:
                try:
                    # Proxies ignorieren für Localhost
                    response = requests.get(
                        f"{self.base_url}/api/tags",
                        timeout=to,
                        proxies={"http": None, "https": None}
                    )
                    if response.status_code == 200:
                        break
                except Exception:
                    response = None
            if response is not None and response.status_code == 200:
                # Modell automatisch bestimmen
                try:
                    tags = response.json()
                except Exception:
                    tags = {}
                self._select_model_from_tags(tags)
                print(f"[Ollama] Server running, selected model: {self.model}")
                self._is_available = True
                return True
            # Fallback: direkter TCP-Connect-Test
            try:
                import socket
                with socket.create_connection(("127.0.0.1", 11434), timeout=0.5):
                    # Dienst läuft, auch wenn /api/tags gerade nicht antwortet
                    if not self.model:
                        self.model = self.preferred_models[0]
                    print(f"[Ollama] TCP check OK, assuming available (model: {self.model})")
                    self._is_available = True
                    return True
            except Exception:
                pass
            # Kein Erfolg → nicht cachen, damit wir im nächsten Versuch neu prüfen
            self._is_available = None
            return False
        except:
            print(f"[Ollama] Server not reachable")
            self._is_available = None
            return False
    
    def generate_response(self, prompt: str) -> tuple[str, str]:
        provider_name = "Ollama"
        if not self.is_available():
            return "Ollama server not running or model not available", provider_name
        # Sicherstellen, dass ein Modell gesetzt ist
        if not self.model:
            # Versuche nochmal Tags zu laden, um bestes Modell zu wählen
            try:
                r = requests.get(f"{self.base_url}/api/tags", timeout=2, proxies={"http": None, "https": None})
                if r.status_code == 200:
                    self._select_model_from_tags(r.json())
            except Exception:
                pass
            if not self.model:
                self.model = self.preferred_models[0]
        
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
        # Lightweight DNS health cache to avoid repeated slow failures (TTL seconds)
        self._dns_health: dict[str, tuple[bool, float]] = {}
        self._dns_ttl_seconds: float = 60.0
        # Map providers to their API hostnames for preflight DNS checks
        self._provider_dns_map = {
            'Groq': 'api.groq.com',
            'DeepSeek': 'api.deepseek.com',
            'Gemini': 'generativelanguage.googleapis.com',
            'Claude': 'api.anthropic.com',
            # Ollama is local; skip DNS
        }
        self._check_dynamic_config()

    def _provider_dns_ok(self, provider_name: str) -> bool:
        """Fast DNS preflight for external providers with small TTL cache.
        Returns True if resolution succeeds quickly; False if it fails.
        Ollama is treated as always OK.
        """
        # Allow Claude to proceed; it has its own DoH + override fallback
        if provider_name == 'Claude':
            return True
        if provider_name == 'Ollama':
            return True
        host = self._provider_dns_map.get(provider_name)
        if not host:
            return True  # Unknown provider -> do not block
        import time as _t
        now = _t.time()
        cached = self._dns_health.get(host)
        if cached and (now - cached[1]) < self._dns_ttl_seconds:
            return cached[0]
        # Perform quick DNS resolution with tight timeout
        try:
            import socket as _s
            old_to = _s.getdefaulttimeout()
            _s.setdefaulttimeout(0.3)
            _s.gethostbyname(host)
            _s.setdefaulttimeout(old_to)
            self._dns_health[host] = (True, now)
            return True
        except Exception:
            try:
                import socket as _s2
                _s2.setdefaulttimeout(None)
            except Exception:
                pass
            self._dns_health[host] = (False, now)
            print(f"[MultiLLM] DNS preflight failed for {provider_name} ({host}) - skipping provider")
            return False
    
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
            # Schneller DNS-Preflight für externe Provider
            if not self._provider_dns_ok(provider_name):
                connection_failures += 1
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
