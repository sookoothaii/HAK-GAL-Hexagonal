# -*- coding: utf-8 -*-
"""
HAK-GAL Semantic Error Fixer
===========================
Findet und korrigiert semantische Fehler in der Knowledge Base.
Unterstützt Dry-Run/Korrektur/Löschen, Backup via VACUUM INTO,
Tabellenwahl (facts/facts_extended) und ausführlichen Report.
"""

import argparse
import json
import os
import re
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# --------- Regeln für semantische Korrekturen ---------
# Jede Regel definiert: SQL-LIKE-Pattern, Regex-Verifikation, Fehlermeldung, optionale Korrektur
CORRECTION_RULES: Dict[str, List[Dict[str, str]]] = {
    "chemistry": [
        {
            "like": "%NH3%oxygen%",
            "regex": r"NH3.*oxygen",
            "error": "NH3 enthält kein Oxygen",
            "correction": "ConsistsOf(NH3, nitrogen, hydrogen).",
        },
        {
            "like": "%H2O%carbon%",
            "regex": r"H2O.*carbon",
            "error": "H2O enthält kein Carbon",
            "correction": "ConsistsOf(H2O, hydrogen, oxygen).",
        },
        {
            "like": "%CH4%oxygen%",
            "regex": r"CH4.*oxygen",
            "error": "CH4 enthält kein Oxygen",
            "correction": "ConsistsOf(CH4, carbon, hydrogen).",
        },
        {
            "like": "%CO2%hydrogen%",
            "regex": r"CO2.*hydrogen",
            "error": "CO2 enthält kein Hydrogen",
            "correction": "ConsistsOf(CO2, carbon, oxygen).",
        },
        {
            "like": "%NaCl%carbon%",
            "regex": r"NaCl.*carbon",
            "error": "NaCl enthält kein Carbon",
            "correction": "ConsistsOf(NaCl, sodium, chlorine).",
        },
    ],
    "biology": [
        {
            "like": "%virus%organ%",
            "regex": r"virus.*organ",
            "error": "Viren haben keine Organe",
            "correction": "ConsistsOf(virus, protein, nucleic_acid).",
        },
        {
            "like": "%bacteria%nucleus%",
            "regex": r"bacteria.*nucleus",
            "error": "Bakterien haben keinen echten Zellkern",
            "correction": "IsTypeOf(bacteria, prokaryote).",
        },
    ],
    "physics": [
        {
            "like": "%gravity%particle%",
            "regex": r"gravity.*particle",
            "error": "Gravity ist eine Kraft, kein Teilchen",
            "correction": "IsTypeOf(gravity, fundamental_force).",
        },
        {
            "like": "%momentum%",
            "regex": r"HasPart\(.*momentum.*\)",
            "error": "Momentum ist eine Eigenschaft",
            "correction": "HasProperty(object, momentum).",
        },
    ],
}

ADDITIONAL_CORRECT_FACTS: List[str] = [
    # Chemie
    "ConsistsOf(H2O, hydrogen, oxygen).",
    "ConsistsOf(NH3, nitrogen, hydrogen).",
    "ConsistsOf(CO2, carbon, oxygen).",
    "ConsistsOf(CH4, carbon, hydrogen).",
    "ConsistsOf(NaCl, sodium, chlorine).",
    # Biologie
    "ConsistsOf(virus, protein, nucleic_acid).",
    "HasPart(cell, nucleus).",
    "HasPart(cell, membrane).",
    "HasPart(cell, cytoplasm).",
    "IsTypeOf(bacteria, prokaryote).",
    "IsTypeOf(virus, infectious_agent).",
    # Physik
    "IsTypeOf(gravity, fundamental_force).",
    "IsTypeOf(electromagnetism, fundamental_force).",
    "HasProperty(photon, energy).",
    "HasProperty(electron, charge).",
    "ConsistsOf(atom, proton, neutron, electron).",
]

@contextmanager
def sqlite_conn(db_path: str):
    conn = sqlite3.connect(db_path)
    try:
        yield conn
    finally:
        conn.close()


def detect_table(conn: sqlite3.Connection, preferred: str) -> str:
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = {row[0] for row in cur.fetchall()}
    if preferred in tables:
        return preferred
    if "facts" in tables:
        return "facts"
    if "facts_extended" in tables:
        return "facts_extended"
    raise RuntimeError("Keine geeignete Tabelle gefunden (facts/facts_extended)")


