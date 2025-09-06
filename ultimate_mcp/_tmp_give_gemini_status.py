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
    await s.handle_tool_call({"id":3,"params":{"name":"health_check_json","arguments":{}}})
    status_text=""; health_text=""
    for r in out:
        if r.get("id")==2:
            status_text=(r.get("result") or {}).get("content")[0].get("text")
        if r.get("id")==3:
            health_text=(r.get("result") or {}).get("content")[0].get("text")
    print("=== get_system_status ===\n"+status_text)
    print("\n=== health_check_json ===\n"+health_text)
asyncio.run(main())
