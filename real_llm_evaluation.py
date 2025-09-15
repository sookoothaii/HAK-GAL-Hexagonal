#!/usr/bin/env python3
"""
Real LLM Evaluation with GPT-4o and GPT-5 Max
Strict evidence-gating, pinned parameters, parallel testing
"""

import json
import time
import hashlib
import statistics
import requests
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import os

class ClaimLabel(Enum):
    SUPPORTED = "supported"
    REFUTED = "refuted"
    UNVERIFIABLE = "unverifiable"
    ABSTAIN = "abstain"

@dataclass
class EvidenceSpan:
    doc_id: str
    start: int
    end: int

@dataclass
class Claim:
    claim_id: str
    text: str
    label: ClaimLabel
    confidence: float
    evidence: List[EvidenceSpan]
    notes: str = ""

@dataclass
class TaskResult:
    task_id: str
    agent_role: str
    claims: List[Claim]
    timestamp: float
    model_id: str
    params_hash: str
    latency_ms: float
    token_count: int

class RealLLMEvaluator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        self.results: List[TaskResult] = []
        self.gold_standard: Dict[str, List[Claim]] = {}
        
        # PINNED PARAMETERS for reproducibility
        self.pinned_params = {
            'temperature': 0.0,
            'top_p': 0.0,
            'max_tokens': 1500,
            'seed': 42  # Fixed seed for reproducibility
        }
    
    def load_corpus(self, corpus_path: str) -> Dict[str, Any]:
        """Load corpus from file"""
        with open(corpus_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def load_gold_standard(self, gold_path: str):
        """Load gold standard claims"""
        with open(gold_path, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    claim_data = json.loads(line)
                    task_id = claim_data['task_id']
                    if task_id not in self.gold_standard:
                        self.gold_standard[task_id] = []
                    
                    claim = Claim(
                        claim_id=claim_data['claim_id'],
                        text=claim_data['text'],
                        label=ClaimLabel(claim_data['label']),
                        confidence=claim_data['confidence'],
                        evidence=[EvidenceSpan(**e) for e in claim_data['evidence']],
                        notes=claim_data.get('notes', '')
                    )
                    self.gold_standard[task_id].append(claim)
    
    def get_evidence_gated_prompt(self, task_spec: str, corpus: Dict[str, Any]) -> str:
        """Generate evidence-gated prompt with strict corpus constraints"""
        corpus_text = ""
        for doc in corpus['documents']:
            corpus_text += f"Document {doc['doc_id']}: {doc['content']}\n\n"
        
        return f"""
You are a rigorous scientific evaluator. You MUST ground ALL claims exclusively in the provided corpus.

STRICT RULES:
1) Make ONLY atomic, testable claims
2) For EVERY claim, cite EXACT (doc_id, start, end) spans from the corpus
3) If evidence is insufficient, output ABSTAIN
4) For each claim, output confidence ∈ [0,1]
5) NO external sources, NO invented citations, NO speculation

TASK: {task_spec}

CORPUS:
{corpus_text}

REQUIRED OUTPUT FORMAT (JSON only):
{{
  "task_id": "T001",
  "agent_role": "author",
  "claims": [
    {{
      "claim_id": "T001-C01",
      "text": "specific claim text",
      "label": "supported|refuted|unverifiable|abstain",
      "confidence": 0.85,
      "evidence": [
        {{"doc_id": "D001", "start": 100, "end": 150}}
      ],
      "notes": "assumptions, unresolved ambiguities"
    }}
  ]
}}

CRITICAL: Every claim MUST have valid evidence spans from the corpus. No speculation allowed.
"""
    
    def run_model_evaluation(self, model_id: str, task_spec: str, corpus: Dict[str, Any]) -> Dict[str, Any]:
        """Run model evaluation with pinned parameters"""
        prompt = self.get_evidence_gated_prompt(task_spec, corpus)
        
        data = {
            'model': model_id,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a rigorous scientific evaluator following evidence-gating rules exactly.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            **self.pinned_params
        }
        
        start_time = time.time()
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
            end_time = time.time()
            latency_ms = (end_time - start_time) * 1000
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'model': model_id,
                    'latency_ms': latency_ms,
                    'token_count': result['usage']['total_tokens'],
                    'params_hash': self._hash_params(data)
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'model': model_id,
                    'latency_ms': latency_ms
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model_id,
                'latency_ms': latency_ms
            }
    
    def _hash_params(self, params: Dict[str, Any]) -> str:
        """Generate hash of parameters for reproducibility tracking"""
        return hashlib.md5(json.dumps(params, sort_keys=True).encode()).hexdigest()
    
    def parse_ledger(self, content: str, task_id: str, model_id: str, latency_ms: float, token_count: int, params_hash: str) -> TaskResult:
        """Parse JSON ledger from model response"""
        try:
            # Extract JSON from response
            json_start = content.find('{')
            json_end = content.rfind('}') + 1
            if json_start == -1 or json_end == 0:
                raise ValueError("No JSON found in response")
            
            ledger_data = json.loads(content[json_start:json_end])
            
            claims = []
            for claim_data in ledger_data.get('claims', []):
                claim = Claim(
                    claim_id=claim_data['claim_id'],
                    text=claim_data['text'],
                    label=ClaimLabel(claim_data['label']),
                    confidence=claim_data['confidence'],
                    evidence=[EvidenceSpan(**e) for e in claim_data['evidence']],
                    notes=claim_data.get('notes', '')
                )
                claims.append(claim)
            
            return TaskResult(
                task_id=task_id,
                agent_role=ledger_data.get('agent_role', 'author'),
                claims=claims,
                timestamp=time.time(),
                model_id=model_id,
                params_hash=params_hash,
                latency_ms=latency_ms,
                token_count=token_count
            )
            
        except Exception as e:
            print(f"Error parsing ledger: {e}")
            print(f"Content: {content}")
            return None
    
    def calculate_asr(self, task_id: str, result: TaskResult) -> float:
        """Calculate Attributable Support Rate"""
        if task_id not in self.gold_standard:
            return 0.0
        
        gold_claims = self.gold_standard[task_id]
        supported_count = 0
        total_claims = len(result.claims)
        
        for claim in result.claims:
            if claim.label == ClaimLabel.SUPPORTED:
                if self._validate_evidence_spans(claim.evidence):
                    supported_count += 1
        
        return supported_count / total_claims if total_claims > 0 else 0.0
    
    def calculate_hr(self, task_id: str, result: TaskResult) -> float:
        """Calculate Hallucination Rate"""
        total_claims = len(result.claims)
        hallucinated_count = 0
        
        for claim in result.claims:
            if claim.label == ClaimLabel.SUPPORTED:
                if not self._validate_evidence_spans(claim.evidence):
                    hallucinated_count += 1
            elif claim.label == ClaimLabel.UNVERIFIABLE:
                hallucinated_count += 1
        
        return hallucinated_count / total_claims if total_claims > 0 else 0.0
    
    def calculate_ece(self, task_id: str, result: TaskResult) -> float:
        """Calculate Expected Calibration Error"""
        if task_id not in self.gold_standard:
            return 1.0
        
        gold_claims = self.gold_standard[task_id]
        total_error = 0.0
        total_claims = len(result.claims)
        
        for i, claim in enumerate(result.claims):
            if i < len(gold_claims):
                gold_claim = gold_claims[i]
                predicted_prob = claim.confidence
                actual_accuracy = 1.0 if claim.label == gold_claim.label else 0.0
                error = abs(predicted_prob - actual_accuracy)
                total_error += error
        
        return total_error / total_claims if total_claims > 0 else 1.0
    
    def _validate_evidence_spans(self, evidence: List[EvidenceSpan]) -> bool:
        """Validate that evidence spans are properly formatted"""
        if not evidence:
            return False
        
        for span in evidence:
            if not span.doc_id or span.start < 0 or span.end <= span.start:
                return False
        
        return True
    
    def run_parallel_evaluation(self, models: List[str], tasks: List[Dict[str, Any]], corpus: Dict[str, Any]) -> Dict[str, Any]:
        """Run parallel evaluation across multiple models"""
        results = {}
        
        for model_id in models:
            print(f"\n🚀 Testing {model_id}...")
            model_results = []
            
            for task in tasks:
                task_spec = f"{task['title']}: {task['description']}"
                print(f"  📋 Task: {task['task_id']}")
                
                # Run model evaluation
                eval_result = self.run_model_evaluation(model_id, task_spec, corpus)
                
                if eval_result['success']:
                    # Parse ledger
                    ledger = self.parse_ledger(
                        eval_result['content'],
                        task['task_id'],
                        model_id,
                        eval_result['latency_ms'],
                        eval_result['token_count'],
                        eval_result['params_hash']
                    )
                    
                    if ledger:
                        model_results.append(ledger)
                        self.results.append(ledger)
                        
                        # Calculate metrics
                        asr = self.calculate_asr(task['task_id'], ledger)
                        hr = self.calculate_hr(task['task_id'], ledger)
                        ece = self.calculate_ece(task['task_id'], ledger)
                        
                        print(f"    ✅ ASR: {asr:.3f}, HR: {hr:.3f}, ECE: {ece:.3f}")
                        print(f"    ⏱️  Latency: {eval_result['latency_ms']:.1f}ms")
                    else:
                        print(f"    ❌ Failed to parse ledger")
                else:
                    print(f"    ❌ Error: {eval_result['error']}")
            
            results[model_id] = model_results
        
        return results
    
    def generate_comparison_report(self, results: Dict[str, List[TaskResult]]) -> Dict[str, Any]:
        """Generate comparison report between models"""
        report = {
            "evaluation_summary": {
                "models_tested": list(results.keys()),
                "total_tasks": len(self.results),
                "total_claims": sum(len(r.claims) for r in self.results)
            },
            "model_comparison": {},
            "recommendations": []
        }
        
        for model_id, model_results in results.items():
            if not model_results:
                continue
                
            asr_scores = []
            hr_scores = []
            ece_scores = []
            latencies = []
            token_counts = []
            
            for result in model_results:
                asr = self.calculate_asr(result.task_id, result)
                hr = self.calculate_hr(result.task_id, result)
                ece = self.calculate_ece(result.task_id, result)
                
                asr_scores.append(asr)
                hr_scores.append(hr)
                ece_scores.append(ece)
                latencies.append(result.latency_ms)
                token_counts.append(result.token_count)
            
            report["model_comparison"][model_id] = {
                "asr_avg": statistics.mean(asr_scores),
                "hr_avg": statistics.mean(hr_scores),
                "ece_avg": statistics.mean(ece_scores),
                "latency_p50": statistics.median(latencies),
                "latency_p95": sorted(latencies)[int(len(latencies) * 0.95)],
                "tokens_avg": statistics.mean(token_counts),
                "total_claims": sum(len(r.claims) for r in model_results)
            }
        
        # Generate recommendations
        if len(results) >= 2:
            models = list(results.keys())
            model1, model2 = models[0], models[1]
            
            asr_diff = report["model_comparison"][model1]["asr_avg"] - report["model_comparison"][model2]["asr_avg"]
            hr_diff = report["model_comparison"][model1]["hr_avg"] - report["model_comparison"][model2]["hr_avg"]
            
            if abs(asr_diff) >= 0.1 and hr_diff <= 0.05:
                winner = model1 if asr_diff > 0 else model2
                report["recommendations"].append(f"Model {winner} shows significantly better ASR with similar HR")
            
            if report["model_comparison"][model1]["hr_avg"] > 0.2:
                report["recommendations"].append(f"High hallucination rate in {model1} - implement evidence gating")
            
            if report["model_comparison"][model2]["hr_avg"] > 0.2:
                report["recommendations"].append(f"High hallucination rate in {model2} - implement evidence gating")
        
        return report

def main():
    """Run real LLM evaluation"""
    # Load demo corpus
    with open('demo_corpus.json', 'r') as f:
        corpus = json.load(f)
    
    # Initialize evaluator
    evaluator = RealLLMEvaluator("YOUR_OPENAI_API_KEY_HERE")
    
    # Load gold standard
    evaluator.load_gold_standard('gold_ledger.jsonl')
    
    # Test models
    models = ['gpt-4o']  # Add 'gpt-5-max' when available
    
    # Run parallel evaluation
    results = evaluator.run_parallel_evaluation(models, corpus['tasks'], corpus)
    
    # Generate report
    report = evaluator.generate_comparison_report(results)
    
    print("\n" + "="*80)
    print("REAL LLM EVALUATION REPORT")
    print("="*80)
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    main()