def find_errors(conn: sqlite3.Connection, table: str, limit: Optional[int]) -> List[Tuple[str, str, Optional[str]]]:
    errors: List[Tuple[str, str, Optional[str]]] = []
    cur = conn.cursor()
    # Spaltenprüfung
    cur.execute(f"PRAGMA table_info({table})")
    cols = [r[1] for r in cur.fetchall()]
    col = "statement" if "statement" in cols else cols[1] if cols else "statement"

    for rules in CORRECTION_RULES.values():
        for rule in rules:
            like = rule["like"]
            regex = re.compile(rule["regex"], re.IGNORECASE)
            sql = f"SELECT {col} FROM {table} WHERE {col} LIKE ?"
            params = (like,)
            if limit:
                sql += " LIMIT ?"
                params = (like, limit)
            cur.execute(sql, params)
            for (stmt,) in cur.fetchall():
                if regex.search(stmt or ""):
                    errors.append((stmt, rule["error"], rule.get("correction")))

    # Duplikate entfernen, Reihenfolge bewahren
    seen = set()
    unique: List[Tuple[str, str, Optional[str]]] = []
    for e in errors:
        if e[0] not in seen:
            unique.append(e)
            seen.add(e[0])
    return unique


def apply_fixes(conn: sqlite3.Connection, table: str, col: str, errors: List[Tuple[str, str, Optional[str]]], mode: str) -> Dict[str, int]:
    stats = {"fixed": 0, "deleted": 0}
    cur = conn.cursor()
    with conn:
        for stmt, _msg, correction in errors:
            if mode == "delete" or (mode == "correct" and not correction):
                cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (stmt,))
                stats["deleted"] += 1
                continue

            if mode == "correct" and correction:
                # Prüfen, ob die Ziel-Korrektur bereits existiert
                cur.execute(f"SELECT 1 FROM {table} WHERE {col} = ? LIMIT 1", (correction,))
                exists = cur.fetchone() is not None
                if exists:
                    # Ziel existiert bereits -> fehlerhafte Zeile löschen
                    cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (stmt,))
                    stats["deleted"] += 1
                    continue
                try:
                    cur.execute(
                        f"UPDATE {table} SET {col} = ? WHERE {col} = ?",
                        (correction, stmt),
                    )
                    # Falls keine Zeile aktualisiert wurde (sollte selten sein), als Fallback einfügen und alte löschen
                    if cur.rowcount == 0:
                        cur.execute(f"INSERT OR IGNORE INTO {table} ({col}) VALUES (?)", (correction,))
                        cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (stmt,))
                        stats["deleted"] += 1
                    else:
                        stats["fixed"] += 1
                except sqlite3.IntegrityError:
                    # UNIQUE-Verletzung -> korrigierte existiert bereits; alte löschen
                    cur.execute(f"DELETE FROM {table} WHERE {col} = ?", (stmt,))
                    stats["deleted"] += 1
    return stats


def add_correct_facts(conn: sqlite3.Connection, table: str, col: str) -> int:
    cur = conn.cursor()
    added = 0
    with conn:
        for fact in ADDITIONAL_CORRECT_FACTS:
            cur.execute(f"SELECT COUNT(1) FROM {table} WHERE {col} = ?", (fact,))
            if cur.fetchone()[0] == 0:
                cur.execute(f"INSERT INTO {table} ({col}) VALUES (?)", (fact,))
                added += 1
    return added


def backup_database(conn: sqlite3.Connection, backup_path: str) -> None:
    cur = conn.cursor()
    cur.execute(f"VACUUM INTO '{backup_path}'")


