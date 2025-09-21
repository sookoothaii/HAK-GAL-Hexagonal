# -*- coding: utf-8 -*-
"""
Heuristisches Uncertainty-Scoring: markiert potenziell fehleranfällige Fakten.
Ergebnisse: validation_results/uncertainty_scores.jsonl und top_k.json
"""
import argparse, os, json, re, sqlite3
from typing import List, Dict

DB='hexagonal_kb.db'
OUT_DIR='validation_results'
PRED_RE=re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')

ILLEGAL_ARG_PAIRS=[('NH3','oxygen'), ('H2O','carbon'), ('CH4','oxygen'), ('CO2','hydrogen')]

def ensure_dir(p:str):
    if not os.path.exists(p): os.makedirs(p)

def get_predicate(stmt:str)->str:
    if not stmt: return ''
    i=stmt.find('(')
    return stmt[:i] if i>0 else stmt.split()[0]

def score_statement(stmt:str)->float:
    score=0.0
    # 1) Syntax
    if '(' not in stmt or not stmt.endswith(')') or stmt.count('(')!=stmt.count(')'):
        score += 0.5
    # 2) Predicate token
    pred=get_predicate(stmt)
    if not PRED_RE.match(pred or ''):
        score += 0.3
    # 3) Multi-arg plausibility (mind. 2 Kommas)
    inner=stmt[stmt.find('(')+1:-1] if '(' in stmt and stmt.endswith(')') else ''
    if inner.count(',')<1:
        score += 0.2
    # 4) Domain Heuristics (Chemie No-Gos)
    low=stmt.lower()
    for a,b in ILLEGAL_ARG_PAIRS:
        if a.lower() in low and b.lower() in low:
            score += 0.8
            break
    # 5) Sehr kurze oder sehr lange Aussagen
    if len(stmt)<12: score += 0.2
    if len(stmt)>120: score += 0.1
    return min(score, 1.0)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--db', default=DB)
    ap.add_argument('--table', default='facts')
    ap.add_argument('--limit', type=int, default=50000)
    ap.add_argument('--top-k', type=int, default=1000)
    args=ap.parse_args()

    ensure_dir(OUT_DIR)
    conn=sqlite3.connect(args.db)
    try:
        cur=conn.cursor()
        # Autowahl Tabelle
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        names={r[0] for r in cur.fetchall()}
        table=args.table if args.table in names else ('facts_extended' if 'facts_extended' in names else 'facts')
        cur.execute(f"SELECT statement FROM {table} LIMIT ?", (args.limit,))
        rows=[r[0] for r in cur.fetchall()]
        scored=[{'statement': s, 'predicate': get_predicate(s), 'uncertainty': score_statement(s)} for s in rows]
        scored.sort(key=lambda x: x['uncertainty'], reverse=True)
        with open(os.path.join(OUT_DIR,'uncertainty_scores.jsonl'),'w',encoding='utf-8') as f:
            for item in scored:
                f.write(json.dumps(item, ensure_ascii=False)+"\n")
        with open(os.path.join(OUT_DIR,'top_k.json'),'w',encoding='utf-8') as f:
            json.dump(scored[:args.top_k], f, ensure_ascii=False, indent=2)
        print(f"Scored {len(scored)} | TopK→ {OUT_DIR}/top_k.json")
    finally:
        conn.close()

if __name__=='__main__':
    main()
