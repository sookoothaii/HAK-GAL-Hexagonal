import argparse
import re
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Analyze logs for errors and warnings")
    ap.add_argument("logfile", help="Path to log file")
    args = ap.parse_args()
    p = Path(args.logfile)
    errs = []
    warns = []
    for line in p.read_text(encoding="utf-8", errors="ignore").splitlines():
        if re.search(r"\bERROR\b|\bException\b", line):
            errs.append(line)
        elif re.search(r"\bWARN\b|\bWARNING\b", line):
            warns.append(line)
    print(f"Errors: {len(errs)} | Warnings: {len(warns)}")
    for ln in errs[:50]:
        print(ln)


if __name__ == "__main__":
    main()


