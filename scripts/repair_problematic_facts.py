import argparse
import json
import re
import sqlite3
import unicodedata
from pathlib import Path
from typing import List, Dict, Any

REPLACEMENTS = {
    '²': '2', '³': '3', '°': 'deg', '—': '-', '–': '-', 'â€™': "'", 'â€“': '-', 'â€œ': '"', 'â€': '"'
}

PATTERN = re.compile(r'^([A-Za-z0-9_\-]+)\((.*)\)\.$')


def normalize(s: str) -> str:
    s = unicodedata.normalize('NFKD', s)
    for k, v in REPLACEMENTS.items():
        s = s.replace(k, v)
    return s


def repair_fact(s: str) -> (str, List[str]):
    reasons: List[str] = []
    orig = s
    s = normalize(s.strip())
    if not s.endswith('.'):
        s += '.'
        reasons.append('appended_period')
    # Double "((" fix in predicate segment
    if '((' in s:
        s = s.replace('((', '(')
        reasons.append('removed_double_open_paren')
    # Balance parentheses in args
    m = PATTERN.match(s)
    if not m and '(' in s and ')' not in s:
        s += ')'
        reasons.append('balanced_parentheses')
        m = PATTERN.match(s)
    # Replace slash in predicate
    m2 = PATTERN.match(s)
    if m2:
        pred, args = m2.group(1), m2.group(2)
        if '/' in pred:
            pred = pred.replace('/', '_')
            reasons.append('predicate_slash_replaced')
        s = f"{pred}({args})."
    return s, reasons


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--db', required=True, help='Pfad zur SQLite DB (k_assistant.db)')
    ap.add_argument('--apply', action='store_true', help='Änderungen schreiben (default: Dry-Run)')
    args = ap.parse_args()

    db_path = Path(args.db)
    if not db_path.exists():
        print(json.dumps({'ok': False, 'error': f'DB not found: {db_path}'}))
        return

    conn = sqlite3.connect(str(db_path))
    try:
        cur = conn.cursor()
        cur.execute('SELECT statement FROM facts')
        rows = cur.fetchall()
        total = len(rows)
        changed = 0
        repairs: List[Dict[str, Any]] = []
        for (stmt,) in rows:
            if not isinstance(stmt, str):
                continue
            fixed, reasons = repair_fact(stmt)
            if fixed != stmt and reasons:
                repairs.append({'original': stmt, 'fixed': fixed, 'reasons': reasons})
        if args.apply:
            for r in repairs:
                cur.execute('UPDATE facts SET statement = ? WHERE statement = ?', (r['fixed'], r['original']))
            conn.commit()
            changed = cur.rowcount
        print(json.dumps({'ok': True, 'total': total, 'repairs': len(repairs), 'applied': args.apply, 'sample': repairs[:20]}))
    finally:
        conn.close()

if __name__ == '__main__':
    main()
