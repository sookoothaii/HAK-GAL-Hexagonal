import argparse
from pathlib import Path


def extract_headings(md_path: Path) -> list[str]:
    headings = []
    for line in md_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("### ") or line.startswith("## "):
            headings.append(line.strip())
    return headings


def main():
    ap = argparse.ArgumentParser(description="Generate consolidated docs from Markdown sources")
    ap.add_argument("sources", nargs="+", help="Markdown input files")
    ap.add_argument("--out", default="PROJECT_HUB/DOCS_INDEX.md")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    parts = ["### Documentation Index\n"]
    for s in args.sources:
        p = Path(s)
        if not p.exists():
            continue
        parts.append(f"\n## {p}")
        for h in extract_headings(p):
            parts.append(f"- {h}")
    out.write_text("\n".join(parts), encoding="utf-8")
    print(f"OK: {out}")


if __name__ == "__main__":
    main()


