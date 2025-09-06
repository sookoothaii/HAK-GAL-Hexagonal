import argparse
import json
from pathlib import Path


def main():
    ap = argparse.ArgumentParser(description="Generate synthetic test data for facts")
    ap.add_argument("--count", type=int, default=10)
    ap.add_argument("--out", default="PROJECT_HUB/test_facts.jsonl")
    args = ap.parse_args()

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    with out.open("w", encoding="utf-8") as f:
        for i in range(args.count):
            obj = {"statement": f"TestRelation(Entity{i}, Entity{i+1})."}
            f.write(json.dumps(obj, ensure_ascii=False) + "\n")
    print(f"OK: generated {args.count} facts -> {out}")


if __name__ == "__main__":
    main()


