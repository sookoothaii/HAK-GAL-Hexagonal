import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

FACTS = [
  "ToolCount(HAKGAL_Instance, 66).",
  "FactCount(HAKGAL_Instance, 6505).",
  "NicheCount(HAKGAL_Instance, 9).",
  "NicheFactsTotal(HAKGAL_Instance, 3649).",
  "SentryConnected(SamuiScienceLab, True).",
  "SentryProject(HAKGAL, hak_gal_backend)."
]

async def add_fact(server, stmt):
    out=[]
    async def cap(r): out.append(r)
    server.send_response=cap
    await server.handle_tool_call({"id": 2, "params": {"name": "add_fact", "arguments": {"statement": stmt}}})

async def main():
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    for st in FACTS:
        await add_fact(s, st)
    print("OK: inserted", len(FACTS))

asyncio.run(main())
