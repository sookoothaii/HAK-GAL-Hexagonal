import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def main():
    server = HAKGALMCPServer()
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    args = {"target_agent": "Gemini:2.5-flash", "task_description": "Gib eine 8-Punkte-Liste kurzer, umsetzbarer HAK_GAL-Verbesserungen (ASCII, ohne JSON).", "context": {"ssot_mode": True}}
    await server.handle_tool_call({"id": 2, "params": {"name": "delegate_task", "arguments": args}})
    for r in out:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    print(it.get("text"))

asyncio.run(main())
