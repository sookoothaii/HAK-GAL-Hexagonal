#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
LLM GOVERNOR DECISION ENGINE
============================
Primärer LLM-basierter Governor für intelligente Engine-Auswahl
Fallback auf Thompson Sampling bei Offline-Modus
"""

import sys
import os
import time
import json
import sqlite3
from typing import Dict, Any, Optional, List
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@dataclass
class SystemState:
    """Aktueller Systemzustand für LLM-Entscheidung"""
    total_facts: int
    recent_facts_count: int
    facts_growth_rate: float
    aethelred_runs: int
    thesis_runs: int
    aethelred_runtime: float
    thesis_runtime: float
    last_decision: str
    current_goals: List[str]
    system_load: float

@dataclass
class LLMDecision:
    """LLM-Entscheidung für Engine-Auswahl"""
    selected_engine: str
    reasoning: str
    confidence: float
    duration_minutes: float
    priority: str
    expected_outcome: str
    llm_provider: str

class LLMGovernorDecisionEngine:
    """LLM-basierter Governor für intelligente Engine-Auswahl"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.decision_history = []
        self.last_system_analysis = None
        
    def analyze_system_state(self) -> SystemState:
        """Analysiere aktuellen Systemzustand"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Fakten-Statistiken
            cursor.execute("SELECT COUNT(*) FROM facts")
            total_facts = cursor.fetchone()[0]
            
            # Neueste Fakten (letzte 100)
            cursor.execute("SELECT COUNT(*) FROM facts LIMIT 100")
            recent_facts_count = cursor.fetchone()[0]
            
            # Berechne Wachstumsrate (vereinfacht)
            facts_growth_rate = min(recent_facts_count / max(total_facts, 1), 1.0)
            
            conn.close()
            
            return SystemState(
                total_facts=total_facts,
                recent_facts_count=recent_facts_count,
                facts_growth_rate=facts_growth_rate,
                aethelred_runs=0,  # Wird vom Governor gesetzt
                thesis_runs=0,     # Wird vom Governor gesetzt
                aethelred_runtime=0.0,
                thesis_runtime=0.0,
                last_decision="none",
                current_goals=["fact_generation", "thesis_analysis", "knowledge_expansion"],
                system_load=0.5  # Vereinfacht
            )
            
        except Exception as e:
            print(f"[ERROR] Failed to analyze system state: {e}")
            return SystemState(
                total_facts=0, recent_facts_count=0, facts_growth_rate=0.0,
                aethelred_runs=0, thesis_runs=0, aethelred_runtime=0.0, thesis_runtime=0.0,
                last_decision="error", current_goals=[], system_load=0.0
            )
    
    def create_decision_prompt(self, system_state: SystemState, engine_status: Dict) -> str:
        """Erstelle Prompt für LLM-Entscheidung"""
        prompt = f"""
You are an intelligent Governor for a dual-engine knowledge system. Your job is to decide which engine to run next based on the current system state.

SYSTEM STATE:
- Total facts in database: {system_state.total_facts}
- Recent facts generated: {system_state.recent_facts_count}
- Facts growth rate: {system_state.facts_growth_rate:.2f}
- Aethelred runs: {system_state.aethelred_runs} (runtime: {system_state.aethelred_runtime:.1f}s)
- Thesis runs: {system_state.thesis_runs} (runtime: {system_state.thesis_runtime:.1f}s)
- Last decision: {system_state.last_decision}
- Current goals: {', '.join(system_state.current_goals)}

ENGINE STATUS:
- Aethelred running: {engine_status.get('aethelred_running', False)}
- Thesis running: {engine_status.get('thesis_running', False)}

ENGINE CAPABILITIES:
1. AETHELRED ENGINE:
   - Generates new facts using LLM (DeepSeek/Gemini/Ollama)
   - Expands knowledge base with factual information
   - High fact generation rate
   - Best for: Knowledge expansion, fact discovery

2. THESIS ENGINE:
   - Analyzes existing facts to generate logical theses
   - Uses LLM to validate and prove theses
   - Creates higher-order knowledge from facts
   - Best for: Knowledge synthesis, logical reasoning

DECISION CRITERIA:
- If facts are growing well (>1000 new facts), focus on thesis analysis
- If fact generation is slow (<500 new facts), prioritize Aethelred
- If both engines have run recently, choose based on knowledge gaps
- Balance between fact generation and knowledge synthesis

Respond with ONLY a JSON object:
{{
    "selected_engine": "aethelred|thesis|wait",
    "reasoning": "Detailed explanation of your decision",
    "confidence": 0.0-1.0,
    "duration_minutes": 1-10,
    "priority": "high|medium|low",
    "expected_outcome": "What you expect this engine to achieve"
}}

