import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def call(name, args=None, req_id=2):
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_tool_call({"id":req_id, "params":{"name":name, "arguments":(args or {})}})
    for r in out:
        if r.get("id")==req_id:
            items=(r.get("result") or {}).get("content") or []
            for it in items:
                if it.get("type")=="text":
                    return it.get("text")
    return ""

async def main():
    print("[sentry_test_connection]\n" + (await call('sentry_test_connection', {}, 50)))

asyncio.run(main())
