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
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_list_tools({"id":2})
    tools=[]
    for r in out:
        if r.get("id")==2:
            tools=[t.get('name') for t in (r.get('result') or {}).get('tools', [])]
    print("HAS niche_list:", 'niche_list' in tools)
    print("HAS niche_stats:", 'niche_stats' in tools)
    print("HAS niche_query:", 'niche_query' in tools)
    if 'niche_list' in tools:
        print("\n[niche_list]\n", await call('niche_list', {}, 10))
    if 'niche_stats' in tools:
        print("\n[niche_stats]\n", await call('niche_stats', {}, 11))
    if 'niche_query' in tools:
        print("\n[niche_query]\n", await call('niche_query', {"name":"architecture","q":"hexagonal","limit":3}, 12))

asyncio.run(main())
