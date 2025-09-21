# -*- coding: utf-8 -*-
"""
Erzeugt provider-neutrale LLM-Batches aus stratifizierten Samples + Uncertainty-TopK.
Schreibt Eingabedateien nach validation_batches/{provider}/batch_*.json ohne API-Calls.
"""
import argparse, os, json
from typing import List, Dict

INP_DIR_S='validation_samples/stratified'
INP_TOPK='validation_results/top_k.json'
OUT_DIR='validation_batches'

PROVIDERS=['deepseek','gemini_pro','gpt5']

PROMPT_SCHEMA={
  'items_schema': {
    'statement': 'string',
    'verdict': 'correct|incorrect|uncertain',
    'reasons': 'string',
    'suggested_fix': 'string|null',
    'domain': 'string',
    'confidence': 'number'
  },
  'summary_schema': {
    'count': 'number', 'correct': 'number', 'incorrect': 'number', 'uncertain': 'number', 'acceptance_rate': 'number'
  }
}

PROVIDER_HINT={
  'deepseek': 'Fokus Chemie/Konsistenz; knappe, präzise Gründe; nur JSON',
  'gemini_pro': 'Fokus Bio/Physik; strikte JSON-Ausgabe; max 40 Items',
  'gpt5': 'Generische Qualitätsprüfung; strikte JSON-Ausgabe'
}

def ensure_dir(p:str):
    if not os.path.exists(p): os.makedirs(p)

def load_json(path:str):
    if not os.path.exists(path): return None
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

def collect_samples()->List[Dict]:
    samples=[]
    for name in ['top','rare','reserve']:
        data=load_json(os.path.join(INP_DIR_S, f'{name}.json'))
        if data:
            samples += data.get('samples', [])
    topk=load_json(INP_TOPK) or []
    samples += [{'predicate': s.get('predicate',''), 'statement': s['statement']} for s in topk]
    # Entdoppeln anhand statement
    seen=set(); uniq=[]
    for it in samples:
        s=it.get('statement')
        if s and s not in seen:
            uniq.append(it); seen.add(s)
    return uniq

def chunk(lst, n):
    for i in range(0, len(lst), n):
        yield lst[i:i+n]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--batch-size', type=int, default=40)
    args=ap.parse_args()

    ensure_dir(OUT_DIR)
    all_samples=collect_samples()
    for prov in PROVIDERS:
        outp=os.path.join(OUT_DIR, prov)
        ensure_dir(outp)
        idx=1
        for ch in chunk(all_samples, args.batch_size):
            payload={
                'provider': prov,
                'instructions': PROVIDER_HINT[prov],
                'schema': PROMPT_SCHEMA,
                'samples': ch,
            }
            with open(os.path.join(outp, f'batch_{idx:03d}.json'),'w',encoding='utf-8') as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            idx+=1
    print(f"Batches erzeugt in {OUT_DIR} für Provider: {', '.join(PROVIDERS)}")

if __name__=='__main__':
    main()
