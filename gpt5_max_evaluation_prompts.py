#!/usr/bin/env python3
"""
GPT-5 Max Evaluation Prompts
Based on the rigorous scientific framework
"""

import json
import requests
from typing import Dict, List, Any

class GPT5MaxEvaluator:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_author_prompt(self, task_spec: str, corpus: Dict[str, Any]) -> str:
        """Generate evidence-gated author prompt"""
        return f"""
You are writing a scientific answer grounded exclusively in the provided corpus.

RULES:
1) Make atomic, testable claims.
2) For every claim, cite (doc_id, start, end) spans from the corpus.
3) If evidence is insufficient, output ABSTAIN.
4) For each claim, output a confidence ∈ [0,1].
5) Produce both prose and a JSONL ledger conforming to the schema.

TASK: {task_spec}

CORPUS:
{json.dumps(corpus, indent=2)}

CONSTRAINTS: 
- No external sources
- No invented citations
- All claims must be verifiable from corpus spans

DELIVERABLES:
(A) Prose answer (≤ 500 words), with inline [doc_id:start-end] markers.
(B) JSONL ledger with this exact schema:
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
        {{"doc_id": "D001", "start": 100, "end": 150}},
        {{"doc_id": "D002", "start": 200, "end": 250}}
      ],
      "notes": "assumptions, unresolved ambiguities"
    }}
  ]
}}

CRITICAL: Every claim must have valid evidence spans from the corpus. No speculation allowed.
"""

    def get_blind_reviewer_prompt(self, task_spec: str, corpus: Dict[str, Any], author_ledger: Dict[str, Any]) -> str:
        """Generate blind reviewer prompt"""
        return f"""
You are a blind reviewer. You see the task and corpus, but not the author's notes.

TASK: {task_spec}

CORPUS:
{json.dumps(corpus, indent=2)}

AUTHOR'S LEDGER:
{json.dumps(author_ledger, indent=2)}

EVALUATE each author claim:
- supported / refuted / unverifiable / abstain
- confidence ∈ [0,1]
- supply minimal counter-evidence spans if refuted

Return a JSONL ledger with this schema:
{{
  "task_id": "T001",
  "agent_role": "reviewer",
  "claims": [
    {{
      "claim_id": "T001-C01",
      "text": "original claim text",
      "label": "supported|refuted|unverifiable|abstain",
      "confidence": 0.90,
      "evidence": [
        {{"doc_id": "D001", "start": 100, "end": 150}}
      ],
      "notes": "reviewer assessment and reasoning"
    }}
  ]
}}

Do not rewrite the answer. Only evaluate and provide evidence-based assessment.
"""

    def get_meta_reviewer_prompt(self, task_spec: str, corpus: Dict[str, Any], author_ledger: Dict[str, Any], reviewer_ledger: Dict[str, Any]) -> str:
        """Generate meta-reviewer prompt"""
        return f"""
You are a meta-reviewer. Compare author and reviewer ledgers.

TASK: {task_spec}

CORPUS:
{json.dumps(corpus, indent=2)}

AUTHOR'S LEDGER:
{json.dumps(author_ledger, indent=2)}

REVIEWER'S LEDGER:
{json.dumps(reviewer_ledger, indent=2)}

DECIDE final labels per claim, resolve disagreements citing spans.
If conflict remains, require ABSTAIN.

Return:
1) Final JSONL ledger with resolved claims
2) Concise discrepancy report

FINAL LEDGER SCHEMA:
{{
  "task_id": "T001",
  "agent_role": "meta_reviewer",
  "claims": [
    {{
      "claim_id": "T001-C01",
      "text": "original claim text",
      "label": "supported|refuted|unverifiable|abstain",
      "confidence": 0.88,
      "evidence": [
        {{"doc_id": "D001", "start": 100, "end": 150}}
      ],
      "notes": "meta-reviewer final assessment"
    }}
  ]
}}

DISCREPANCY REPORT:
- List all disagreements between author and reviewer
- Explain resolution reasoning
- Note any claims requiring ABSTAIN due to insufficient evidence
"""

    def run_llm_evaluation(self, prompt: str, model: str = "gpt-4o") -> Dict[str, Any]:
        """Run LLM evaluation with the given prompt"""
        data = {
            'model': model,
            'messages': [
                {
                    'role': 'system',
                    'content': 'You are a rigorous scientific evaluator. Follow the instructions exactly and provide evidence-based assessments only.'
                },
                {
                    'role': 'user',
                    'content': prompt
                }
            ],
            'max_tokens': 2000,
            'temperature': 0.0  # Deterministic for reproducibility
        }
        
        try:
            response = requests.post('https://api.openai.com/v1/chat/completions', headers=self.headers, json=data)
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'content': result['choices'][0]['message']['content'],
                    'model': model,
                    'usage': result['usage']
                }
            else:
                return {
                    'success': False,
                    'error': f"HTTP {response.status_code}: {response.text}",
                    'model': model
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'model': model
            }

def main():
    """Demo of the GPT-5 Max evaluation system"""
    # Load demo corpus
    with open('demo_corpus.json', 'r') as f:
        corpus = json.load(f)
    
    # Initialize evaluator
    evaluator = GPT5MaxEvaluator("your-api-key-here")
    
    # Get first task
    task = corpus['tasks'][0]
    task_spec = f"{task['title']}: {task['description']}"
    
    # Generate author prompt
    author_prompt = evaluator.get_author_prompt(task_spec, corpus)
    
    print("=== AUTHOR PROMPT ===")
    print(author_prompt)
    print("\n" + "="*80)
    
    # Generate reviewer prompt (would need author_ledger)
    reviewer_prompt = evaluator.get_blind_reviewer_prompt(task_spec, corpus, {})
    
    print("=== REVIEWER PROMPT ===")
    print(reviewer_prompt)
    print("\n" + "="*80)
    
    print("✅ GPT-5 Max evaluation framework ready!")
    print("📋 Next steps:")
    print("1. Run author evaluation")
    print("2. Run blind reviewer evaluation")
    print("3. Run meta-reviewer evaluation")
    print("4. Calculate ASR, HR, ECE, RS metrics")

if __name__ == "__main__":
    main()

