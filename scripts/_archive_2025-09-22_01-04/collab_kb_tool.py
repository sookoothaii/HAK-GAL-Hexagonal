# HAK_GAL 4-LLM Kollaborations-Tool
# Beiträge:
# - DeepSeek: extract_relationships
# - Gemini: visualize_as_ascii
# - Claude: analyze_kb
# - Orchestrator/CLI: Assistant

def extract_relationships(facts: list[str]) -> list[tuple[str,str,str]]:
    results: list[tuple[str,str,str]] = []
    for s in facts:
        if not s or '(' not in s or ')' not in s:
            continue
        try:
            predicate = s.split('(', 1)[0].strip()
            inner = s[s.find('(')+1:s.rfind(')')]
            parts = [p.strip().rstrip('.') for p in inner.split(',')]
            if len(parts) == 2 and predicate:
                a, b = parts[0], parts[1]
                if a and b:
                    results.append((predicate, a, b))
        except Exception:
            continue
    return results

def visualize_as_ascii(relationships: list[tuple[str,str,str]], max_nodes: int = 50) -> str:
    seen_nodes = set()
    by_pred: dict[str, list[tuple[str, str]]] = {}
    for pred, a, b in relationships:
        by_pred.setdefault(pred, []).append((a, b))
        if len(seen_nodes) < max_nodes:
            seen_nodes.add(a)
        if len(seen_nodes) < max_nodes:
            seen_nodes.add(b)
    lines: list[str] = []
    for pred in sorted(by_pred.keys()):
        lines.append(f"[{pred}]")
        for a, b in by_pred[pred]:
            if a in seen_nodes and b in seen_nodes:
                lines.append(f"  {a} --{pred}--> {b}")
        lines.append("")
    if not lines:
        return "<no relationships>"
    return "\n".join(lines).rstrip()

def analyze_kb(db_path: str, sample: int = 100) -> dict:
    import sqlite3
    out = {"count": 0, "unique_predicates": [], "top_entities": [], "sample_facts": []}
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT COUNT(*) FROM facts")
        out["count"] = int(cur.fetchone()[0])
        cur = conn.execute("SELECT statement FROM facts LIMIT ?", (int(sample),))
        facts = [row[0] for row in cur]
        out["sample_facts"] = facts
        preds: dict[str, int] = {}
        ents: dict[str, int] = {}
        for s in facts:
            try:
                pred = s.split('(',1)[0].strip()
                inner = s[s.find('(')+1:s.rfind(')')]
                parts = [p.strip().rstrip('.') for p in inner.split(',')]
                if pred:
                    preds[pred] = preds.get(pred,0)+1
                for p in parts:
                    if p:
                        ents[p] = ents.get(p,0)+1
            except Exception:
                continue
        out["unique_predicates"] = sorted(list(preds.keys()))
        out["top_entities"] = sorted(ents.items(), key=lambda x: x[1], reverse=True)[:20]
        conn.close()
    except Exception:
        pass
    return out
def _read_facts_from_db(db_path: str, limit: int = 200):
    import sqlite3
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT statement FROM facts LIMIT ?", (int(limit),))
        items = [row[0] for row in cur]
        conn.close()
        return items
    except Exception:
        return []


def main():
    import argparse, json
    p = argparse.ArgumentParser(description="HAK_GAL Knowledge Visualizer (4-LLM Collab)")
    p.add_argument("--db", default="D:/MCP Mods/HAK_GAL_HEXAGONAL/hexagonal_kb.db")
    p.add_argument("--sample", type=int, default=100)
    p.add_argument("--out", default="")
    args = p.parse_args()

    stats = analyze_kb(args.db, args.sample)
    facts = stats.get("sample_facts") or _read_facts_from_db(args.db, args.sample)
    rels = extract_relationships(facts)
    ascii_graph = visualize_as_ascii(rels, max_nodes=50)

    out = {
        "stats": stats,
        "relationships_count": len(rels),
        "ascii_graph": ascii_graph
    }
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)
        print(f"Wrote output to {args.out}")
    else:
        print(text)

if __name__ == "__main__":
    main()
