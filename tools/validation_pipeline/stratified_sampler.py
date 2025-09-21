# -*- coding: utf-8 -*-
"""
Stratifizierte Stichprobe aus SQLite: balanciert nach Prädikaten (Top & selten),
inkl. Random-Reserve. Ergebnisse in validation_samples/stratified/*.json.
"""
import argparse, os, json, sqlite3, random
from collections import Counter, defaultdict
from typing import List, Dict, Tuple

DB='hexagonal_kb.db'
OUT='validation_samples/stratified'

def ensure_dir(p:str):
    if not os.path.exists(p):
        os.makedirs(p)

def get_predicate(stmt:str)->str:
    if not stmt: return ''
    i=stmt.find('(')
    return stmt[:i] if i>0 else stmt.split()[0]

def load_pred_counts(conn:sqlite3.Connection, table:str, sample:int=10000)->Counter:
    cur=conn.cursor()
    cur.execute(f"SELECT statement FROM {table} ORDER BY RANDOM() LIMIT ?", (sample,))
    cnt=Counter()
    for (s,) in cur.fetchall():
        cnt[get_predicate(s)] += 1
    return cnt

def pick_tables(conn)->str:
    cur=conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names={r[0] for r in cur.fetchall()}
    return 'facts' if 'facts' in names else ('facts_extended' if 'facts_extended' in names else 'facts')

def sample_from_pred(conn, table, pred:str, n:int)->List[str]:
    cur=conn.cursor()
    cur.execute(f"SELECT statement FROM {table} WHERE statement LIKE ? ORDER BY RANDOM() LIMIT ?", (pred+'(%', n))
    return [r[0] for r in cur.fetchall()]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--db', default=DB)
    ap.add_argument('--table', default=None)
    ap.add_argument('--top', type=int, default=10, help='Top Predicates')
    ap.add_argument('--rare', type=int, default=10, help='Seltene Predicates')
    ap.add_argument('--per-pred', type=int, default=20)
    ap.add_argument('--reserve', type=int, default=200)
    args=ap.parse_args()

    ensure_dir(OUT)
    conn=sqlite3.connect(args.db)
    try:
        table=args.table or pick_tables(conn)
        counts=load_pred_counts(conn, table, sample=20000)
        if '' in counts:
            counts.pop('')
        if not counts:
            raise SystemExit('Keine Prädikate gefunden')
        top_preds=[p for p,_ in counts.most_common(args.top)]
        rare_preds=[p for p,_ in sorted(counts.items(), key=lambda kv: kv[1])[:args.rare]]
        # Entdoppeln
        rare_preds=[p for p in rare_preds if p not in top_preds]

        batches: Dict[str, List[Dict[str,str]]] = {}
        for name, preds in [('top', top_preds), ('rare', rare_preds)]:
            items=[]
            for p in preds:
                for s in sample_from_pred(conn, table, p, args.per_pred):
                    items.append({'predicate': p, 'statement': s})
            batches[name]=items

        # Reserve: echte Zufallsstichprobe
        cur=conn.cursor()
        cur.execute(f"SELECT statement FROM {table} ORDER BY RANDOM() LIMIT ?", (args.reserve,))
        reserve=[{'predicate': get_predicate(s), 'statement': s} for (s,) in cur.fetchall()]

        with open(os.path.join(OUT,'top.json'),'w',encoding='utf-8') as f:
            json.dump({'table': table, 'samples': batches['top']}, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUT,'rare.json'),'w',encoding='utf-8') as f:
            json.dump({'table': table, 'samples': batches['rare']}, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUT,'reserve.json'),'w',encoding='utf-8') as f:
            json.dump({'table': table, 'samples': reserve}, f, ensure_ascii=False, indent=2)
        print(f"Top: {len(batches['top'])} | Rare: {len(batches['rare'])} | Reserve: {len(reserve)} → {OUT}")
    finally:
        conn.close()

if __name__=='__main__':
    main()
