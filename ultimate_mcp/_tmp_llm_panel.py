import asyncio, json, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

PROMPT = {
  "brief": "Analysiere das HAK_GAL System streng nach Verfassung (Artikel 2-7). Gib konkrete, umsetzbare Verbesserungen (Architektur, Tools, Qualit?t, Sicherheit, Observability, Performance).",
  "constraints": [
    "SSoT-first, niche-second; niemals Widerspr?che erzeugen",
    "ASCII-only Antworten, pr?zise, ohne Marketing",
    "Belege Empfehlungen mit knappen Gr?nden",
    "Schlage safe, inkrementelle Schritte vor (no risky ops)",
  ],
}

async def delegate(agent: str, task: str):
    server = HAKGALMCPServer()
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    args = {"target_agent": agent, "task_description": task, "context": {"ssot_mode": True}}
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})
    for r in out:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    return it.get("text")
    return ""

async def main():
    task = f"{PROMPT['brief']}\n\nConstraints:\n- " + "\n- ".join(PROMPT['constraints'])
    panel = {}
    for agent in ("DeepSeek:chat", "Gemini:2.5-flash", "Claude:sonnet"):
        try:
            panel[agent] = await delegate(agent, task)
        except Exception as e:
            panel[agent] = f"ERROR: {e}"
    Path('..\\reports\\llm_panel_raw.json').write_text(json.dumps(panel, ensure_ascii=False, indent=2), encoding='utf-8')
    print('LLM panel collected')

asyncio.run(main())