Make an intelligent decision based on the current state.
"""
        return prompt
    
    def call_llm_for_decision(self, prompt: str) -> Optional[LLMDecision]:
        """Rufe LLM für Engine-Entscheidung auf"""
        # Versuche verschiedene LLM Provider
        providers = ['deepseek', 'groq', 'gemini', 'ollama']
        
        for provider in providers:
            try:
                result = self.call_specific_llm(provider, prompt)
                if result:
                    return LLMDecision(
                        selected_engine=result['selected_engine'],
                        reasoning=result['reasoning'],
                        confidence=result['confidence'],
                        duration_minutes=result['duration_minutes'],
                        priority=result['priority'],
                        expected_outcome=result['expected_outcome'],
                        llm_provider=provider
                    )
            except Exception as e:
                print(f"[WARNING] {provider} failed: {e}")
                continue
        
        print("[ERROR] All LLM providers failed")
        return None
    
    def call_specific_llm(self, provider: str, prompt: str) -> Optional[Dict]:
        """Rufe spezifischen LLM Provider auf"""
        if provider == 'deepseek':
            return self.call_deepseek_llm(prompt)
        elif provider == 'groq':
            return self.call_groq_llm(prompt)
        elif provider == 'gemini':
            return self.call_gemini_llm(prompt)
        elif provider == 'ollama':
            return self.call_ollama_llm(prompt)
        return None
    
    def call_deepseek_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe DeepSeek LLM auf"""
        try:
            import requests
            import os
            
            api_key = os.environ.get('DEEPSEEK_API_KEY')
            if not api_key:
                raise Exception("No DeepSeek API key")
            
            response = requests.post(
                "https://api.deepseek.com/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "deepseek-chat",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 800
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    parsed = json.loads(content)
                    return parsed
                except:
                    # Fallback: Extract decision from text
                    if "aethelred" in content.lower():
                        return {"selected_engine": "aethelred", "confidence": 0.7, "reasoning": content[:200]}
                    elif "thesis" in content.lower():
                        return {"selected_engine": "thesis", "confidence": 0.7, "reasoning": content[:200]}
                    else:
                        return {"selected_engine": "wait", "confidence": 0.5, "reasoning": content[:200]}
            
        except Exception as e:
            print(f"[DEEPSEEK] Error: {e}")
            return None
    
    def call_groq_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Groq LLM auf"""
        try:
            import requests
            import os
            
            api_key = os.environ.get('GROQ_API_KEY')
            if not api_key:
                raise Exception("No Groq API key")
            
            response = requests.post(
                "https://api.groq.com/openai/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "llama-3.3-70b",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 800
                },
                timeout=20
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                try:
                    parsed = json.loads(content)
                    return parsed
                except:
                    if "aethelred" in content.lower():
                        return {"selected_engine": "aethelred", "confidence": 0.8, "reasoning": content[:200]}
                    elif "thesis" in content.lower():
                        return {"selected_engine": "thesis", "confidence": 0.8, "reasoning": content[:200]}
                    else:
                        return {"selected_engine": "wait", "confidence": 0.5, "reasoning": content[:200]}
            
        except Exception as e:
            print(f"[GROQ] Error: {e}")
            return None
    
    def call_gemini_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Gemini LLM auf"""
        try:
            from adapters.llm_providers import GeminiProvider
            
            gemini = GeminiProvider()
            if gemini.is_available():
                response = gemini.generate_response(prompt)
                if isinstance(response, tuple):
                    response = response[0]
                
                try:
                    parsed = json.loads(response)
                    return parsed
                except:
                    if "aethelred" in response.lower():
                        return {"selected_engine": "aethelred", "confidence": 0.6, "reasoning": response[:200]}
                    elif "thesis" in response.lower():
                        return {"selected_engine": "thesis", "confidence": 0.6, "reasoning": response[:200]}
                    else:
                        return {"selected_engine": "wait", "confidence": 0.4, "reasoning": response[:200]}
            
        except Exception as e:
            print(f"[GEMINI] Error: {e}")
            return None
    
    def call_ollama_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Ollama LLM auf"""
        try:
            from adapters.ollama_adapter import OllamaProvider
            
            ollama = OllamaProvider(model="qwen2.5:7b", timeout=20)
            if ollama.is_available():
                response = ollama.generate_response(prompt)
                if isinstance(response, tuple):
                    response = response[0]
                
                try:
                    parsed = json.loads(response)
                    return parsed
                except:
                    if "aethelred" in response.lower():
                        return {"selected_engine": "aethelred", "confidence": 0.5, "reasoning": response[:200]}
                    elif "thesis" in response.lower():
                        return {"selected_engine": "thesis", "confidence": 0.5, "reasoning": response[:200]}
                    else:
                        return {"selected_engine": "wait", "confidence": 0.3, "reasoning": response[:200]}
            
        except Exception as e:
            print(f"[OLLAMA] Error: {e}")
            return None
    
    def make_decision(self, engine_status: Dict) -> Dict[str, Any]:
        """Mache intelligente Engine-Entscheidung"""
        print("[LLM GOVERNOR] Making intelligent decision...")
        
        # Analysiere Systemzustand
        system_state = self.analyze_system_state()
        
        # Erstelle Prompt
        prompt = self.create_decision_prompt(system_state, engine_status)
        
        # Rufe LLM auf
        llm_decision = self.call_llm_for_decision(prompt)
        
        if llm_decision:
            print(f"[LLM DECISION] {llm_decision.selected_engine.upper()}")
            print(f"[REASONING] {llm_decision.reasoning}")
            print(f"[CONFIDENCE] {llm_decision.confidence:.2f}")
            print(f"[PROVIDER] {llm_decision.llm_provider}")
            
            # Konvertiere zu Governor-Format
            decision = {
                'timestamp': time.time(),
                'action': 'start_engine' if llm_decision.selected_engine != 'wait' else 'wait',
                'engine': llm_decision.selected_engine if llm_decision.selected_engine != 'wait' else None,
                'duration': llm_decision.duration_minutes * 60,  # Convert to seconds
                'confidence': llm_decision.confidence,
                'reasoning': [llm_decision.reasoning],
                'llm_provider': llm_decision.llm_provider,
                'priority': llm_decision.priority,
                'expected_outcome': llm_decision.expected_outcome
            }
            
            # Speichere Entscheidung
            self.decision_history.append(decision)
            return decision
        
        else:
            print("[LLM GOVERNOR] LLM failed, falling back to Thompson Sampling")
            return self.thompson_fallback(engine_status)
    
    def thompson_fallback(self, engine_status: Dict) -> Dict[str, Any]:
        """Thompson Sampling Fallback bei LLM-Ausfall"""
        import random
        
        # Einfache Thompson Sampling Logik
        aethelred_score = random.betavariate(3, 1)  # Leicht bevorzugt
        thesis_score = random.betavariate(2, 2)     # Ausbalanciert
        
        if aethelred_score > thesis_score:
            selected_engine = 'aethelred'
            confidence = aethelred_score
        else:
            selected_engine = 'thesis'
            confidence = thesis_score
        
        return {
            'timestamp': time.time(),
            'action': 'start_engine',
            'engine': selected_engine,
            'duration': random.uniform(180, 600),  # 3-10 minutes
            'confidence': confidence,
            'reasoning': [f'Thompson Sampling fallback: {selected_engine} selected'],
            'llm_provider': 'thompson_sampling',
            'priority': 'medium',
            'expected_outcome': 'Standard engine operation'
        }
    
    def get_decision_history(self) -> List[Dict]:
        """Hole Entscheidungshistorie"""
        return self.decision_history
    
    def get_decision_statistics(self) -> Dict[str, Any]:
        """Hole Entscheidungsstatistiken"""
        if not self.decision_history:
            return {}
        
        total_decisions = len(self.decision_history)
        llm_decisions = len([d for d in self.decision_history if d.get('llm_provider') != 'thompson_sampling'])
        thompson_decisions = total_decisions - llm_decisions
        
        engine_counts = {}
        for decision in self.decision_history:
            engine = decision.get('engine', 'wait')
            engine_counts[engine] = engine_counts.get(engine, 0) + 1
        
        return {
            'total_decisions': total_decisions,
            'llm_decisions': llm_decisions,
            'thompson_decisions': thompson_decisions,
            'llm_success_rate': llm_decisions / total_decisions if total_decisions > 0 else 0,
            'engine_distribution': engine_counts,
            'last_decision': self.decision_history[-1] if self.decision_history else None
        }

def main():
    """Test der LLM Governor Decision Engine"""
    engine = LLMGovernorDecisionEngine(r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db")
    
    # Simuliere Engine Status
    engine_status = {
        'aethelred_running': False,
        'thesis_running': False
    }
    
    # Mache Entscheidung
    decision = engine.make_decision(engine_status)
    print(f"\n[FINAL DECISION] {decision}")
    
    # Zeige Statistiken
    stats = engine.get_decision_statistics()
    print(f"\n[STATISTICS] {stats}")

if __name__ == "__main__":
    main()







