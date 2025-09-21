# -*- coding: utf-8 -*-
"""
Führt DeepSeek-, Gemini-, GPT5-Validierungen und lokale Heuristik zusammen.
Ergebnis: validation_results/final_consensus.json, cleanup_proposals.sql, summary.md
"""
import os, json, statistics
from typing import Dict, List

INP_DS='validation_results/deepseek_chemistry.json'
INP_GM='validation_results/gemini_pro.json'
INP_GPT='validation_results/gpt5.json'
INP_SELF='validation_results/self_report.json'
OUT_DIR='validation_results'

def load_json(path:str):
    if not os.path.exists(path): return None
    with open(path,'r',encoding='utf-8') as f:
        return json.load(f)

def to_dict(items:List[Dict])->Dict[str,Dict]:
    return { it['statement']: it for it in items }

def majority_vote(verdicts:List[str])->str:
    if not verdicts: return 'uncertain'
    counts={v: verdicts.count(v) for v in set(verdicts)}
    return max(counts, key=counts.get)

def main():
    ds=load_json(INP_DS) or {'items': [], 'summary': {}}
    gm=load_json(INP_GM) or {'items': [], 'summary': {}}
    gp=load_json(INP_GPT) or {'items': [], 'summary': {}}
    selfrep=load_json(INP_SELF) or {}

    ds_map=to_dict(ds.get('items',[]))
    gm_map=to_dict(gm.get('items',[]))
    gp_map=to_dict(gp.get('items',[]))

    all_statements=set(ds_map.keys()) | set(gm_map.keys()) | set(gp_map.keys())
    consensus=[]
    cleanup_sql=[]
    correct_cnt=incorrect_cnt=uncertain_cnt=0

    for s in all_statements:
        votes=[]; confs=[]; domains=[]; reasons=[]; fix=None
        for src in (ds_map, gm_map, gp_map):
            if s in src:
                votes.append(src[s]['verdict'])
                confs.append(float(src[s].get('confidence', 0)))
                domains.append(src[s].get('domain',''))
                reasons.append(src[s].get('reasons',''))
                if not fix and src[s].get('suggested_fix'): fix=src[s]['suggested_fix']
        verdict=majority_vote(votes)
        confidence=float(statistics.mean(confs)) if confs else 0.0
        item={'statement': s, 'verdict': verdict, 'confidence': round(confidence,3), 'domains': domains, 'reasons': reasons, 'suggested_fix': fix}
        consensus.append(item)
        if verdict=='incorrect':
            if fix:
                cleanup_sql.append(f"UPDATE facts SET statement = '{fix.replace("'","''")}' WHERE statement = '{s.replace("'","''")}';")
            else:
                cleanup_sql.append(f"DELETE FROM facts WHERE statement = '{s.replace("'","''")}';")
        correct_cnt += 1 if verdict=='correct' else 0
        incorrect_cnt += 1 if verdict=='incorrect' else 0
        uncertain_cnt += 1 if verdict=='uncertain' else 0

    out={'items': consensus, 'summary': {
        'count': len(consensus), 'correct': correct_cnt, 'incorrect': incorrect_cnt,
        'uncertain': uncertain_cnt,
        'acceptance_rate': (correct_cnt/max(1,len(consensus)))
    }, 'self_report': selfrep}

    os.makedirs(OUT_DIR, exist_ok=True)
    with open(os.path.join(OUT_DIR,'final_consensus.json'),'w',encoding='utf-8') as f:
        json.dump(out, f, ensure_ascii=False, indent=2)
    with open(os.path.join(OUT_DIR,'cleanup_proposals.sql'),'w',encoding='utf-8') as f:
        f.write('\n'.join(cleanup_sql))
    with open(os.path.join(OUT_DIR,'summary.md'),'w',encoding='utf-8') as f:
        f.write(f"Gesamt Items: {out['summary']['count']}\n")
        f.write(f"Incorrect: {incorrect_cnt} | Correct: {correct_cnt} | Uncertain: {uncertain_cnt}\n")
        f.write(f"Acceptance Rate: {out['summary']['acceptance_rate']:.3f}\n")
    print('Konsens erstellt → validation_results/final_consensus.json, cleanup_proposals.sql, summary.md')

if __name__=='__main__':
    main()
