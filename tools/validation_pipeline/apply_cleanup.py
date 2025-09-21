# -*- coding: utf-8 -*-
"""
Wendet cleanup_proposals.sql sicher an (Dry-Run standardmäßig). Backup via VACUUM INTO.
"""
import argparse, sqlite3, os
from datetime import datetime

DB='hexagonal_kb.db'
SQL_IN='validation_results/cleanup_proposals.sql'

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--db', default=DB)
    ap.add_argument('--sql', default=SQL_IN)
    ap.add_argument('--apply', action='store_true', help='Wenn gesetzt, Änderungen wirklich anwenden')
    args=ap.parse_args()

    if not os.path.exists(args.sql):
        raise SystemExit(f'SQL nicht gefunden: {args.sql}')

    conn=sqlite3.connect(args.db)
    try:
        cur=conn.cursor()
        # Dry-Run Anzeige
        with open(args.sql,'r',encoding='utf-8') as f:
            lines=[ln.strip() for ln in f if ln.strip()]
        print(f"SQL-Vorschläge: {len(lines)}")
        if not args.apply:
            for ln in lines[:20]:
                print(ln)
            if len(lines)>20:
                print('...')
            print('Dry-Run beendet. Mit --apply wirklich anwenden.')
            return
        # Backup
        backup=f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
        cur.execute(f"VACUUM INTO '{backup}'")
        print(f'Backup erstellt: {backup}')
        # Anwenden
        script='\n'.join(lines)
        cur.executescript(script)
        conn.commit()
        print('Cleanup angewendet.')
    finally:
        conn.close()

if __name__=='__main__':
    main()
