# -*- coding: utf-8 -*-
import json, os, sqlite3, random
from typing import List, Dict

DB_PATH = 'hexagonal_kb.db'
OUT_DIR = 'validation_samples'

PRED_CHEM = ['Bond','ConsistsOf','CombinesWith','Emits','FormsFrom']
PRED_BIO_PHYS = ['IsTypeOf','HasPart','HasProperty','DependsOn','Causes','LocatedAt','DetectedBy']


def ensure_dir(p:str):
    if not os.path.exists(p):
        os.makedirs(p)


def get_predicate(stmt: str) -> str:
    if not stmt:
        return ''
    i = stmt.find('(')
    return stmt[:i] if i>0 else stmt.split()[0]


def sample_by_predicates(conn: sqlite3.Connection, table: str, predicates: List[str], per_pred: int) -> List[Dict[str,str]]:
    cur = conn.cursor()
    col = 'statement'
    res: List[Dict[str,str]] = []
    for pred in predicates:
        cur.execute(f"SELECT {col} FROM {table} WHERE {col} LIKE ? ORDER BY RANDOM() LIMIT ?", (pred+'(%', per_pred))
        rows = cur.fetchall()
        for (stmt,) in rows:
            res.append({"predicate": get_predicate(stmt), "statement": stmt})
    return res


def top_predicates(conn: sqlite3.Connection, table: str, top_n: int) -> List[str]:
    cur = conn.cursor()
    cur.execute(f"SELECT statement FROM {table} ORDER BY RANDOM() LIMIT 5000")
    counts: Dict[str,int] = {}
    for (stmt,) in cur.fetchall():
        p = get_predicate(stmt)
        if not p: continue
        counts[p] = counts.get(p,0)+1
    return [p for p,_ in sorted(counts.items(), key=lambda kv: kv[1], reverse=True)[:top_n]]


def main():
    ensure_dir(OUT_DIR)
    conn = sqlite3.connect(DB_PATH)
    try:
        # autodetect table preference: facts
        table = 'facts'
        cur = conn.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = {r[0] for r in cur.fetchall()}
        if table not in tables:
            table = 'facts_extended' if 'facts_extended' in tables else 'facts'

        deepseek = sample_by_predicates(conn, table, PRED_CHEM, per_pred=50//max(1,len(PRED_CHEM)))
        gemini = sample_by_predicates(conn, table, PRED_BIO_PHYS, per_pred=60//max(1,len(PRED_BIO_PHYS)))
        # self: top predicates generic
        tops = top_predicates(conn, table, top_n=10)
        generic = sample_by_predicates(conn, table, tops, per_pred=100//max(1,len(tops)))

        with open(os.path.join(OUT_DIR,'deepseek_chemistry.json'),'w',encoding='utf-8') as f:
            json.dump({"table": table, "samples": deepseek}, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUT_DIR,'gemini_bio_phys.json'),'w',encoding='utf-8') as f:
            json.dump({"table": table, "samples": gemini}, f, ensure_ascii=False, indent=2)
        with open(os.path.join(OUT_DIR,'self_generic.json'),'w',encoding='utf-8') as f:
            json.dump({"table": table, "samples": generic}, f, ensure_ascii=False, indent=2)
    finally:
        conn.close()

if __name__ == '__main__':
    main()
