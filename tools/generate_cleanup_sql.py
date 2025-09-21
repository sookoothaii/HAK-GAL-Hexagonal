# -*- coding: utf-8 -*-
"""
Erzeugt vorsichtiges Cleanup-SQL für bekannte Probleme (Chemie-No-Gos, generische HasProperty).
Schreibt nach validation_results/cleanup_targeted.sql
"""
import sqlite3, os
from datetime import datetime

DB='hexagonal_kb.db'
OUT='validation_results/cleanup_targeted.sql'

CHEM_PAIRS=[('NH3','oxygen'),('H2O','carbon'),('CH4','oxygen'),('CO2','hydrogen')]
GENERIC_HP_TERMS=['complex','fundamental','static','variable','output']
def esc(s:str)->str:
    return s.replace("'","''")

def main():
    os.makedirs('validation_results', exist_ok=True)
    conn=sqlite3.connect(DB)
    cur=conn.cursor()
    # Tabelle wählen
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    names={r[0] for r in cur.fetchall()}
    table='facts' if 'facts' in names else ('facts_extended' if 'facts_extended' in names else 'facts')

    lines=[]
    lines.append(f"-- Cleanup erstellt am {datetime.now().isoformat()}")
    lines.append(f"-- Ziel-Tabelle: {table}")

    # 1) Chemie-No-Gos: bevorzugt ersetzen, sonst löschen
    for a,b in CHEM_PAIRS:
        cur.execute(f"SELECT statement FROM {table} WHERE lower(statement) LIKE ? AND lower(statement) LIKE ?", (f"%{a.lower()}%", f"%{b.lower()}%"))
        for (s,) in cur.fetchall():
            low=s.lower()
            fix=None
            if 'nh3' in low and 'oxygen' in low:
                fix="ConsistsOf(NH3, nitrogen, hydrogen)."
            elif 'h2o' in low and 'carbon' in low:
                fix="ConsistsOf(H2O, hydrogen, oxygen)."
            elif 'ch4' in low and 'oxygen' in low:
                fix="ConsistsOf(CH4, carbon, hydrogen)."
            elif 'co2' in low and 'hydrogen' in low:
                fix="ConsistsOf(CO2, carbon, oxygen)."
            if fix:
                # Sicheres Update ohne UNIQUE-Konflikt:
                # 1) Wenn Ziel schon existiert -> alte Zeile entfernen
                lines.append(
                    f"DELETE FROM {table} WHERE statement = '{esc(s)}' AND EXISTS (SELECT 1 FROM {table} WHERE statement = '{esc(fix)}');"
                )
                # 2) Wenn Ziel noch nicht existiert -> altes Statement auf Ziel updaten
                lines.append(
                    f"UPDATE {table} SET statement = '{esc(fix)}' WHERE statement = '{esc(s)}' AND NOT EXISTS (SELECT 1 FROM {table} WHERE statement = '{esc(fix)}');"
                )
            else:
                lines.append(f"DELETE FROM {table} WHERE statement = '{esc(s)}';")

    # 2) Zu generische HasProperty (...) – defensiv löschen (nur wenn offensichtlich generisch)
    for term in GENERIC_HP_TERMS:
        cur.execute(f"SELECT statement FROM {table} WHERE statement LIKE 'HasProperty(%' AND lower(statement) LIKE ? LIMIT 5000", (f"%{term.lower()}%",))
        for (s,) in cur.fetchall():
            lines.append(f"DELETE FROM {table} WHERE statement = '{esc(s)}';")

    with open(OUT,'w',encoding='utf-8') as f:
        f.write('\n'.join(lines)+"\n")
    print(f"Cleanup-SQL → {OUT} | Statements: {len(lines)}")

if __name__=='__main__':
    main()
