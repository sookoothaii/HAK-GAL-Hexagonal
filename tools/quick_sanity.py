# -*- coding: utf-8 -*-
import sqlite3, json, os, re, random
from typing import List, Tuple

DB='hexagonal_kb.db'
OUT_DIR='validation_results'

PROBLEM_PAIRS=[('NH3','oxygen'),('H2O','carbon'),('CH4','oxygen'),('CO2','hydrogen')]
GENERIC_TERMS={'complex','fundamental','static','variable','output'}

os.makedirs(OUT_DIR, exist_ok=True)

conn=sqlite3.connect(DB)
cur=conn.cursor()

# Tabelle erkennen
cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
names={r[0] for r in cur.fetchall()}
table='facts' if 'facts' in names else ('facts_extended' if 'facts_extended' in names else 'facts')

# Gesamtzahl
cur.execute(f"SELECT COUNT(1) FROM {table}")
(total,)=cur.fetchone()

# Utility
def fetch_all_like(pattern:str, limit:int=0)->List[str]:
    sql=f"SELECT statement FROM {table} WHERE statement LIKE ?"
    if limit>0:
        sql += " LIMIT ?"
    params=(pattern,)
    if limit>0:
        params+=(limit,)
    cur.execute(sql, params)
    return [r[0] for r in cur.fetchall()]

# Counts
api_cnt=len(fetch_all_like('API(%'))
http_cnt=len(fetch_all_like('%HTTP%'))
sql_cnt=len(fetch_all_like('%SQL%'))

# HasProperty mit generischen Attributen (heuristisch)
cur.execute(f"SELECT statement FROM {table} WHERE statement LIKE 'HasProperty(%' LIMIT 50000")
hp_rows=[r[0] for r in cur.fetchall()]
hp_generic=sum(1 for s in hp_rows for t in GENERIC_TERMS if t.lower() in s.lower())

# Chemie No-Gos
chem_issues=0
for a,b in PROBLEM_PAIRS:
    cur.execute(f"SELECT COUNT(1) FROM {table} WHERE lower(statement) LIKE ? AND lower(statement) LIKE ?", (f"%{a.lower()}%", f"%{b.lower()}%"))
    chem_issues += cur.fetchone()[0]

# Argument-Verteilung (Kommas im Inneren)
cur.execute(f"SELECT statement FROM {table} LIMIT 50000")
rows=[r[0] for r in cur.fetchall()]

def arg_count(s:str)->int:
    i=s.find('(')
    if i<0 or not s.endswith(')'):
        return 0
    inner=s[i+1:-1]
    if not inner:
        return 0
    return inner.count(',')+1

counts={'>=5_args':0,'4_args':0,'3_args':0,'<=2_args':0}
for s in rows:
    n=arg_count(s)
    if n>=5: counts['>=5_args']+=1
    elif n==4: counts['4_args']+=1
    elif n==3: counts['3_args']+=1
    else: counts['<=2_args']+=1

# Kleine Stichprobe verdächtiger Sätze
suspicious=[]
for s in rows:
    low=s.lower()
    if 'api(' in low or 'http' in low or 'sql' in low:
        suspicious.append(s)
    elif any(a.lower() in low and b.lower() in low for a,b in PROBLEM_PAIRS):
        suspicious.append(s)
random.shuffle(suspicious)
sample=suspicious[:15]

summary={
    'table': table,
    'total': total,
    'counts': {
        'api_predicate': api_cnt,
        'contains_HTTP': http_cnt,
        'contains_SQL': sql_cnt,
        'hasproperty_generic_terms_50k_scan': hp_generic,
        'chem_invalid_pairs_total': chem_issues,
    },
    'arg_distribution_50k': counts,
}

with open(os.path.join(OUT_DIR,'sanity_summary.json'),'w',encoding='utf-8') as f:
    json.dump(summary, f, ensure_ascii=False, indent=2)
with open(os.path.join(OUT_DIR,'sanity_sample.md'),'w',encoding='utf-8') as f:
    f.write('\n'.join(sample))

print(json.dumps(summary, ensure_ascii=False))
