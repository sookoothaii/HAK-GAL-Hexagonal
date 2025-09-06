import asyncio, re, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

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

async def main():
    server = HAKGALMCPServer()
    responses = []
    async def capture(resp):
        responses.append(resp)
    server.send_response = capture
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({"id":2, "params": {"name":"delegate_task", "arguments": {"target_agent":"Gemini:2.0-flash-exp", "task_description": PROMPT_GM, "context":{}}}})
    text = None
    for r in responses:
        if r.get("id") == 2:
            items = r.get("result",{}).get("content",[])
            for it in items:
                if it.get("type")=="text":
                    text = it.get("text")
                    break
    code = text or ""
    m = re.search(r"BEGIN_CODE\n([\s\S]*?)\nEND_CODE", code)
    out = m.group(1) if m else code
    print(out)

asyncio.run(main())
