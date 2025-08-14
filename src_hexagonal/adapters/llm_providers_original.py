"""
LLM Providers for Deep Explanations
====================================
Provides DeepSeek and Mistral integration
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
    """DeepSeek API provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('DEEPSEEK_API_KEY', '')
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
        self.model = "deepseek-chat"
    
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
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"DeepSeek API error: {response.status_code}"
                
        except Exception as e:
            return f"DeepSeek error: {str(e)}"

class MistralProvider(LLMProvider):
    """Mistral API provider"""
    
    def __init__(self):
        self.api_key = os.environ.get('MISTRAL_API_KEY', '')
        self.base_url = "https://api.mistral.ai/v1/chat/completions"
        self.model = "mistral-medium"
    
    def is_available(self) -> bool:
        return bool(self.api_key)
    
    def generate_response(self, prompt: str) -> str:
        if not self.is_available():
            return "Mistral API key not configured"
        
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
                "max_tokens": 1000
            }
            
            response = requests.post(
                self.base_url,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"Mistral API error: {response.status_code}"
                
        except Exception as e:
            return f"Mistral error: {str(e)}"

class MultiLLMProvider(LLMProvider):
    """Fallback provider that tries multiple LLMs"""
    
    def __init__(self, providers: Optional[List[LLMProvider]] = None):
        if providers is None:
            providers = [
                DeepSeekProvider(),
                MistralProvider()
            ]
        self.providers = providers
    
    def is_available(self) -> bool:
        return any(p.is_available() for p in self.providers)
    
    def generate_response(self, prompt: str) -> str:
        for provider in self.providers:
            if provider.is_available():
                try:
                    response = provider.generate_response(prompt)
                    if response and not response.startswith("Error") and "API error" not in response:
                        return response
                except Exception:
                    continue
        
        return "No LLM provider available. Please configure DEEPSEEK_API_KEY or MISTRAL_API_KEY in environment."

def get_llm_provider() -> LLMProvider:
    """Factory function to get the best available LLM provider"""
    return MultiLLMProvider()
