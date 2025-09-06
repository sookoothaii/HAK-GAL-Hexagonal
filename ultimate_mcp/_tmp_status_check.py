import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def main():
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_tool_call({"id":2,"params":{"name":"get_system_status","arguments":{}}})
    for r in out:
        if r.get("id")==2:
            print((r.get("result") or {}).get("content")[0].get("text"))
asyncio.run(main())