def generate_report(db_path: str, table: str, total_errors: int, stats: Dict[str, int], remaining_query: str) -> str:
    with sqlite_conn(db_path) as conn:
        cur = conn.cursor()
        cur.execute(f"SELECT COUNT(1) FROM {table}")
        total = cur.fetchone()[0]
        cur.execute(remaining_query)
        remaining = cur.fetchone()[0]

    lines: List[str] = []
    lines.append("=" * 70)
    lines.append("   SEMANTIC ERROR FIX - ABSCHLUSSBERICHT")
    lines.append("=" * 70)
    lines.append(f"Zeitpunkt: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append("📊 STATISTIK:")
    lines.append("-" * 40)
    lines.append(f"  Gefundene Fehler: {total_errors}")
    lines.append(f"  ✅ Korrigiert: {stats.get('fixed', 0)}")
    lines.append(f"  🗑️ Gelöscht: {stats.get('deleted', 0)}")
    lines.append("")
    lines.append("📈 NEUE DATENBANK-STATISTIK:")
    lines.append(f"  Total Fakten ({table}): {total:,}")
    lines.append(f"  Verbleibende Fehler: {remaining}")
    if remaining == 0:
        lines.append("🎉 ERFOLG! Alle bekannten semantischen Fehler wurden behoben!")
    lines.append("")
    lines.append("Hinweis: Nur regelbasierte bekannten Fehler geprüft. Für tiefergehende QA bitte LLM-Validierung einsetzen.")
    lines.append("=" * 70)
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description="HAK-GAL Semantic Error Fixer")
    parser.add_argument("--db", default="hexagonal_kb.db", help="Pfad zur SQLite DB")
    parser.add_argument("--table", default="facts", help="Zieltabelle: facts oder facts_extended")
    parser.add_argument("--mode", choices=["dry-run", "correct", "delete"], default="dry-run", help="dry-run/korrigieren/löschen")
    parser.add_argument("--limit", type=int, default=None, help="Max Treffer pro Regel (optional)")
    parser.add_argument("--no-backup", action="store_true", help="Kein Backup erstellen")
    parser.add_argument("--add-correct", action="store_true", help="Korrekte Fakten zusätzlich einfügen")
    parser.add_argument("--report", default="semantic_fix_report.md", help="Report-Datei")
    parser.add_argument("--stats", default="semantic_fix_stats.json", help="Stats JSON")

    args = parser.parse_args()

    if not os.path.exists(args.db):
        raise SystemExit(f"DB nicht gefunden: {args.db}")

    with sqlite_conn(args.db) as conn:
        table = detect_table(conn, args.table)
        cur = conn.cursor()
        cur.execute(f"PRAGMA table_info({table})")
        cols = [r[1] for r in cur.fetchall()]
        col = "statement" if "statement" in cols else cols[1] if cols else "statement"

        print("=" * 70)
        print("   HAK-GAL SEMANTIC ERROR FIXER")
        print("=" * 70)
        print(f"DB: {args.db} | Tabelle: {table} | Spalte: {col}")
        print(f"Modus: {args.mode} | Limit: {args.limit or '-'}")

        # Phase 1: Suche
        print("\n📋 Phase 1: Fehlersuche...")
        errors = find_errors(conn, table, args.limit)
        total_errors = len(errors)
        print(f"✅ {total_errors} semantische Fehler gefunden")
        for stmt, msg, corr in errors[:5]:
            print(f"❌ {stmt[:100]}...")
            print(f"   Problem: {msg}")
            if corr:
                print(f"   ✅ Korrektur: {corr}")

        # Optionales Backup
        if args.mode != "dry-run" and not args.no_backup and total_errors > 0:
            backup_name = f"hexagonal_kb_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db"
            print(f"\n📦 Backup erstellen → {backup_name}")
            backup_database(conn, backup_name)
            print("✅ Backup fertig")

        # Phase 2: Anwenden
        stats = {"fixed": 0, "deleted": 0}
        if args.mode in ("correct", "delete") and total_errors > 0:
            print("\n🔧 Phase 2: Änderungen anwenden...")
            stats = apply_fixes(conn, table, col, errors, args.mode)
            print(f"✅ Korrigiert: {stats['fixed']} | Gelöscht: {stats['deleted']}")

        # Phase 3: Zusätzliche korrekte Fakten
        if args.add_correct and args.mode != "delete":
            print("\n➕ Phase 3: Korrekte Fakten hinzufügen...")
            added = add_correct_facts(conn, table, col)
            print(f"✅ Hinzugefügt: {added}")

    # Report & Stats
    remaining_query = (
        "SELECT COUNT(1) FROM {table} WHERE "
        "( {col} LIKE '%NH3%' AND {col} LIKE '%oxygen%' ) OR "
        "( {col} LIKE '%H2O%' AND {col} LIKE '%carbon%' ) OR "
        "( {col} LIKE '%CH4%' AND {col} LIKE '%oxygen%' ) OR "
        "( {col} LIKE '%CO2%' AND {col} LIKE '%hydrogen%' ) OR "
        "( lower({col}) LIKE '%virus%' AND lower({col}) LIKE '%organ%' ) OR "
        "( lower({col}) LIKE '%bacteria%' AND lower({col}) LIKE '%nucleus%' ) OR "
        "( lower({col}) LIKE '%gravity%' AND lower({col}) LIKE '%particle%' ) OR "
        "( {col} LIKE '%momentum%' AND {col} LIKE '%HasPart(%' )"
    ).format(table=table, col=col)

    report_text = generate_report(args.db, table, total_errors, stats, remaining_query)
    with open(args.report, "w", encoding="utf-8") as f:
        f.write(report_text)
    with open(args.stats, "w", encoding="utf-8") as f:
        json.dump({"total_errors": total_errors, **stats}, f, indent=2)

    print(f"\n📄 Report gespeichert: {args.report}")
    print(f"📊 Stats gespeichert: {args.stats}")


if __name__ == "__main__":
    main()
