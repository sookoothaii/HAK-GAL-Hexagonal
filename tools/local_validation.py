# -*- coding: utf-8 -*-
import json, os, re, sqlite3, statistics
from typing import Dict, List

DB='hexagonal_kb.db'
OUT_DIR='validation_results'

PRED_RE = re.compile(r'^[A-Za-z_][A-Za-z0-9_]*$')


def get_all(conn, table: str, limit:int=10000):
    cur = conn.cursor()
    cur.execute(f"SELECT statement FROM {table} LIMIT ?", (limit,))
    return [r[0] for r in cur.fetchall()]


def analyze(statements: List[str]) -> Dict:
    lens = [len(s or '') for s in statements]
    paren_ok = sum(1 for s in statements if s.count('(')==s.count(')') and '(' in s)
    pred_ok = 0
    multiarg = 0
    examples_bad_syntax = []
    sample_count = min(1000, len(statements))
    for s in statements[:sample_count]:
        i = s.find('(')
        pred = s[:i] if i>0 else ''
        if PRED_RE.match(pred or ''):
            pred_ok += 1
        inner = s[i+1:-1] if i>0 and s.endswith(')') else ''
        if inner.count(',')>=2:
            multiarg += 1
        if not (i>0 and s.endswith(')') and s.count('(')==s.count(')')):
            if len(examples_bad_syntax)<10:
                examples_bad_syntax.append(s)
    return {
        'count': len(statements),
        'len_avg': statistics.mean(lens) if lens else 0,
        'len_p95': statistics.quantiles(lens, n=20)[18] if len(lens)>=20 else max(lens or [0]),
        'paren_balance_rate': paren_ok/len(statements) if statements else 0,
        'predicate_token_rate': (pred_ok/sample_count) if sample_count else 0,
        'multiarg_rate': (multiarg/sample_count) if sample_count else 0,
        'bad_syntax_examples': examples_bad_syntax,
    }


def main():
    if not os.path.exists(OUT_DIR):
        os.makedirs(OUT_DIR)
    conn = sqlite3.connect(DB)
    try:
        # prefer facts
        table='facts'
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables={r[0] for r in cur.fetchall()}
        if table not in tables:
            table='facts_extended' if 'facts_extended' in tables else 'facts'
        stmts = get_all(conn, table, limit=50000)
        res = analyze(stmts)
        res['table']=table
        with open(os.path.join(OUT_DIR,'self_report.json'),'w',encoding='utf-8') as f:
            json.dump(res, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUT_DIR,'self_report.md'),'w',encoding='utf-8') as f:
            f.write(f"Gesamt: {res['count']}\n")
            f.write(f"Multi-Arg-Rate: {res['multiarg_rate']:.3f}\n")
            f.write(f"Klammer-Balance: {res['paren_balance_rate']:.3f}\n")
            f.write(f"Predicate-Token-Rate: {res['predicate_token_rate']:.3f}\n")
    finally:
        conn.close()

if __name__=='__main__':
    main()
