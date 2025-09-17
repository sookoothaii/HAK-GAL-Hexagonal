#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
THESIS LLM PROOF VALIDATOR
=========================
Validiert generierte Thesen mit LLM-Hilfe und beweist sie
"""

import sys
import os
import sqlite3
import time
import argparse
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

@dataclass
class ProofResult:
    """Ergebnis einer LLM-Beweisführung"""
    thesis_id: int
    thesis_statement: str
    proof_status: str  # proven, disproven, uncertain, needs_more_evidence
    proof_text: str
    confidence: float
    llm_provider: str
    validated_at: str

class ThesisLLMProofValidator:
    """Validiert Thesen mit LLM-Hilfe"""
    
    def __init__(self):
        self.db_path = r"D:\MCP Mods\HAK_GAL_HEXAGONAL\hexagonal_kb.db"
        
    def load_pending_theses(self, limit: int = 10) -> List[Dict]:
        """Lade Thesen die noch bewiesen werden müssen"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, statement, supporting_facts, confidence, category
                FROM theses 
                WHERE status = 'pending'
                ORDER BY confidence DESC, created_at ASC
                LIMIT ?
            """, (limit,))
            
            theses = []
            for row in cursor.fetchall():
                theses.append({
                    'id': row[0],
                    'statement': row[1],
                    'supporting_facts': row[2].split('; ') if row[2] else [],
                    'confidence': row[3],
                    'category': row[4]
                })
            
            conn.close()
            return theses
            
        except Exception as e:
            print(f"[ERROR] Failed to load theses: {e}")
            return []
    
    def get_relevant_facts(self, thesis_statement: str, limit: int = 20) -> List[str]:
        """Hole relevante Fakten für die These"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Extrahiere Keywords aus der These
            keywords = thesis_statement.lower().split()
            keyword_conditions = []
            for keyword in keywords:
                if len(keyword) > 3:  # Ignoriere kurze Wörter
                    keyword_conditions.append(f"statement LIKE '%{keyword}%'")
            
            if not keyword_conditions:
                return []
            
            where_clause = " OR ".join(keyword_conditions)
            
            cursor.execute(f"""
                SELECT statement 
                FROM facts 
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
            
            facts = [row[0] for row in cursor.fetchall()]
            conn.close()
            return facts
            
        except Exception as e:
            print(f"[ERROR] Failed to get relevant facts: {e}")
            return []
    
    def validate_thesis_with_llm(self, thesis: Dict) -> Optional[ProofResult]:
        """Validiere eine These mit LLM"""
        thesis_statement = thesis['statement']
        supporting_facts = thesis['supporting_facts']
        
        # Hole relevante Fakten aus der Knowledge Base
        relevant_facts = self.get_relevant_facts(thesis_statement)
        
        # Erstelle Prompt für LLM
        prompt = self.create_validation_prompt(thesis_statement, supporting_facts, relevant_facts)
        
        # Versuche verschiedene LLM Provider
        llm_result = self.call_llm_for_validation(prompt)
        
        if llm_result:
            return ProofResult(
                thesis_id=thesis['id'],
                thesis_statement=thesis_statement,
                proof_status=llm_result['status'],
                proof_text=llm_result['proof'],
                confidence=llm_result['confidence'],
                llm_provider=llm_result['provider'],
                validated_at=datetime.now().isoformat()
            )
        
        return None
    
    def create_validation_prompt(self, thesis: str, supporting_facts: List[str], relevant_facts: List[str]) -> str:
        """Erstelle Prompt für LLM-Validierung"""
        prompt = f"""
You are a logical reasoning expert. Please analyze the following thesis and determine if it can be proven or disproven based on the available evidence.

THESIS TO VALIDATE:
{thesis}

SUPPORTING FACTS (from pattern analysis):
{chr(10).join(f"- {fact}" for fact in supporting_facts)}

RELEVANT FACTS (from knowledge base):
{chr(10).join(f"- {fact}" for fact in relevant_facts)}

Please provide your analysis in the following JSON format:
{{
    "status": "proven|disproven|uncertain|needs_more_evidence",
    "confidence": 0.0-1.0,
    "proof": "Detailed explanation of your reasoning",
    "reasoning": "Step-by-step logical analysis",
    "evidence_quality": "strong|moderate|weak",
    "recommendations": "What additional evidence would strengthen this thesis"
}}

Focus on:
1. Logical consistency of the thesis
2. Quality and relevance of supporting evidence
3. Potential counter-evidence
4. Logical gaps or assumptions

Respond ONLY with valid JSON.
"""
        return prompt
    
    def call_llm_for_validation(self, prompt: str) -> Optional[Dict]:
        """Rufe LLM für Validierung auf"""
        # Versuche verschiedene LLM Provider - DEEPSEEK ZUERST!
        providers = ['deepseek', 'groq', 'gemini', 'ollama']
        
        for provider in providers:
            try:
                if provider == 'deepseek':
                    result = self.call_deepseek_llm(prompt)
                elif provider == 'groq':
                    result = self.call_groq_llm(prompt)
                elif provider == 'gemini':
                    result = self.call_gemini_llm(prompt)
                elif provider == 'ollama':
                    result = self.call_ollama_llm(prompt)
                
                if result:
                    result['provider'] = provider
                    return result
                    
            except Exception as e:
                print(f"[WARNING] {provider} failed: {e}")
                continue
        
        print("[ERROR] All LLM providers failed")
        return None
    
    def call_deepseek_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe DeepSeek LLM auf"""
        try:
            # Versuche DeepSeek Integration
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
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                import json
                try:
                    parsed = json.loads(content)
                    return parsed
                except:
                    # Fallback: Extract status from text
                    if "proven" in content.lower():
                        return {"status": "proven", "confidence": 0.9, "proof": content}
                    elif "disproven" in content.lower():
                        return {"status": "disproven", "confidence": 0.9, "proof": content}
                    else:
                        return {"status": "uncertain", "confidence": 0.6, "proof": content}
            
        except Exception as e:
            print(f"[DEEPSEEK] Error: {e}")
            return None
    
    def call_groq_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Groq LLM auf"""
        try:
            # Versuche Groq Integration
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
                    "max_tokens": 1000
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                import json
                try:
                    parsed = json.loads(content)
                    return parsed
                except:
                    # Fallback: Extract status from text
                    if "proven" in content.lower():
                        return {"status": "proven", "confidence": 0.8, "proof": content}
                    elif "disproven" in content.lower():
                        return {"status": "disproven", "confidence": 0.8, "proof": content}
                    else:
                        return {"status": "uncertain", "confidence": 0.5, "proof": content}
            
        except Exception as e:
            print(f"[GROQ] Error: {e}")
            return None
    
    def call_gemini_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Gemini LLM auf"""
        try:
            # Versuche Gemini Integration
            from adapters.llm_providers import GeminiProvider
            
            gemini = GeminiProvider()
            if gemini.is_available():
                response = gemini.generate_response(prompt)
                if isinstance(response, tuple):
                    response = response[0]
                
                # Parse JSON response
                import json
                try:
                    parsed = json.loads(response)
                    return parsed
                except:
                    # Fallback parsing
                    if "proven" in response.lower():
                        return {"status": "proven", "confidence": 0.7, "proof": response}
                    else:
                        return {"status": "uncertain", "confidence": 0.5, "proof": response}
            
        except Exception as e:
            print(f"[GEMINI] Error: {e}")
            return None
    
    def call_ollama_llm(self, prompt: str) -> Optional[Dict]:
        """Rufe Ollama LLM auf"""
        try:
            from adapters.ollama_adapter import OllamaProvider
            
            ollama = OllamaProvider(model="qwen2.5:7b", timeout=30)
            if ollama.is_available():
                response = ollama.generate_response(prompt)
                if isinstance(response, tuple):
                    response = response[0]
                
                # Parse JSON response
                import json
                try:
                    parsed = json.loads(response)
                    return parsed
                except:
                    # Fallback parsing
                    if "proven" in response.lower():
                        return {"status": "proven", "confidence": 0.6, "proof": response}
                    else:
                        return {"status": "uncertain", "confidence": 0.4, "proof": response}
            
        except Exception as e:
            print(f"[OLLAMA] Error: {e}")
            return None
    
    def save_proof_result(self, result: ProofResult) -> bool:
        """Speichere Beweisergebnis in der Datenbank"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Erstelle Tabelle für Beweise falls nicht vorhanden
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS thesis_proofs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thesis_id INTEGER,
                    thesis_statement TEXT,
                    proof_status TEXT,
                    proof_text TEXT,
                    confidence REAL,
                    llm_provider TEXT,
                    validated_at TEXT,
                    FOREIGN KEY (thesis_id) REFERENCES theses (id)
                )
            """)
            
            # Füge Beweis hinzu
            cursor.execute("""
                INSERT INTO thesis_proofs 
                (thesis_id, thesis_statement, proof_status, proof_text, confidence, llm_provider, validated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                result.thesis_id,
                result.thesis_statement,
                result.proof_status,
                result.proof_text,
                result.confidence,
                result.llm_provider,
                result.validated_at
            ))
            
            # Aktualisiere Status der These
            cursor.execute("""
                UPDATE theses 
                SET status = ?
                WHERE id = ?
            """, (result.proof_status, result.thesis_id))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to save proof result: {e}")
            return False
    
    def run(self, duration_minutes: float = 5.0):
        """Hauptschleife für Thesen-Validierung"""
        print(f"[START] Thesis LLM Proof Validator - {duration_minutes} minutes")
        print("[INFO] Validating theses with LLM assistance")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        validated_count = 0
        
        while time.time() < end_time:
            print(f"\n=== Validation Round ===")
            
            # Lade Thesen die validiert werden müssen
            theses = self.load_pending_theses(5)
            if not theses:
                print("[INFO] No pending theses to validate")
                time.sleep(30)
                continue
            
            print(f"[LOADED] {len(theses)} theses to validate")
            
            # Validiere Thesen
            for i, thesis in enumerate(theses):
                print(f"[VALIDATING {i+1}/{len(theses)}] {thesis['statement'][:80]}...")
                
                result = self.validate_thesis_with_llm(thesis)
                if result:
                    if self.save_proof_result(result):
                        validated_count += 1
                        print(f"[PROOF] {result.proof_status.upper()} (confidence: {result.confidence:.2f})")
                        print(f"[PROOF] Provider: {result.llm_provider}")
                    else:
                        print("[ERROR] Failed to save proof result")
                else:
                    print("[SKIP] LLM validation failed")
                
                # Pause zwischen Validierungen
                time.sleep(5)
            
            # Pause zwischen Runden
            if time.time() < end_time:
                time.sleep(30)
        
        print(f"\n[DONE] Validated {validated_count} theses")

def main():
    parser = argparse.ArgumentParser(description="Thesis LLM Proof Validator")
    parser.add_argument("-d", "--duration", type=float, default=0.1, help="Duration in minutes")
    parser.add_argument("-p", "--port", type=int, default=5002, help="Port (unused)")
    args = parser.parse_args()
    
    validator = ThesisLLMProofValidator()
    validator.run(duration_minutes=args.duration)

if __name__ == "__main__":
    main()
