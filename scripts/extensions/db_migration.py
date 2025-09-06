import argparse
import sqlite3
from pathlib import Path


def apply_migration(db_path: Path, sql_path: Path) -> None:
    con = sqlite3.connect(str(db_path))
    try:
        with con:
            con.executescript(sql_path.read_text(encoding="utf-8"))
    finally:
        con.close()


def main():
    ap = argparse.ArgumentParser(description="Execute SQLite migration script")
    ap.add_argument("db", help="Path to SQLite DB (e.g. data/k_assistant.db)")
    ap.add_argument("sql", help="Path to .sql file with DDL/DML")
    args = ap.parse_args()
    apply_migration(Path(args.db), Path(args.sql))
    print("OK: migration applied")


if __name__ == "__main__":
    main()


