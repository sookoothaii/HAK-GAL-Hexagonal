import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def call(tool, args=None):
    server = HAKGALMCPServer()
    out = []
    async def cap(resp): out.append(resp)
    server.send_response = cap
    await server.handle_initialize({"id": 1})
    await server.handle_tool_call({"id": 2, "params": {"name": tool, "arguments": (args or {})}})
    for r in out:
        if r.get("id") == 2:
            items = (r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type") == "text":
                    print(it.get("text"))

async def main():
    print('[HEALTH-PLAIN]'); await call('health_check')
    print('\n[HEALTH-JSON]'); await call('health_check_json')

asyncio.run(main())
