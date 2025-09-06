import asyncio, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from ultimate_mcp.hakgal_mcp_ultimate import HAKGALMCPServer

async def list_tools():
    s=HAKGALMCPServer(); out=[]
    async def cap(r): out.append(r)
    s.send_response=cap
    await s.handle_initialize({"id":1})
    await s.handle_list_tools({"id":2})
    names=[]
    for r in out:
        if r.get("id")==2:
            names=[t.get('name') for t in (r.get('result') or {}).get('tools', [])]
    return names

async def call(name, args=None, req_id=10):
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
    names = await list_tools()
    print("Total tools:", len(names))
    for n in ("niche_list","niche_stats","niche_query"):
        print(n, n in names)
    if "niche_list" in names:
        print("\n[niche_list]\n", await call("niche_list", {}, 20))
    if "niche_stats" in names:
        print("\n[niche_stats]\n", await call("niche_stats", {}, 21))
    if "niche_query" in names:
        print("\n[niche_query]\n", await call("niche_query", {"name":"hakgal_core","q":"hakgal","limit":3}, 22))

asyncio.run(main())
