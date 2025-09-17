#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM Governor Adapter - Mock Implementation
==========================================
Mock implementation für LLM Governor während Opus 4.1 die Architektur entwickelt.
Bereit für echte LLM-Integration sobald Design verfügbar ist.
"""

import time
import random
import logging
import json
import os
import subprocess
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

class LLMProvider(Enum):
    """Available LLM Providers"""
    MOCK = "mock"
    GROQ = "groq"
    GEMINI = "gemini"
    OLLAMA = "ollama"

@dataclass
class FactEvaluation:
    """Result of fact evaluation by LLM Governor"""
    fact: str
    score: float  # 0.0 to 1.0
    confidence: float  # 0.0 to 1.0
    reasoning: str
    provider: str
    evaluation_time_ms: int
    metadata: Dict[str, Any]

class LLMGovernorAdapter:
    """
    LLM Governor Adapter - Evaluates facts using LLM providers
    Currently implements Mock provider, ready for real LLM integration
    """
    
    def __init__(self, provider: LLMProvider = LLMProvider.MOCK):
        self.provider = provider
        self.evaluation_count = 0
        self.total_evaluation_time = 0.0
        
        # Mock evaluation patterns for realistic testing
        self.mock_patterns = {
            'high_quality': {
                'score_range': (0.8, 1.0),
                'confidence_range': (0.7, 0.95),
                'keywords': ['scientific', 'research', 'study', 'analysis', 'data']
            },
            'medium_quality': {
                'score_range': (0.5, 0.8),
                'confidence_range': (0.5, 0.8),
                'keywords': ['general', 'common', 'typical', 'standard']
            },
            'low_quality': {
                'score_range': (0.0, 0.5),
                'confidence_range': (0.2, 0.6),
                'keywords': ['speculation', 'opinion', 'unclear', 'vague']
            }
        }
        
        logger.info(f"LLM Governor Adapter initialized with provider: {provider.value}")
    
    def evaluate_fact(self, fact: str, context: Optional[Dict[str, Any]] = None) -> FactEvaluation:
        """
        Evaluate a fact using the configured LLM provider
        
        Args:
            fact: The fact statement to evaluate
            context: Optional context information
            
        Returns:
            FactEvaluation with score, confidence, and reasoning
        """
        start_time = time.time()
        
        if self.provider == LLMProvider.MOCK:
            result = self._evaluate_mock(fact, context)
        elif self.provider == LLMProvider.GROQ:
            result = self._evaluate_groq(fact, context)
        elif self.provider == LLMProvider.GEMINI:
            result = self._evaluate_gemini(fact, context)
        elif self.provider == LLMProvider.OLLAMA:
            result = self._evaluate_ollama(fact, context)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")
        
        evaluation_time_ms = int((time.time() - start_time) * 1000)
        result.evaluation_time_ms = evaluation_time_ms
        
        # Update statistics
        self.evaluation_count += 1
        self.total_evaluation_time += evaluation_time_ms
        
        logger.info(f"Fact evaluated: {fact[:50]}... Score: {result.score:.2f}, Time: {evaluation_time_ms}ms")
        
        return result
    
    def _evaluate_mock(self, fact: str, context: Optional[Dict[str, Any]] = None) -> FactEvaluation:
        """Mock evaluation for testing and development"""
        
        # Determine quality pattern based on fact content
        fact_lower = fact.lower()
        quality_pattern = 'medium_quality'  # default
        
        for pattern_name, pattern_data in self.mock_patterns.items():
            if any(keyword in fact_lower for keyword in pattern_data['keywords']):
                quality_pattern = pattern_name
                break
        
        # Generate realistic scores
        score_range = self.mock_patterns[quality_pattern]['score_range']
        confidence_range = self.mock_patterns[quality_pattern]['confidence_range']
        
        score = random.uniform(*score_range)
        confidence = random.uniform(*confidence_range)
        
        # Generate reasoning based on quality
        reasoning_templates = {
            'high_quality': [
                "This fact appears to be well-researched and scientifically grounded.",
                "The statement contains specific, verifiable information.",
                "This fact demonstrates clear domain knowledge and accuracy."
            ],
            'medium_quality': [
                "This fact seems generally accurate but could benefit from more specificity.",
                "The statement is plausible but lacks detailed supporting evidence.",
                "This appears to be a reasonable general statement."
            ],
            'low_quality': [
                "This fact contains speculative or unverified information.",
                "The statement lacks sufficient detail or supporting evidence.",
                "This fact appears to be based on opinion rather than verifiable data."
            ]
        }
        
        reasoning = random.choice(reasoning_templates[quality_pattern])
        
        return FactEvaluation(
            fact=fact,
            score=score,
            confidence=confidence,
            reasoning=reasoning,
            provider="mock",
            evaluation_time_ms=0,  # Will be set by caller
            metadata={
                'quality_pattern': quality_pattern,
                'context': context or {},
                'mock_evaluation': True
            }
        )
    
    def _evaluate_groq(self, fact: str, context: Optional[Dict[str, Any]] = None) -> FactEvaluation:
        """Groq API evaluation with mixtral-8x7b-32768"""
        try:
            from groq import Groq
            
            # Initialize Groq client
            api_key = os.environ.get('GROQ_API_KEY')
            if not api_key:
                logger.warning("GROQ_API_KEY not found - using mock")
                return self._evaluate_mock(fact, context)
            
            client = Groq(api_key=api_key)
            
            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(fact, context)
            
            # Call Groq API
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a scientific fact evaluator. Respond only with valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"}
            )
            
            # Parse response
            result = json.loads(response.choices[0].message.content)
            
            return FactEvaluation(
                fact=fact,
                score=result.get('overall_score', 0.5),
                confidence=result.get('confidence', 0.8),
                reasoning=result.get('reasoning', 'Groq evaluation'),
                provider="groq",
                evaluation_time_ms=0,  # Will be set by caller
                metadata={
                    'relevance': result.get('relevance', 0.5),
                    'uniqueness': result.get('uniqueness', 0.5),
                    'scientific_value': result.get('scientific_value', 0.5),
                    'recommendation': result.get('recommendation', 'unknown'),
                    'model': 'llama-3.3-70b-versatile'
                }
            )
            
        except ImportError:
            logger.warning("Groq library not installed - using mock")
            return self._evaluate_mock(fact, context)
        except Exception as e:
            logger.error(f"Groq evaluation failed: {e} - using mock")
            return self._evaluate_mock(fact, context)
    
    def _evaluate_gemini(self, fact: str, context: Optional[Dict[str, Any]] = None) -> FactEvaluation:
        """Gemini API evaluation - TODO: Implement when design is ready"""
        # Placeholder for Gemini integration
        logger.warning("Gemini evaluation not yet implemented - using mock")
        return self._evaluate_mock(fact, context)
    
    def _evaluate_ollama(self, fact: str, context: Optional[Dict[str, Any]] = None) -> FactEvaluation:
        """Ollama local evaluation with qwen2.5 models"""
        try:
            import requests
            
            # Select best available model
            model = self._select_ollama_model()
            if not model:
                logger.warning("No Ollama models available - using mock")
                return self._evaluate_mock(fact, context)
            
            # Build evaluation prompt
            prompt = self._build_evaluation_prompt(fact, context)
            
            # Call Ollama API
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": model,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json",
                    "options": {
                        "temperature": 0.1,
                        "top_p": 0.9,
                        "num_predict": 500
                    }
                },
                timeout=30
            )
            
            if response.status_code != 200:
                logger.error(f"Ollama API error: {response.status_code}")
                return self._evaluate_mock(fact, context)
            
            result = response.json()
            
            # Parse JSON response
            try:
                evaluation_data = json.loads(result['response'])
            except json.JSONDecodeError:
                logger.error("Ollama returned invalid JSON - using mock")
                return self._evaluate_mock(fact, context)
            
            return FactEvaluation(
                fact=fact,
                score=evaluation_data.get('overall_score', 0.5),
                confidence=evaluation_data.get('confidence', 0.7),
                reasoning=evaluation_data.get('reasoning', 'Ollama evaluation'),
                provider="ollama",
                evaluation_time_ms=0,  # Will be set by caller
                metadata={
                    'relevance': evaluation_data.get('relevance', 0.5),
                    'uniqueness': evaluation_data.get('uniqueness', 0.5),
                    'scientific_value': evaluation_data.get('scientific_value', 0.5),
                    'recommendation': evaluation_data.get('recommendation', 'unknown'),
                    'model': model
                }
            )
            
        except requests.exceptions.ConnectionError:
            logger.warning("Ollama not running - using mock")
            return self._evaluate_mock(fact, context)
        except Exception as e:
            logger.error(f"Ollama evaluation failed: {e} - using mock")
            return self._evaluate_mock(fact, context)
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get evaluation statistics"""
        avg_time = self.total_evaluation_time / max(self.evaluation_count, 1)
        
        return {
            'provider': self.provider.value,
            'evaluation_count': self.evaluation_count,
            'total_evaluation_time_ms': self.total_evaluation_time,
            'average_evaluation_time_ms': avg_time,
            'status': 'operational' if self.evaluation_count > 0 else 'idle'
        }
    
    def _select_ollama_model(self) -> Optional[str]:
        """Select the best available Ollama model"""
        try:
            result = subprocess.run(['ollama', 'list'], 
                                  capture_output=True, text=True, timeout=5)
            
            if result.returncode != 0:
                return None
            
            models = result.stdout
            
            # Priority order (best to worst)
            priority_models = [
                'qwen2.5:14b',
                'qwen2.5:14b-instruct-q4_K_M', 
                'qwen2.5:7b'
            ]
            
            for model in priority_models:
                if model in models:
                    return model
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to check Ollama models: {e}")
            return None
    
    def _build_evaluation_prompt(self, fact: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build evaluation prompt for LLM"""
        context_str = ""
        if context:
            context_str = f"\nCONTEXT: {json.dumps(context, indent=2)}"
        
        return f"""Evaluate this scientific fact. Respond ONLY with valid JSON.

FACT: {fact}{context_str}

Evaluate on scale 0-1:
- relevance: How relevant to the domain?
- uniqueness: Is this duplicate information? 
- scientific_value: Does this add valuable knowledge?
- overall_score: Weighted average (0.3*relevance + 0.35*uniqueness + 0.25*scientific_value + 0.1*correctness)
- confidence: How confident are you in this evaluation?

JSON Response format:
{{
  "relevance": 0.0-1.0,
  "uniqueness": 0.0-1.0,
  "scientific_value": 0.0-1.0,
  "overall_score": 0.0-1.0,
  "confidence": 0.0-1.0,
  "reasoning": "brief explanation",
  "recommendation": "accept|reject"
}}"""
    
    def health_check(self) -> Dict[str, Any]:
        """Health check for the LLM Governor"""
        # Check provider availability
        provider_status = "available"
        if self.provider == LLMProvider.GROQ:
            if not os.environ.get('GROQ_API_KEY'):
                provider_status = "no_api_key"
        elif self.provider == LLMProvider.OLLAMA:
            if not self._select_ollama_model():
                provider_status = "no_models"
        
        return {
            'status': 'healthy' if provider_status == "available" else 'degraded',
            'provider': self.provider.value,
            'provider_status': provider_status,
            'evaluation_count': self.evaluation_count,
            'ready_for_integration': True
        }

# Test function for development
def test_llm_governor():
    """Test the LLM Governor Adapter"""
    print("🧪 Testing LLM Governor Adapter...")
    
    # Initialize adapter
    governor = LLMGovernorAdapter(LLMProvider.MOCK)
    
    # Test facts
    test_facts = [
        "Water boils at 100 degrees Celsius at sea level.",
        "The Earth orbits around the Sun in approximately 365.25 days.",
        "This is probably some speculative information that might not be accurate.",
        "Scientific research shows that regular exercise improves cardiovascular health."
    ]
    
    print(f"\n📊 Evaluating {len(test_facts)} test facts...")
    
    for i, fact in enumerate(test_facts, 1):
        print(f"\n{i}. Fact: {fact}")
        evaluation = governor.evaluate_fact(fact)
        print(f"   Score: {evaluation.score:.2f}")
        print(f"   Confidence: {evaluation.confidence:.2f}")
        print(f"   Reasoning: {evaluation.reasoning}")
        print(f"   Time: {evaluation.evaluation_time_ms}ms")
    
    # Show statistics
    stats = governor.get_statistics()
    print(f"\n📈 Statistics:")
    print(f"   Provider: {stats['provider']}")
    print(f"   Evaluations: {stats['evaluation_count']}")
    print(f"   Avg Time: {stats['average_evaluation_time_ms']:.1f}ms")
    
    # Health check
    health = governor.health_check()
    print(f"\n🏥 Health Check: {health['status']}")
    
    print("\n✅ LLM Governor Adapter test completed!")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        test_llm_governor()
    else:
        print("LLM Governor Adapter - Mock Implementation")
        print("Usage: python llm_governor_adapter.py --test")
        print("Ready for integration with Opus 4.1 design!")