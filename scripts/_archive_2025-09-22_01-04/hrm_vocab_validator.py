import argparse
import json
import sys
from typing import List, Dict, Any

try:
    import requests
except Exception:
    print("Bitte 'pip install requests' ausführen.", file=sys.stderr)
    raise

DEFAULT_URL = "http://127.0.0.1:5000"  # Original API mit HRM Info


def fetch_hrm_info(base: str) -> Dict[str, Any]:
    url = f"{base}/api/hrm/info"
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def validate_queries(vocab: List[str], queries: List[str]) -> Dict[str, Any]:
    vocab_set = set([t.lower() for t in vocab])
    incompatible: List[Dict[str, Any]] = []

    def extract_terms(q: str) -> List[str]:
        # sehr einfache Extraktion: Wörter und Token in Klammern/Kommas
        inside = q
        for ch in ["(", ")", ",", "."]:
            inside = inside.replace(ch, " ")
        parts = [p.strip() for p in inside.split() if p.strip()]
        return parts

    for q in queries:
        terms = extract_terms(q)
        missing = [t for t in terms if t.lower() not in vocab_set]
        if missing:
            incompatible.append({
                "query": q,
                "missing_terms": missing
            })
    return {
        "total": len(queries),
        "incompatible_count": len(incompatible),
        "incompatible": incompatible
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="HRM Vokabular-Validierung")
    parser.add_argument("--base", default=DEFAULT_URL, help="Backend Base URL (default: %(default)s)")
    parser.add_argument("--queries", nargs="*", default=[
        "IsTypeOf(Water, Substance)",
        "PartOf(CPU, Computer)",
        "HasTrait(Mammalia, ProducesMilk)",
        "IsMemberOf(Felis catus, Mammalia)",
        "LocatedIn(AmazonRiver, SouthAmerica)",
        "DiscoveredBy(Penicillin, Alexander Fleming)",
        "InventedBy(LightBulb, Thomas Edison)",
    ])
    args = parser.parse_args()

    info = fetch_hrm_info(args.base)
    vocab = info.get("vocabulary", []) or info.get("vocabulary_terms", [])
    if not vocab:
        print("Kein Vokabular im HRM-Info gefunden.", file=sys.stderr)
        sys.exit(2)

    result = validate_queries(vocab, args.queries)
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
