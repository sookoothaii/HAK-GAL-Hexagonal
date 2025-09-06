import asyncio, json, sys, re
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

PROMPT_DS = r'''Gib NUR Python-Code zwischen den Markern BEGIN_CODE und END_CODE aus.
Implementiere: def extract_relationships(facts: list[str]) -> list[tuple[str,str,str]]:
- facts enthält Strings wie 'Predicate(Arg1, Arg2).'
- Parse robust: ignoriere invalide, trimme Whitespaces, entferne trailing Punkt.
- Liefere Liste von (predicate, arg1, arg2) für 2-Argument-Fakten.
- Keine externen Imports. Keine Prints.
BEGIN_CODE
# DeepSeek contribution
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
END_CODE
'''

PROMPT_GM = r'''Gib NUR Python-Code zwischen BEGIN_CODE und END_CODE aus.
Implementiere: def visualize_as_ascii(relationships: list[tuple[str,str,str]], max_nodes: int = 50) -> str
- relationships: Liste (predicate, a, b)
- Erzeuge einfache ASCII-Kantenliste gruppiert nach Prädikat.
- Begrenze auf max_nodes verschiedene Knoten.
- Keine externen Imports. Keine Prints.
BEGIN_CODE
# Gemini contribution
def visualize_as_ascii(relationships: list[tuple[str,str,str]], max_nodes: int = 50) -> str:
    seen_nodes = set()
    by_pred = {}
    for pred, a, b in relationships:
        by_pred.setdefault(pred, []).append((a, b))
        if len(seen_nodes) < max_nodes:
            seen_nodes.add(a)
        if len(seen_nodes) < max_nodes:
            seen_nodes.add(b)
    lines = []
    for pred in sorted(by_pred.keys()):
        lines.append(f"[{pred}]")
        for a, b in by_pred[pred]:
            if a in seen_nodes and b in seen_nodes:
                lines.append(f"  {a} --{pred}--> {b}")
        lines.append("")
    if not lines:
        return "<no relationships>"
    return "\n".join(lines).rstrip()
END_CODE
'''

PROMPT_CL = r'''Gib NUR Python-Code zwischen BEGIN_CODE und END_CODE aus.
Implementiere: def analyze_kb(db_path: str, sample: int = 100) -> dict
- Öffne SQLite-DB und lese bis zu sample Fakten aus Tabelle facts(statement TEXT).
- Ermittle count, unique_predicates, top_entities (einfaches Zählen), sample_facts.
- Keine externen Pakete außer sqlite3. Keine Prints.
BEGIN_CODE
# Claude contribution
import sqlite3
def analyze_kb(db_path: str, sample: int = 100) -> dict:
    out = {"count": 0, "unique_predicates": [], "top_entities": [], "sample_facts": []}
    try:
        conn = sqlite3.connect(db_path)
        cur = conn.execute("SELECT COUNT(*) FROM facts")
        out["count"] = int(cur.fetchone()[0])
        cur = conn.execute("SELECT statement FROM facts LIMIT ?", (int(sample),))
        facts = [row[0] for row in cur]
        out["sample_facts"] = facts
        preds = {}
        ents = {}
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
END_CODE
'''

async def call_delegate(vendor: str, task: str):
    server = HAKGALMCPServer()
    responses = []
    async def capture(resp):
        responses.append(resp)
    server.send_response = capture
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({
        "id": 2,
        "params": {
            "name": "delegate_task",
            "arguments": {"target_agent": vendor, "task_description": task, "context": {}}
        }
    })
    for resp in responses:
        if resp.get("id") == 2:
            items = resp.get("result", {}).get("content", [])
            for it in items:
                if it.get("type") == "text":
                    return it.get("text")
    return ""

async def main():
    ds_code = await call_delegate("DeepSeek:chat", PROMPT_DS)
    gm_code = await call_delegate("Gemini:2.5-flash", PROMPT_GM)
    cl_code = await call_delegate("Claude:sonnet", PROMPT_CL)

    def extract_between(text: str):
        m = re.search(r"BEGIN_CODE\n([\s\S]*?)\nEND_CODE", text)
        return m.group(1).strip() if m else text.strip()

    ds_fn = extract_between(ds_code)
    gm_fn = extract_between(gm_code)
    cl_fn = extract_between(cl_code)

    header = """
# HAK_GAL 4-LLM Kollaborations-Tool
# Beiträge:
# - DeepSeek: extract_relationships
# - Gemini: visualize_as_ascii
# - Claude: analyze_kb
# - Orchestrator/CLI: Assistant
""".strip()

    footer = r"""

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
"""

    target = Path("..") / "collab_kb_tool.py"
    content = (header + "\n\n" + ds_fn + "\n\n" + gm_fn + "\n\n" + cl_fn + footer)
    target.write_text(content, encoding="utf-8")
    print(f"Wrote {target}")

asyncio.run(main())
